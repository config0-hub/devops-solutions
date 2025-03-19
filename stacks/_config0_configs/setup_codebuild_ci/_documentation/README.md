# AWS CI/CD Environment Stack

## Description
This stack sets up a complete CI/CD environment in AWS, including S3 buckets, DynamoDB tables, Lambda functions, Step Functions, API Gateway, and SNS subscriptions to create a serverless CI/CD pipeline.

## Variables

### Required Variables
| Name | Description | Default |
|------|-------------|---------|
| ci_environment | CI/CD environment name | |

### Optional Variables
| Name | Description | Default |
|------|-------------|---------|
| suffix_id | Configuration for suffix id | |
| suffix_length | Configuration for suffix length | 4 |
| aws_default_region | Default AWS region | eu-west-1 |
| cloud_tags_hash | Resource tags for cloud provider | |
| bucket_acl | S3 bucket access permissions | private |
| bucket_expire_days | Days until object expiration | 7 |
| runtime | Configuration for runtime | python3.9 |
| lambda_layers | Lambda function layers | arn:aws:lambda:eu-west-1:553035198032:layer:git-lambda2:8 |

## Features
- Creates permanent and temporary S3 buckets for CI/CD artifacts with configurable lifecycle policies
- Sets up DynamoDB tables for tracking runs and settings
- Deploys multiple Lambda functions with appropriate IAM policies
- Configures Step Functions for workflow orchestration
- Integrates with API Gateway for webhook processing
- Sets up SNS subscriptions for notifications on build completion

## Dependencies

### Substacks
- [config0-publish:::aws_s3_bucket](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/aws_s3_bucket)
- [config0-publish:::aws_dynamodb](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/aws_dynamodb)
- [config0-publish:::aws-lambda-python-codebuild](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/aws-lambda-python-codebuild)
- [config0-publish:::apigw_lambda-integ](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/apigw_lambda-integ)
- [config0-publish:::codebuild_stepf_ci](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/codebuild_stepf_ci)
- [config0-publish:::codebuild_complete_trigger](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/codebuild_complete_trigger)

### Execgroups
- [config0-publish:::github::lambda_trigger_stepf](https://api-app.config0.com/web_api/v1.0/exec/groups/config0-publish/github/lambda_trigger_stepf)
- [config0-publish:::github::lambda_codebuild_ci](https://api-app.config0.com/web_api/v1.0/exec/groups/config0-publish/github/lambda_codebuild_ci)

## License
Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.