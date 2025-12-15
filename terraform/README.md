# X12 EDI Processor - Terraform Infrastructure

Complete Terraform configuration for deploying the X12 EDI processor to AWS.

## Architecture

```
┌─────────────┐
│   S3 Bucket │
│  (X12 Files)│
└──────┬──────┘
       │ Upload .x12 file to /input/
       │
       ▼
┌─────────────────────┐
│  S3 Event Trigger   │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐       ┌──────────────┐
│  Lambda Function    │──────▶│  CloudWatch  │
│ (X12 Processor)     │       │     Logs     │
└──────┬──────────────┘       └──────────────┘
       │
       ├──▶ Success: s3://bucket/processed/
       └──▶ Error:   s3://bucket/errors/
```

## Resources Created

- **Lambda Function**: Processes X12 277 and 835 documents
- **S3 Bucket**: Stores input and processed files
- **IAM Role & Policies**: Permissions for Lambda execution
- **CloudWatch Log Group**: Function logs with configurable retention
- **S3 Event Notifications**: Triggers Lambda on file upload
- **CloudWatch Alarms**: Monitors errors and execution time
- **Dead Letter Queue** (optional): Captures failed invocations

## Prerequisites

1. **Terraform**: Version 1.0 or higher
   ```powershell
   C:\TF\terraform_1.14.2_windows_amd64\terraform.exe --version
   ```

2. **AWS CLI**: Configured with credentials
   ```powershell
   aws configure
   ```

3. **AWS Credentials**: Ensure you have appropriate permissions:
   - Lambda: Create/Update functions
   - S3: Create/Configure buckets
   - IAM: Create roles and policies
   - CloudWatch: Create log groups and alarms
   - SQS: Create queues (if DLQ enabled)

## Quick Start

### 1. Configure Variables

```powershell
# Navigate to terraform directory
cd C:\VSCode\x12-edi-processor\terraform

# Create your configuration file
Copy-Item terraform.tfvars.example terraform.tfvars

# Edit terraform.tfvars with your values
notepad terraform.tfvars
```

### 2. Initialize Terraform

```powershell
C:\TF\terraform_1.14.2_windows_amd64\terraform.exe init
```

### 3. Review Deployment Plan

```powershell
C:\TF\terraform_1.14.2_windows_amd64\terraform.exe plan
```

### 4. Deploy Infrastructure

```powershell
C:\TF\terraform_1.14.2_windows_amd64\terraform.exe apply
```

Type `yes` when prompted to confirm deployment.

### 5. View Outputs

```powershell
C:\TF\terraform_1.14.2_windows_amd64\terraform.exe output
```

## Configuration

### Essential Variables

Edit `terraform.tfvars`:

```hcl
# Environment
environment = "dev"        # dev, staging, or production
aws_region  = "us-east-1"

# Lambda Configuration
lambda_memory_size = 512   # MB (128-10240)
lambda_timeout     = 300   # seconds (3-900)

# Application Settings
log_level          = "INFO"
max_file_size_mb   = 50
enable_validation  = true
strict_mode        = false
```

### Environment-Specific Deployments

Create separate `.tfvars` files for each environment:

```powershell
# Development
C:\TF\terraform_1.14.2_windows_amd64\terraform.exe apply -var-file="dev.tfvars"

# Staging
C:\TF\terraform_1.14.2_windows_amd64\terraform.exe apply -var-file="staging.tfvars"

# Production
C:\TF\terraform_1.14.2_windows_amd64\terraform.exe apply -var-file="production.tfvars"
```

## Usage

### Upload Files for Processing

```powershell
# Get bucket name from Terraform output
$BUCKET = (C:\TF\terraform_1.14.2_windows_amd64\terraform.exe output -raw s3_bucket_name)

# Upload X12 file (triggers automatic processing)
aws s3 cp sample.x12 s3://$BUCKET/input/sample.x12
```

### Manual Lambda Invocation

```powershell
# Get function name
$FUNCTION = (C:\TF\terraform_1.14.2_windows_amd64\terraform.exe output -raw lambda_function_name)

# Invoke Lambda directly
aws lambda invoke `
  --function-name $FUNCTION `
  --payload '{"input_source":"s3","bucket":"'$BUCKET'","key":"input/sample.x12","transaction_type":"277"}' `
  response.json

# View response
Get-Content response.json | ConvertFrom-Json
```

### View Logs

```powershell
# Tail logs in real-time
$LOG_GROUP = (C:\TF\terraform_1.14.2_windows_amd64\terraform.exe output -raw cloudwatch_log_group_name)
aws logs tail $LOG_GROUP --follow

# View recent logs
aws logs tail $LOG_GROUP --since 1h
```

## Monitoring

### CloudWatch Alarms

Two alarms are automatically created:

1. **Error Alarm**: Triggers when more than 5 errors occur in 10 minutes
2. **Duration Alarm**: Triggers when execution time exceeds 80% of timeout

View alarms:
```powershell
aws cloudwatch describe-alarms --alarm-names `
  "x12-edi-processor-errors" `
  "x12-edi-processor-duration"
```

### Metrics

View Lambda metrics:
```powershell
aws cloudwatch get-metric-statistics `
  --namespace AWS/Lambda `
  --metric-name Invocations `
  --dimensions Name=FunctionName,Value=$FUNCTION `
  --start-time (Get-Date).AddHours(-1).ToString("yyyy-MM-ddTHH:mm:ss") `
  --end-time (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss") `
  --period 300 `
  --statistics Sum
```

## Cost Optimization

### Estimated Monthly Costs (us-east-1)

| Resource | Usage | Est. Cost |
|----------|-------|-----------|
| Lambda | 10,000 invocations/month @ 512MB, 30s avg | $0.20 |
| S3 Storage | 100GB stored | $2.30 |
| CloudWatch Logs | 10GB logs | $5.00 |
| Data Transfer | 50GB out | $4.50 |
| **Total** | | **~$12.00/month** |

### Cost Reduction Tips

1. **Adjust Lambda Memory**: Lower memory for smaller files
2. **Log Retention**: Reduce from 30 to 7 days
3. **S3 Lifecycle**: Enable Glacier transition for old files
4. **Reserved Capacity**: For predictable workloads

## Disaster Recovery

### Backup Strategy

The Terraform state is critical. Store it remotely:

```hcl
# Add to main.tf
terraform {
  backend "s3" {
    bucket = "your-terraform-state-bucket"
    key    = "x12-edi-processor/terraform.tfstate"
    region = "us-east-1"
  }
}
```

### Recovery Procedure

```powershell
# Re-initialize with remote state
C:\TF\terraform_1.14.2_windows_amd64\terraform.exe init

# Verify infrastructure
C:\TF\terraform_1.14.2_windows_amd64\terraform.exe plan

# Restore if needed
C:\TF\terraform_1.14.2_windows_amd64\terraform.exe apply
```

## Troubleshooting

### Common Issues

**Issue**: Lambda timeout errors
```powershell
# Solution: Increase timeout
# Edit terraform.tfvars
lambda_timeout = 600  # 10 minutes
C:\TF\terraform_1.14.2_windows_amd64\terraform.exe apply
```

**Issue**: Out of memory errors
```powershell
# Solution: Increase memory
lambda_memory_size = 1024
C:\TF\terraform_1.14.2_windows_amd64\terraform.exe apply
```

**Issue**: S3 permissions denied
```powershell
# Check IAM policy
aws iam get-role-policy `
  --role-name x12-edi-processor-lambda-role-dev `
  --policy-name x12-edi-processor-lambda-policy-dev
```

## Cleanup

### Destroy Infrastructure

```powershell
# WARNING: This deletes all resources including data in S3!

# Review what will be destroyed
C:\TF\terraform_1.14.2_windows_amd64\terraform.exe plan -destroy

# Destroy (requires confirmation)
C:\TF\terraform_1.14.2_windows_amd64\terraform.exe destroy
```

### Partial Cleanup

Remove specific resources:
```powershell
# Remove only CloudWatch alarms
C:\TF\terraform_1.14.2_windows_amd64\terraform.exe destroy `
  -target=aws_cloudwatch_metric_alarm.lambda_errors `
  -target=aws_cloudwatch_metric_alarm.lambda_duration
```

## Advanced Configuration

### VPC Deployment

Enable VPC for database access:

```hcl
# terraform.tfvars
enable_vpc         = true
vpc_id             = "vpc-xxxxx"
subnet_ids         = ["subnet-xxxxx", "subnet-yyyyy"]
security_group_ids = ["sg-xxxxx"]
```

### Lambda Layers

For large dependencies, use Lambda Layers:

```powershell
# Build layer
mkdir -p python/lib/python3.12/site-packages
pip install -r requirements.txt -t python/lib/python3.12/site-packages/
zip -r lambda_layer.zip python/

# Uncomment layer resource in main.tf
# Then apply
C:\TF\terraform_1.14.2_windows_amd64\terraform.exe apply
```

## Security Best Practices

1. **Encryption**: S3 encryption enabled by default (AES-256)
2. **Access Control**: S3 bucket blocks all public access
3. **Least Privilege**: IAM role has minimal required permissions
4. **Logging**: All Lambda invocations logged to CloudWatch
5. **Tracing**: X-Ray enabled for debugging and monitoring

## Support

For issues or questions:
1. Check CloudWatch logs for errors
2. Review Terraform documentation: https://registry.terraform.io/providers/hashicorp/aws/
3. AWS Lambda documentation: https://docs.aws.amazon.com/lambda/

## Updates

### Update Lambda Code

```powershell
# After code changes
C:\TF\terraform_1.14.2_windows_amd64\terraform.exe apply

# Force new deployment
C:\TF\terraform_1.14.2_windows_amd64\terraform.exe taint aws_lambda_function.x12_processor
C:\TF\terraform_1.14.2_windows_amd64\terraform.exe apply
```

### Update Configuration

```powershell
# Modify terraform.tfvars
# Then apply changes
C:\TF\terraform_1.14.2_windows_amd64\terraform.exe apply
```
