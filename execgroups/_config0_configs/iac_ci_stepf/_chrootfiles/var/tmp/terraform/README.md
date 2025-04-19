# AWS Step Function CI/CD Pipeline

This module creates an AWS Step Function state machine that orchestrates a CI/CD pipeline using AWS services. The state machine processes webhooks from code repositories, executes CodeBuild jobs, and checks the results to enable automated infrastructure deployments.

## Overview

The state machine workflow handles:
- Processing webhook events from source code repositories
- Packaging code to S3 for deployment
- Triggering CodeBuild jobs for infrastructure validation and deployment
- Checking and reporting CodeBuild execution status
- Updating pull requests with deployment results

## Requirements

- OpenTofu >= 1.8.8
- AWS provider
- IAM permissions to create and manage Step Functions, IAM roles, and Lambda functions

## Usage

```hcl
module "ci_cd_step_function" {
  source = "path/to/module"

  app_name           = "my-infra-ci"
  step_function_name = "my-ci-pipeline"
  
  # Optional: Override default values
  aws_default_region = "us-east-1"
  cloud_tags = {
    Environment = "Development"
    Project     = "Infrastructure"
  }
}
```

## Variables

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| `aws_default_region` | AWS region where resources will be deployed | `string` | `"eu-west-1"` | no |
| `step_function_name` | Name of the AWS Step Function state machine | `string` | `"apigw-codebuild-ci"` | no |
| `app_name` | Prefix for all Lambda functions and other resources | `string` | `"iac-ci"` | no |
| `process_webhook` | Name suffix for the Lambda function that processes webhooks | `string` | `"process-webhook"` | no |
| `pkgcode_to_s3` | Name suffix for the Lambda function that packages code to S3 | - | `"pkgcode-to-s3"` | no |
| `trigger_lambda` | Name suffix for the Lambda function that triggers other Lambda functions | - | `"trigger-lambda"` | no |
| `update_pr` | Name suffix for the Lambda function that updates pull requests | - | `"update-pr"` | no |
| `check_codebuild` | Name suffix for the Lambda function that checks CodeBuild status | - | `"check-codebuild"` | no |
| `trigger_codebuild` | Name suffix for the Lambda function that triggers CodeBuild jobs | - | `"trigger-codebuild"` | no |
| `cloud_tags` | Additional tags to apply to all resources | `map(string)` | `{}` | no |

## Outputs

| Name | Description |
|------|-------------|
| `role_arn` | ARN of the IAM role used by the Step Function state machine |
| `arn` | ARN of the Step Function state machine |

## State Machine Workflow

1. **ProcessWebhook**: Processes incoming webhook events
2. **ChkProcessWebhook**: Determines next action based on webhook content
3. **PkgCodeToS3**: Packages code to S3 (for validation)
4. **TriggerLambda**: Triggers Lambda functions for PR checks
5. **EvaluatePr**: Updates PR with validation results
6. **TriggerCodebuild**: Triggers CodeBuild for infrastructure deployments
7. **CheckCodebuild**: Monitors CodeBuild job status

## Notes

- This module only creates the Step Function state machine and associated IAM role
- The Lambda functions referenced in the state machine must be created separately
- You will need to set up API Gateway or other triggers to invoke the Step Function

## License

Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.