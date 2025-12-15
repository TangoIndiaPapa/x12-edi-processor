"""Custom exceptions for X12 EDI processing.

Provides a hierarchy of exception classes for different failure scenarios
in X12 document processing. All exceptions inherit from X12ProcessingError
for easy catching of all X12-related errors.

Callers:
    - src.parsers.*: Raises X12ParseError, X12ValidationError
    - src.input.*: Raises InputError, FileSizeError, S3Error
    - src.handlers.lambda_handler: Catches X12ProcessingError

Exception Hierarchy:
    X12ProcessingError (base)
    ├── X12ParseError: Document parsing failures
    ├── X12ValidationError: Validation failures
    ├── InputError: Generic input source errors
    ├── OutputError: Output destination errors
    ├── ConfigurationError: Configuration problems
    ├── FileSizeError: File size limit exceeded
    └── S3Error: AWS S3 operation failures

Example:
    try:
        parser.parse(x12_content)
    except X12ParseError as e:
        logger.error(f"Parsing failed: {e}")
    except X12ProcessingError as e:
        logger.error(f"General error: {e}")
"""


class X12ProcessingError(Exception):
    """Base exception for X12 processing errors.

    All X12-specific exceptions inherit from this class, allowing callers
    to catch all X12-related errors with a single except clause.

    Raised by:
        - Not raised directly, used as base class

    Caught by:
        - src.handlers.lambda_handler: For general error handling
    """

    pass


class X12ParseError(X12ProcessingError):
    """Exception raised when parsing X12 data fails.

    Indicates that the X12 document structure is invalid, cannot be parsed,
    or doesn't conform to expected format.

    Raised by:
        - src.parsers.x12_277_parser.X12_277_Parser.parse()
        - src.parsers.x12_835_parser.X12_835_Parser.parse()

    Example:
        raise X12ParseError("Failed to parse 277 document: Invalid ST segment")
    """

    pass


class X12ValidationError(X12ProcessingError):
    """Exception raised when X12 validation fails.

    Indicates that the X12 document parsed successfully but contains
    validation errors (missing required fields, invalid values, etc.).

    Raised by:
        - Parser validate() methods when STRICT_MODE is enabled

    Example:
        raise X12ValidationError("Missing required payer information")
    """

    pass


class InputError(X12ProcessingError):
    """Exception raised for input source errors.

    Generic input error for problems reading from any input source.

    Raised by:
        - src.input.local_input.LocalInput: File not found, not readable
        - src.input.upload_input.UploadInput: Empty content, decode errors
        - src.input.base_input.BaseInput: Generic read failures

    Example:
        raise InputError(f"File not found: {file_path}")
    """

    pass


class OutputError(X12ProcessingError):
    """Exception raised for output destination errors.

    Indicates problems writing processed results to output destination.

    Raised by:
        - Output handler implementations (when implemented)

    Example:
        raise OutputError(f"Failed to write to S3: {error}")
    """

    pass


class ConfigurationError(X12ProcessingError):
    """Exception raised for configuration errors.

    Indicates invalid or missing configuration settings.

    Raised by:
        - Modules detecting invalid configuration state

    Example:
        raise ConfigurationError("AWS_REGION not configured")
    """

    pass


class FileSizeError(X12ProcessingError):
    """Exception raised when file size exceeds limits.

    Raised when input file/content size exceeds MAX_FILE_SIZE_MB setting.

    Raised by:
        - src.input.local_input.LocalInput.validate_source()
        - src.input.s3_input.S3Input.validate_source()
        - src.input.upload_input.UploadInput.validate_source()

    Example:
        raise FileSizeError(
            f"File size ({size} bytes) exceeds maximum ({max_size} bytes)"
        )
    """

    pass


class S3Error(X12ProcessingError):
    """Exception raised for S3 operations errors.

    Wraps AWS S3 ClientError exceptions with application-specific context.

    Raised by:
        - src.input.s3_input.S3Input.validate_source()
        - src.input.s3_input.S3Input.read()
        - src.input.s3_input.S3Input.copy_to_local()

    Common scenarios:
        - Object not found (404)
        - Access denied (403)
        - Network/connectivity issues

    Example:
        raise S3Error(f"S3 object not found: s3://{bucket}/{key}")
    """

    pass
