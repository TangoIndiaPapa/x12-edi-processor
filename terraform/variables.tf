# ============================================================================
# Terraform Variables for X12 EDI Processor
# ============================================================================
# Define all input variables for the infrastructure deployment.
# Override these values in terraform.tfvars or via command line.
# ============================================================================

# ============================================================================
# General Configuration
# ============================================================================

variable "project_name" {
  description = "Project name used for resource naming and tagging"
  type        = string
  default     = "x12-edi-processor"
}

variable "environment" {
  description = "Environment name (dev, staging, production)"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "production"], var.environment)
    error_message = "Environment must be dev, staging, or production."
  }
}

variable "aws_region" {
  description = "AWS region for resource deployment"
  type        = string
  default     = "us-east-1"
}

# ============================================================================
# Lambda Function Configuration
# ============================================================================

variable "lambda_function_name" {
  description = "Name of the Lambda function"
  type        = string
  default     = "x12-edi-processor"
}

variable "lambda_runtime" {
  description = "Lambda runtime version (Python)"
  type        = string
  default     = "python3.12"

  validation {
    condition     = can(regex("^python3\\.(9|10|11|12)$", var.lambda_runtime))
    error_message = "Lambda runtime must be python3.9, python3.10, python3.11, or python3.12."
  }
}

variable "lambda_timeout" {
  description = "Lambda function timeout in seconds (max 900)"
  type        = number
  default     = 300

  validation {
    condition     = var.lambda_timeout >= 3 && var.lambda_timeout <= 900
    error_message = "Lambda timeout must be between 3 and 900 seconds."
  }
}

variable "lambda_memory_size" {
  description = "Lambda function memory size in MB (128-10240)"
  type        = number
  default     = 512

  validation {
    condition     = var.lambda_memory_size >= 128 && var.lambda_memory_size <= 10240
    error_message = "Lambda memory size must be between 128 and 10240 MB."
  }
}

variable "lambda_reserved_concurrency" {
  description = "Reserved concurrent executions for Lambda (0 = unreserved, -1 = no concurrent executions)"
  type        = number
  default     = -1
}

# ============================================================================
# Application Configuration
# ============================================================================

variable "log_level" {
  description = "Application log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
  type        = string
  default     = "INFO"

  validation {
    condition     = contains(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], var.log_level)
    error_message = "Log level must be DEBUG, INFO, WARNING, ERROR, or CRITICAL."
  }
}

variable "max_file_size_mb" {
  description = "Maximum X12 file size in megabytes"
  type        = number
  default     = 50

  validation {
    condition     = var.max_file_size_mb > 0 && var.max_file_size_mb <= 250
    error_message = "Max file size must be between 1 and 250 MB."
  }
}

variable "enable_validation" {
  description = "Enable X12 document validation"
  type        = bool
  default     = true
}

variable "strict_mode" {
  description = "Fail processing on validation errors"
  type        = bool
  default     = false
}

# ============================================================================
# Storage Configuration
# ============================================================================

variable "file_retention_days" {
  description = "Number of days to retain files in S3 before deletion"
  type        = number
  default     = 365

  validation {
    condition     = var.file_retention_days >= 1
    error_message = "File retention must be at least 1 day."
  }
}

# ============================================================================
# Monitoring Configuration
# ============================================================================

variable "log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number
  default     = 30

  validation {
    condition     = contains([1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, 3653], var.log_retention_days)
    error_message = "Log retention days must be a valid CloudWatch retention period."
  }
}

variable "enable_xray_tracing" {
  description = "Enable AWS X-Ray tracing for Lambda"
  type        = bool
  default     = true
}

# ============================================================================
# Reliability Configuration
# ============================================================================

variable "enable_dlq" {
  description = "Enable Dead Letter Queue for failed Lambda invocations"
  type        = bool
  default     = true
}

# ============================================================================
# Network Configuration
# ============================================================================

variable "enable_vpc" {
  description = "Deploy Lambda in VPC (requires VPC configuration)"
  type        = bool
  default     = false
}

variable "vpc_id" {
  description = "VPC ID for Lambda deployment (required if enable_vpc = true)"
  type        = string
  default     = ""
}

variable "subnet_ids" {
  description = "List of subnet IDs for Lambda deployment (required if enable_vpc = true)"
  type        = list(string)
  default     = []
}

variable "security_group_ids" {
  description = "List of security group IDs for Lambda (required if enable_vpc = true)"
  type        = list(string)
  default     = []
}

# ============================================================================
# Tagging Configuration
# ============================================================================

variable "additional_tags" {
  description = "Additional tags to apply to all resources"
  type        = map(string)
  default     = {}
}
