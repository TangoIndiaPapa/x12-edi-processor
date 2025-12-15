"""AWS Lambda handler for processing X12 EDI documents."""

# Standard library imports
import json
from datetime import datetime
from typing import Any, Dict, Optional

# Third-party imports
import boto3
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext

# Application imports - using absolute imports for enterprise standards
# Absolute imports are preferred over relative imports (PEP 8) for:
# - Better code clarity and maintainability
# - Explicit dependency declaration
# - Improved IDE support and static analysis
# - Easier refactoring and module relocation
from src.core.config import get_settings
from src.core.exceptions import X12ProcessingError
from src.input.local_input import LocalInput
from src.input.s3_input import S3Input
from src.parsers.x12_277_parser import X12_277_Parser
from src.parsers.x12_835_parser import X12_835_Parser

# Initialize module-level instances
logger = Logger()
tracer = Tracer()
settings = get_settings()


@logger.inject_lambda_context
@tracer.capture_lambda_handler
def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    """
    AWS Lambda handler for X12 EDI processing.
    
    Event structure:
    {
        "input_source": "s3" | "local",
        "bucket": "bucket-name",  # For S3 source
        "key": "path/to/file",    # For S3 source
        "file_path": "/path",     # For local source
        "transaction_type": "277" | "835",
        "output_destination": "s3" | "local",
        "output_bucket": "bucket", # For S3 output
        "output_prefix": "prefix/", # For S3 output
        "output_path": "/path"     # For local output
    }
    
    Args:
        event: Lambda event dict
        context: Lambda context
        
    Returns:
        Response dict with processing results
    """
    try:
        logger.info("Processing X12 EDI document", extra={"event": event})
        
        # Check if this is an S3 event trigger (vs direct invocation)
        # S3 events have a "Records" array with S3 object metadata
        if "Records" in event and event["Records"]:
            # Extract S3 bucket and key from the S3 event structure
            # This happens when files are uploaded to S3 input/ directory
            s3_record = event["Records"][0]["s3"]
            event["bucket"] = s3_record["bucket"]["name"]
            event["key"] = s3_record["object"]["key"]
            event["input_source"] = "s3"
            logger.info(f"S3 event detected: {event['bucket']}/{event['key']}")
        
        # Extract processing parameters from event
        input_source = event.get("input_source", "s3")  # Default to S3 in Lambda
        transaction_type = event.get("transaction_type", "auto")  # Auto-detect if not specified
        
        # Read X12 content from source (S3 or local file system)
        x12_content = _read_input(event, input_source)
        
        # Log content preview for debugging (helps identify line ending issues)
        logger.info(f"Read X12 content ({len(x12_content)} bytes). First 200 chars: {x12_content[:200]}")
        
        # Auto-detect transaction type from ST segment if not provided
        if transaction_type == "auto":
            transaction_type = _detect_transaction_type(x12_content)
            logger.info(f"Auto-detected transaction type: {transaction_type}")
        
        # Get appropriate parser and parse the X12 document
        parser = _get_parser(transaction_type)
        parsed_data = parser.parse(x12_content)
        
        # Validate parsed data if validation is enabled in settings
        if settings.ENABLE_VALIDATION:
            validation_errors = parser.validate(parsed_data)
            
            # In strict mode, fail the request if validation errors exist
            if validation_errors and settings.STRICT_MODE:
                return {
                    "statusCode": 400,
                    "body": json.dumps({
                        "error": "Validation failed",
                        "validation_errors": validation_errors
                    })
                }
            
            # Include validation errors in output for non-strict mode
            parsed_data["validation_errors"] = validation_errors
        
        # Write parsed data to output destination (S3, local, or in-memory)
        output_location = _write_output(event, parsed_data)
        
        # Log successful processing with key metadata
        logger.info("Successfully processed X12 document", extra={
            "transaction_type": transaction_type,
            "output_location": output_location
        })
        
        # Return success response with summary (not full parsed data)
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Successfully processed X12 document",
                "transaction_type": transaction_type,
                "output_location": output_location,
                "summary": _create_summary(parsed_data)  # Lightweight summary for response
            })
        }
        
    except X12ProcessingError as e:
        logger.error(f"X12 processing error: {str(e)}", exc_info=True)
        return {
            "statusCode": 400,
            "body": json.dumps({
                "error": "X12 processing error",
                "message": str(e)
            })
        }
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": "Internal server error",
                "message": str(e)
            })
        }


def _read_input(event: Dict[str, Any], source: str) -> str:
    """
    Read X12 EDI content from the specified input source.
    
    Supports reading from S3 buckets or local file system. The appropriate
    input handler is instantiated based on the source type.
    
    Args:
        event: Lambda event containing source parameters (bucket, key, or file_path)
        source: Input source type - "s3" or "local"
        
    Returns:
        str: Raw X12 EDI content with normalized line endings
        
    Raises:
        ValueError: If required parameters are missing or source type is unsupported
    """
    if source == "s3":
        # Extract S3 location from event
        bucket = event.get("bucket")
        key = event.get("key")
        if not bucket or not key:
            raise ValueError("S3 source requires 'bucket' and 'key'")
        
        # Use S3Input handler which handles line ending normalization
        input_handler = S3Input(bucket=bucket, key=key)
        return input_handler.read()
    
    elif source == "local":
        # Extract file path from event
        file_path = event.get("file_path")
        if not file_path:
            raise ValueError("Local source requires 'file_path'")
        
        # Use LocalInput handler for file system access
        input_handler = LocalInput(file_path=file_path)
        return input_handler.read()
    
    else:
        raise ValueError(f"Unsupported input source: {source}")


def _detect_transaction_type(x12_content: str) -> str:
    """
    Auto-detect X12 transaction type from the ST (Transaction Set Header) segment.
    
    The ST segment is the first segment in each transaction set and contains
    the transaction set identifier code (e.g., 277 for Claim Status, 835 for Payment).
    Format: ST*{transaction_code}*{control_number}*{version}~
    
    Args:
        x12_content: Raw X12 EDI content
        
    Returns:
        str: Transaction type code (e.g., "277", "835") or "unknown" if not found
    """
    # Split on segment terminator (~) to process each segment
    lines = x12_content.split('~')
    
    # Find the ST segment which identifies the transaction type
    for line in lines:
        if line.strip().startswith('ST'):
            # Split on element separator (*) to extract transaction code
            elements = line.split('*')
            if len(elements) >= 2:
                # Second element (index 1) is the transaction set identifier
                return elements[1]
    
    return "unknown"


def _get_parser(transaction_type: str):
    """
    Factory function to instantiate the appropriate X12 parser based on transaction type.
    
    Supported transaction types:
    - 277: Health Care Claim Status Notification
    - 835: Health Care Claim Payment/Advice
    
    Args:
        transaction_type: X12 transaction set identifier (e.g., "277", "835")
        
    Returns:
        Parser instance for the specified transaction type
        
    Raises:
        ValueError: If transaction type is not supported
    """
    if transaction_type == "277":
        # Instantiate parser for claim status notifications
        return X12_277_Parser()
    elif transaction_type == "835":
        # Instantiate parser for payment/remittance advice
        return X12_835_Parser()
    else:
        raise ValueError(f"Unsupported transaction type: {transaction_type}")


def _write_output(event: Dict[str, Any], data: Dict[str, Any]) -> str:
    """
    Write parsed X12 data to the specified output destination.
    
    Supports writing to S3 buckets or local file system. For S3 output,
    generates a unique filename with timestamp to prevent overwrites.
    
    Args:
        event: Lambda event containing output parameters (bucket, prefix, path)
        data: Parsed X12 data to write (dict will be serialized to JSON)
        
    Returns:
        str: Output location (S3 URI, file path, or "in-memory")
        
    Note:
        Uses json.dumps with default=str to handle date/datetime objects
        that may be present in parsed X12 data.
    """
    # Determine output destination (default to S3 for Lambda environment)
    output_dest = event.get("output_destination", "s3")
    
    if output_dest == "s3":
        # Get S3 bucket and prefix from event or use defaults from config
        bucket = event.get("output_bucket", settings.AWS_S3_BUCKET)
        prefix = event.get("output_prefix", "output/")  # Default to output/ directory
        
        # Generate unique filename with UTC timestamp to prevent overwrites
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        transaction_type = data.get("transaction_type", "unknown")
        
        # Preserve original filename if available from S3 trigger event
        original_key = event.get("key", "")
        if original_key:
            # Extract filename without path and .x12 extension
            original_filename = original_key.split("/")[-1].replace(".x12", "")
            output_key = f"{prefix}{original_filename}_{timestamp}.json"
        else:
            # Fallback to transaction type if no original filename
            output_key = f"{prefix}{transaction_type}_{timestamp}.json"
        
        # Write JSON to S3 with proper content type
        s3_client = boto3.client("s3")
        s3_client.put_object(
            Bucket=bucket,
            Key=output_key,
            Body=json.dumps(data, indent=2, default=str),  # default=str handles date objects
            ContentType="application/json"
        )
        
        logger.info(f"Wrote output to s3://{bucket}/{output_key}")
        return f"s3://{bucket}/{output_key}"
    
    elif output_dest == "local":
        # Write to local file system (used for testing)
        output_path = event.get("output_path", "/tmp/result.json")
        with open(output_path, "w") as f:
            json.dumps(data, f, indent=2)
        return output_path
    
    # Return in-memory for other cases (no persistent storage)
    return "in-memory"


def _create_summary(parsed_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a concise summary of the parsed X12 data for API response.
    
    Extracts key metadata without including the full parsed data structure,
    making the Lambda response lightweight and informative.
    
    Args:
        parsed_data: Complete parsed X12 data dictionary
        
    Returns:
        dict: Summary containing transaction type, version, count, and validation status
    """
    # Get transaction list to count how many transactions were processed
    transactions = parsed_data.get("transactions", [])
    
    return {
        "transaction_type": parsed_data.get("transaction_type"),  # e.g., "277", "835"
        "version": parsed_data.get("version"),  # X12 version (e.g., "005010X212")
        "transaction_count": len(transactions),  # Number of transactions in the document
        "has_validation_errors": bool(parsed_data.get("validation_errors"))  # Quick validation check
    }
