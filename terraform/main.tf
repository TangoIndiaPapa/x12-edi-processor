# ============================================================================
# X12 EDI Processor - AWS Infrastructure
# ============================================================================
# This Terraform configuration deploys the X12 EDI processing platform to AWS
# including Lambda functions, S3 buckets, IAM roles, and CloudWatch monitoring.
#
# Resources Created:
#   - Lambda function for X12 processing
#   - S3 bucket for input/output files
#   - IAM roles and policies
#   - CloudWatch Log Groups
#   - S3 event notifications
# ============================================================================

terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.4"
    }
  }
}

# ============================================================================
# Provider Configuration
# ============================================================================
provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "X12-EDI-Processor"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# ============================================================================
# Data Sources
# ============================================================================

# Get current AWS account ID
data "aws_caller_identity" "current" {}

# Get current AWS region
data "aws_region" "current" {}

# ============================================================================
# S3 Bucket for X12 Files
# ============================================================================

# Main S3 bucket for storing input and processed X12 files
resource "aws_s3_bucket" "x12_files" {
  bucket = "${var.project_name}-${var.environment}-${data.aws_caller_identity.current.account_id}"

  tags = {
    Name        = "X12 EDI Files"
    Description = "Storage for X12 input and processed files"
  }
}

# Enable versioning to prevent accidental deletions
resource "aws_s3_bucket_versioning" "x12_files" {
  bucket = aws_s3_bucket.x12_files.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Server-side encryption for data at rest
resource "aws_s3_bucket_server_side_encryption_configuration" "x12_files" {
  bucket = aws_s3_bucket.x12_files.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Block public access to the bucket
resource "aws_s3_bucket_public_access_block" "x12_files" {
  bucket = aws_s3_bucket.x12_files.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Lifecycle policy to manage storage costs
resource "aws_s3_bucket_lifecycle_configuration" "x12_files" {
  bucket = aws_s3_bucket.x12_files.id

  rule {
    id     = "archive-old-files"
    status = "Enabled"

    # Move files to cheaper storage after 90 days
    transition {
      days          = 90
      storage_class = "GLACIER"
    }

    # Delete files after retention period
    expiration {
      days = var.file_retention_days
    }
  }

  rule {
    id     = "delete-old-versions"
    status = "Enabled"

    noncurrent_version_expiration {
      noncurrent_days = 30
    }
  }
}

# ============================================================================
# CloudWatch Log Group
# ============================================================================

# Log group for Lambda function logs
resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/${var.lambda_function_name}"
  retention_in_days = var.log_retention_days

  tags = {
    Name = "X12 Processor Lambda Logs"
  }
}

# ============================================================================
# IAM Role for Lambda
# ============================================================================

# Trust policy allowing Lambda to assume this role
data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

# Create IAM role for Lambda function
resource "aws_iam_role" "lambda_role" {
  name               = "${var.project_name}-lambda-role-${var.environment}"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json

  tags = {
    Name = "X12 Processor Lambda Role"
  }
}

# Policy document for Lambda permissions
data "aws_iam_policy_document" "lambda_policy" {
  # CloudWatch Logs permissions
  statement {
    sid    = "CloudWatchLogs"
    effect = "Allow"

    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]

    resources = [
      "${aws_cloudwatch_log_group.lambda_logs.arn}:*"
    ]
  }

  # S3 read permissions for input files
  statement {
    sid    = "S3ReadAccess"
    effect = "Allow"

    actions = [
      "s3:GetObject",
      "s3:GetObjectVersion",
      "s3:ListBucket"
    ]

    resources = [
      aws_s3_bucket.x12_files.arn,
      "${aws_s3_bucket.x12_files.arn}/*"
    ]
  }

  # S3 write permissions for processed files
  statement {
    sid    = "S3WriteAccess"
    effect = "Allow"

    actions = [
      "s3:PutObject",
      "s3:PutObjectAcl"
    ]

    resources = [
      "${aws_s3_bucket.x12_files.arn}/output/*",
      "${aws_s3_bucket.x12_files.arn}/processed/*",
      "${aws_s3_bucket.x12_files.arn}/errors/*"
    ]
  }

  # X-Ray tracing permissions
  statement {
    sid    = "XRayAccess"
    effect = "Allow"

    actions = [
      "xray:PutTraceSegments",
      "xray:PutTelemetryRecords"
    ]

    resources = ["*"]
  }
}

# Attach custom policy to Lambda role
resource "aws_iam_role_policy" "lambda_policy" {
  name   = "${var.project_name}-lambda-policy-${var.environment}"
  role   = aws_iam_role.lambda_role.id
  policy = data.aws_iam_policy_document.lambda_policy.json
}

# Attach AWS managed policy for VPC access (if needed)
resource "aws_iam_role_policy_attachment" "lambda_vpc_execution" {
  count      = var.enable_vpc ? 1 : 0
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

# ============================================================================
# Lambda Function Package
# ============================================================================

# Create deployment package with dependencies
data "archive_file" "lambda_package" {
  type        = "zip"
  source_dir  = "${path.module}/../"
  output_path = "${path.module}/lambda_function.zip"

  excludes = [
    ".git",
    ".github",
    ".pytest_cache",
    "__pycache__",
    "*.pyc",
    "htmlcov",
    "venv",
    "venv312",
    "tests",
    "test_*.py",
    "terraform",
    ".env",
    ".coverage",
    "*.md"
  ]
}

# ============================================================================
# Lambda Function
# ============================================================================

# Main Lambda function for X12 processing
resource "aws_lambda_function" "x12_processor" {
  filename         = data.archive_file.lambda_package.output_path
  function_name    = var.lambda_function_name
  role             = aws_iam_role.lambda_role.arn
  handler          = "src.handlers.lambda_handler.lambda_handler"
  source_code_hash = data.archive_file.lambda_package.output_base64sha256
  runtime          = var.lambda_runtime
  timeout          = var.lambda_timeout
  memory_size      = var.lambda_memory_size

  # Environment variables for the Lambda function
  environment {
    variables = {
      ENVIRONMENT             = "development"
      AWS_S3_BUCKET           = aws_s3_bucket.x12_files.id
      LOG_LEVEL               = var.log_level
      MAX_FILE_SIZE_MB        = var.max_file_size_mb
      ENABLE_VALIDATION       = var.enable_validation
      STRICT_MODE             = var.strict_mode
      POWERTOOLS_SERVICE_NAME = "x12-edi-processor"
    }
  }

  # Enable X-Ray tracing for performance monitoring
  tracing_config {
    mode = var.enable_xray_tracing ? "Active" : "PassThrough"
  }

  # Reserved concurrent executions (0 = no limit)
  reserved_concurrent_executions = var.lambda_reserved_concurrency

  # Dead Letter Queue for failed invocations
  dynamic "dead_letter_config" {
    for_each = var.enable_dlq ? [1] : []
    content {
      target_arn = aws_sqs_queue.dlq[0].arn
    }
  }

  depends_on = [
    aws_cloudwatch_log_group.lambda_logs,
    aws_iam_role_policy.lambda_policy
  ]

  tags = {
    Name = "X12 EDI Processor"
  }
}

# Lambda function alias for versioning
resource "aws_lambda_alias" "x12_processor_live" {
  name             = "live"
  function_name    = aws_lambda_function.x12_processor.function_name
  function_version = "$LATEST"

  description = "Live version of X12 processor"
}

# ============================================================================
# S3 Event Notifications
# ============================================================================

# Allow S3 to invoke Lambda function
resource "aws_lambda_permission" "allow_s3" {
  statement_id  = "AllowExecutionFromS3Bucket"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.x12_processor.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.x12_files.arn
}

# S3 bucket notification to trigger Lambda on file upload
resource "aws_s3_bucket_notification" "x12_file_upload" {
  bucket = aws_s3_bucket.x12_files.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.x12_processor.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "input/"
    filter_suffix       = ".x12"
  }

  depends_on = [aws_lambda_permission.allow_s3]
}

# ============================================================================
# Dead Letter Queue (Optional)
# ============================================================================

# SQS queue for failed Lambda invocations
resource "aws_sqs_queue" "dlq" {
  count = var.enable_dlq ? 1 : 0

  name                      = "${var.project_name}-dlq-${var.environment}"
  message_retention_seconds = 1209600 # 14 days

  tags = {
    Name = "X12 Processor DLQ"
  }
}

# Allow Lambda to send messages to DLQ
resource "aws_iam_role_policy" "lambda_dlq" {
  count = var.enable_dlq ? 1 : 0

  name = "${var.project_name}-lambda-dlq-policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "sqs:SendMessage"
        ]
        Resource = aws_sqs_queue.dlq[0].arn
      }
    ]
  })
}

# ============================================================================
# CloudWatch Alarms
# ============================================================================

# Alarm for Lambda errors
resource "aws_cloudwatch_metric_alarm" "lambda_errors" {
  alarm_name          = "${var.lambda_function_name}-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = 300
  statistic           = "Sum"
  threshold           = 5
  alarm_description   = "This metric monitors Lambda function errors"
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = aws_lambda_function.x12_processor.function_name
  }

  tags = {
    Name = "X12 Processor Error Alarm"
  }
}

# Alarm for Lambda duration (timeout warning)
resource "aws_cloudwatch_metric_alarm" "lambda_duration" {
  alarm_name          = "${var.lambda_function_name}-duration"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "Duration"
  namespace           = "AWS/Lambda"
  period              = 300
  statistic           = "Average"
  threshold           = var.lambda_timeout * 1000 * 0.8 # 80% of timeout
  alarm_description   = "This metric monitors Lambda execution time"
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = aws_lambda_function.x12_processor.function_name
  }

  tags = {
    Name = "X12 Processor Duration Alarm"
  }
}

# ============================================================================
# Lambda Layer for Dependencies (Optional - for large dependencies)
# ============================================================================

# Uncomment this section if you want to use Lambda Layers for Python dependencies
# This can reduce deployment package size and improve cold start times

# resource "aws_lambda_layer_version" "python_dependencies" {
#   filename            = "${path.module}/lambda_layer.zip"
#   layer_name          = "${var.project_name}-dependencies"
#   compatible_runtimes = [var.lambda_runtime]
#   description         = "Python dependencies for X12 EDI processor"
# 
#   # Build layer with: 
#   # mkdir -p python/lib/python3.12/site-packages
#   # pip install -r requirements.txt -t python/lib/python3.12/site-packages/
#   # zip -r lambda_layer.zip python/
# }
