# AWS Step Function CI/CD Pipeline

This OpenTofu module creates a CI/CD pipeline implemented using AWS Step Functions to automate the process of triggering AWS CodeBuild projects from code repository webhooks.

## Overview

The pipeline consists of the following workflow:
1. Process incoming webhooks from code repositories
2. Package and upload code to S3
3. Trigger CodeBuild projects
4. Check CodeBuild execution status

## Requirements

- OpenTofu >= 1.8.8
- AWS provider
- AWS Lambda functions (referenced in the state machine)

## Usage

```hcl
module "cicd_pipeline" {
  source = "./modules/cicd-pipeline"
  
  # Optional customization
  aws_default_region = "us-east-1"
  step_function_name = "my-cicd-pipeline"
}
```

## Variables

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| aws_default_region | AWS region where resources will be deployed | string | "eu-west-1" | no |
| step_function_name | Name of the AWS Step Function state machine | string | "apigw-codebuild-ci" | no |
| process_webhook | Name of the Lambda function that processes webhooks | string | "process-webhook" | no |
| pkgcode_to_s3 | Name of the Lambda function that packages code to S3 | string | "pkgcode-to-s3" | no |
| check_codebuild | Name of the Lambda function that checks CodeBuild status | string | "check-codebuild" | no |
| trigger_codebuild | Name of the Lambda function that triggers CodeBuild | string | "trigger-codebuild" | no |
| cloud_tags | Additional tags as a map to apply to all resources | map(string) | {} | no |

## Outputs

| Name | Description |
|------|-------------|
| role_arn | ARN of the IAM role used by the Step Function state machine |
| arn | ARN of the Step Function state machine |

## Architecture

The Step Function state machine implements the following workflow:

1. **ProcessWebhook**: Processes incoming webhooks from code repositories
2. **PkgCodeToS3**: Packages the code and uploads it to S3
3. **TriggerCodebuild**: Starts the CodeBuild execution
4. **CheckCodebuild**: Monitors the CodeBuild execution status

Each step includes a choice state to determine whether to proceed to the next step or exit the workflow.

## Prerequisites

Before using this module, you need to have the following AWS Lambda functions created:
- process-webhook
- pkgcode-to-s3
- trigger-codebuild
- check-codebuild

## License

Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.