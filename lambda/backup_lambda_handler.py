"""AWS Lambda handler for processing X12 EDI documents."""

import json
from typing import Any, Dict, Optional

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext

from ..core.config import get_settings
from ..core.exceptions import X12ProcessingError
from ..input.s3_input import S3Input
from ..input.local_input import LocalInput
from ..parsers.x12_277_parser import X12_277_Parser
from ..parsers.x12_835_parser import X12_835_Parser

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
        
        # Check if this is an S3 event
        if "Records" in event and event["Records"]:
            # This is an S3 trigger event
            s3_record = event["Records"][0]["s3"]
            event["bucket"] = s3_record["bucket"]["name"]
            event["key"] = s3_record["object"]["key"]
            event["input_source"] = "s3"
            logger.info(f"S3 event detected: {event['bucket']}/{event['key']}")
        
        # Extract parameters
        input_source = event.get("input_source", "s3")
        transaction_type = event.get("transaction_type", "auto")
        
        # Read input
        x12_content = _read_input(event, input_source)
        
        # Log the first 200 characters to verify content
        logger.info(f"Read X12 content ({len(x12_content)} bytes). First 200 chars: {x12_content[:200]}")
        
        # Auto-detect transaction type if needed
        if transaction_type == "auto":
            transaction_type = _detect_transaction_type(x12_content)
            logger.info(f"Auto-detected transaction type: {transaction_type}")
        
        # Parse document
        parser = _get_parser(transaction_type)
        parsed_data = parser.parse(x12_content)
        
        # Validate if enabled
        if settings.ENABLE_VALIDATION:
            validation_errors = parser.validate(parsed_data)
            if validation_errors and settings.STRICT_MODE:
                return {
                    "statusCode": 400,
                    "body": json.dumps({
                        "error": "Validation failed",
                        "validation_errors": validation_errors
                    })
                }
            parsed_data["validation_errors"] = validation_errors
        
        # Write output (implementation depends on output handler)
        output_location = _write_output(event, parsed_data)
        
        logger.info("Successfully processed X12 document", extra={
            "transaction_type": transaction_type,
            "output_location": output_location
        })
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Successfully processed X12 document",
                "transaction_type": transaction_type,
                "output_location": output_location,
                "summary": _create_summary(parsed_data)
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
    """Read input from specified source."""
    if source == "s3":
        bucket = event.get("bucket")
        key = event.get("key")
        if not bucket or not key:
            raise ValueError("S3 source requires 'bucket' and 'key'")
        
        input_handler = S3Input(bucket=bucket, key=key)
        return input_handler.read()
    
    elif source == "local":
        file_path = event.get("file_path")
        if not file_path:
            raise ValueError("Local source requires 'file_path'")
        
        input_handler = LocalInput(file_path=file_path)
        return input_handler.read()
    
    else:
        raise ValueError(f"Unsupported input source: {source}")


def _detect_transaction_type(x12_content: str) -> str:
    """Auto-detect X12 transaction type from ST segment."""
    lines = x12_content.split('~')
    for line in lines:
        if line.strip().startswith('ST'):
            elements = line.split('*')
            if len(elements) >= 2:
                return elements[1]
    return "unknown"


def _get_parser(transaction_type: str):
    """Get appropriate parser for transaction type."""
    if transaction_type == "277":
        return X12_277_Parser()
    elif transaction_type == "835":
        return X12_835_Parser()
    else:
        raise ValueError(f"Unsupported transaction type: {transaction_type}")


def _write_output(event: Dict[str, Any], data: Dict[str, Any]) -> str:
    """Write output to specified destination."""
    import boto3
    from datetime import datetime
    
    output_dest = event.get("output_destination", "s3")
    
    if output_dest == "s3":
        bucket = event.get("output_bucket", settings.AWS_S3_BUCKET)
        prefix = event.get("output_prefix", "output/")
        
        # Generate unique filename with timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        transaction_type = data.get("transaction_type", "unknown")
        
        # Extract original filename from event if available
        original_key = event.get("key", "")
        if original_key:
            original_filename = original_key.split("/")[-1].replace(".x12", "")
            output_key = f"{prefix}{original_filename}_{timestamp}.json"
        else:
            output_key = f"{prefix}{transaction_type}_{timestamp}.json"
        
        # Write to S3
        s3_client = boto3.client("s3")
        s3_client.put_object(
            Bucket=bucket,
            Key=output_key,
            Body=json.dumps(data, indent=2),
            ContentType="application/json"
        )
        
        logger.info(f"Wrote output to s3://{bucket}/{output_key}")
        return f"s3://{bucket}/{output_key}"
    
    elif output_dest == "local":
        output_path = event.get("output_path", "/tmp/result.json")
        with open(output_path, "w") as f:
            json.dumps(data, f, indent=2)
        return output_path
    
    return "in-memory"


def _create_summary(parsed_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create processing summary."""
    transactions = parsed_data.get("transactions", [])
    
    return {
        "transaction_type": parsed_data.get("transaction_type"),
        "version": parsed_data.get("version"),
        "transaction_count": len(transactions),
        "has_validation_errors": bool(parsed_data.get("validation_errors"))
    }
