# ============================================================================
# Terraform Outputs for X12 EDI Processor
# ============================================================================
# Export important resource information for use by other systems or teams.
# ============================================================================

# ============================================================================
# Lambda Function Outputs
# ============================================================================

output "lambda_function_name" {
  description = "Name of the Lambda function"
  value       = aws_lambda_function.x12_processor.function_name
}

output "lambda_function_arn" {
  description = "ARN of the Lambda function"
  value       = aws_lambda_function.x12_processor.arn
}

output "lambda_function_version" {
  description = "Latest published version of Lambda function"
  value       = aws_lambda_function.x12_processor.version
}

output "lambda_function_qualified_arn" {
  description = "Qualified ARN of the Lambda function"
  value       = aws_lambda_function.x12_processor.qualified_arn
}

output "lambda_role_arn" {
  description = "ARN of the Lambda execution role"
  value       = aws_iam_role.lambda_role.arn
}

output "lambda_role_name" {
  description = "Name of the Lambda execution role"
  value       = aws_iam_role.lambda_role.name
}

# ============================================================================
# S3 Bucket Outputs
# ============================================================================

output "s3_bucket_name" {
  description = "Name of the S3 bucket for X12 files"
  value       = aws_s3_bucket.x12_files.id
}

output "s3_bucket_arn" {
  description = "ARN of the S3 bucket"
  value       = aws_s3_bucket.x12_files.arn
}

output "s3_bucket_domain_name" {
  description = "Domain name of the S3 bucket"
  value       = aws_s3_bucket.x12_files.bucket_domain_name
}

output "s3_bucket_regional_domain_name" {
  description = "Regional domain name of the S3 bucket"
  value       = aws_s3_bucket.x12_files.bucket_regional_domain_name
}

# ============================================================================
# CloudWatch Outputs
# ============================================================================

output "cloudwatch_log_group_name" {
  description = "Name of the CloudWatch log group"
  value       = aws_cloudwatch_log_group.lambda_logs.name
}

output "cloudwatch_log_group_arn" {
  description = "ARN of the CloudWatch log group"
  value       = aws_cloudwatch_log_group.lambda_logs.arn
}

# ============================================================================
# Dead Letter Queue Outputs
# ============================================================================

output "dlq_url" {
  description = "URL of the Dead Letter Queue (if enabled)"
  value       = var.enable_dlq ? aws_sqs_queue.dlq[0].url : null
}

output "dlq_arn" {
  description = "ARN of the Dead Letter Queue (if enabled)"
  value       = var.enable_dlq ? aws_sqs_queue.dlq[0].arn : null
}

# ============================================================================
# Alarm Outputs
# ============================================================================

output "error_alarm_arn" {
  description = "ARN of the Lambda error alarm"
  value       = aws_cloudwatch_metric_alarm.lambda_errors.arn
}

output "duration_alarm_arn" {
  description = "ARN of the Lambda duration alarm"
  value       = aws_cloudwatch_metric_alarm.lambda_duration.arn
}

# ============================================================================
# Usage Instructions
# ============================================================================

output "usage_instructions" {
  description = "Instructions for using the deployed infrastructure"
  value       = <<-EOT
    
    ========================================
    X12 EDI Processor - Deployment Complete
    ========================================
    
    S3 Bucket: ${aws_s3_bucket.x12_files.id}
    Lambda Function: ${aws_lambda_function.x12_processor.function_name}
    Region: ${var.aws_region}
    Environment: ${var.environment}
    
    To process X12 files:
    1. Upload .x12 files to: s3://${aws_s3_bucket.x12_files.id}/input/
    2. Lambda will automatically process them
    3. Results will be saved to: s3://${aws_s3_bucket.x12_files.id}/processed/
    4. Errors will be saved to: s3://${aws_s3_bucket.x12_files.id}/errors/
    
    View logs:
    aws logs tail /aws/lambda/${aws_lambda_function.x12_processor.function_name} --follow
    
    Manual invocation:
    aws lambda invoke --function-name ${aws_lambda_function.x12_processor.function_name} \
      --payload '{"input_source":"s3","bucket":"${aws_s3_bucket.x12_files.id}","key":"input/sample.x12","transaction_type":"277"}' \
      response.json
    
    Monitor CloudWatch:
    https://console.aws.amazon.com/cloudwatch/home?region=${var.aws_region}#logsV2:log-groups/log-group/${replace(aws_cloudwatch_log_group.lambda_logs.name, "/", "$252F")}
    
    ========================================
  EOT
}

# ============================================================================
# Resource Summary
# ============================================================================

output "resource_summary" {
  description = "Summary of deployed resources"
  value = {
    lambda_function = aws_lambda_function.x12_processor.function_name
    s3_bucket       = aws_s3_bucket.x12_files.id
    log_group       = aws_cloudwatch_log_group.lambda_logs.name
    region          = var.aws_region
    environment     = var.environment
    xray_enabled    = var.enable_xray_tracing
    dlq_enabled     = var.enable_dlq
    vpc_enabled     = var.enable_vpc
  }
}
