# AWS CodeBuild CI/CD Setup

This stack automates the setup of AWS CodeBuild CI/CD pipelines, including the necessary AWS resources like S3 buckets, ECR repositories, SSH keys, and GitHub webhooks.

## Variables

### Required Variables

| Name | Description | Default |
|------|-------------|---------|
| codebuild_name | CodeBuild project name | |
| git_repo | Configuration for repo | |
| git_url | 99checkme99 Git repository URL | |
| project_id | config0 builtin - id of Project | |
| ci_environment | CI/CD environment name | |
| security_group_id | Security group ID | null |

### Optional Variables

| Name | Description | Default |
|------|-------------|---------|
| slack_channel | 99checkme99 Slack channel for notifications | |
| ecr_repository_uri | 99checkme99 ECR repository URI | |
| ecr_repo_name | 99checkme99 ECR repository name | |
| docker_repository_uri | 99checkme99 Docker repository URI | |
| docker_repo_name | 99checkme99 Docker repository name | |
| docker_username | 99checkme99 Docker registry username | |
| run_title | 99checkme99 Title for the CodeBuild run | "codebuild_ci" |
| trigger_id | 99checkme99 Unique ID for the webhook trigger | "_random" |
| privileged_mode | Configuration for privileged mode | "true" |
| image_type | Configuration for image type | "LINUX_CONTAINER" |
| build_image | Configuration for build image | "aws/codebuild/standard:5.0" |
| build_timeout | Configuration for build timeout | "444" |
| compute_type | Configuration for compute type | "BUILD_GENERAL1_SMALL" |
| secret | Configuration for secret | "_random" |
| branch | Git branch name | "master" |
| suffix_id | Configuration for suffix id | |
| suffix_length | Configuration for suffix length | "4" |
| docker_registry | Docker registry URL | "ecr" |
| aws_default_region | Default AWS region | "us-west-1" |
| cloud_tags_hash | Resource tags for cloud provider | |
| bucket_acl | S3 bucket access permissions | "private" |
| bucket_expire_days | Days until object expiration | "1" |
| subnet_ids | Subnet ID list | "null" |
| vpc_id | VPC network identifier | "null" |

## Features

- Automatic creation of ECR repositories
- SSH key generation for GitHub repository access
- S3 bucket creation for build cache and artifacts
- GitHub webhook configuration
- AWS SSM Parameter Store integration for secure credentials
- DynamoDB configuration for build settings
- Fully automated AWS CodeBuild project setup

## Dependencies

### Substacks

- [config0-publish:::aws_ecr_repo](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/aws_ecr_repo)
- [config0-publish:::aws_s3_bucket](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/aws_s3_bucket)
- [config0-publish:::new_github_ssh_key](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/new_github_ssh_key)
- [config0-publish:::aws_dynamodb_item](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/aws_dynamodb_item)
- [config0-publish:::aws_ssm_param](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/aws_ssm_param)
- [config0-publish:::aws_codebuild](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/aws_codebuild)
- [config0-publish:::github_webhook](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/github_webhook)

## License

Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.