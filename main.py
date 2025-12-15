"""X12 EDI Processing Application Entry Point.

This module serves as the local development entry point for testing the X12
EDI processing platform. In production, the lambda_handler is used instead.

Callers:
    - Direct execution: python main.py
    - Development testing and verification
    
Callees:
    - src.handlers.lambda_handler: Lambda processing function
    - src.core.config: Application configuration
    - logging: Standard library logging

Usage:
    # Run locally for testing
    python main.py
    
    # With custom environment
    ENVIRONMENT=production LOG_LEVEL=DEBUG python main.py
"""
from src.handlers.lambda_handler import lambda_handler
from src.core.config import get_settings
import logging

# Configure logging for local development
# Uses standard library logging instead of aws-lambda-powertools
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Local development entry point.
    
    Initializes the application and displays configuration information.
    Does not process files - use lambda_handler for actual processing.
    
    Called by:
        - Direct script execution (__main__)
        
    Logs:
        - Application startup message
        - Current environment setting
        - Ready status for transaction types
        
    Example:
        $ python main.py
        INFO - Starting X12 EDI Processor
        INFO - Environment: development
        INFO - Application ready for X12 277 and 835 processing
    """
    logger.info("Starting X12 EDI Processor")
    
    # Load and display configuration settings
    settings = get_settings()
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Application ready for X12 277 and 835 processing")


if __name__ == "__main__":
    # Entry point when script is executed directly
    main()
