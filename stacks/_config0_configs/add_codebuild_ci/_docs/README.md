# AWS CodeBuild CI/CD Setup

This stack automates the setup of AWS CodeBuild CI/CD pipelines, including the necessary AWS resources like S3 buckets, ECR repositories, SSH keys, and GitHub webhooks.

The deploy key is an EC2 key pair made by `new_github_ssh_key`: EC2 keeps the private half in SSM
Parameter Store at `/ec2/keypair/<key_pair_id>`, and the `ssh_key_pair` row names that parameter in
`private_key_ssm_path`. This stack hands the NAME to the Lambdas (settings row `ssm_ssh_key`) and to
the CodeBuild project (buildspec `parameter-store` entry `SSH_KEY`); the `ssm` job uploads the
optional Docker token and Slack webhook, never the key.

The `ci-shared-settings` row the `connect_repo` job writes carries what the Lambdas need to run a build:
the repository and branch, the webhook secret, the deploy key's SSM parameter name, the buckets and the
registry. It carries no Config0 endpoint: the Lambdas do not post a build's result to Config0 (decided
2026-10-18, CON-101). The result is the run row in `ci-shared-runs` and, with a Slack webhook, the Slack
message.

## Variables

### Required Variables

| Name | Description | Default |
|------|-------------|---------|
| codebuild_name | CodeBuild project name | &nbsp; |
| git_repo | GitHub repository name | &nbsp; |
| git_url | Git repository URL | &nbsp; |
| ci_environment | CI/CD environment name | &nbsp; |

### Optional Variables

| Name | Description | Default |
|------|-------------|---------|
| slack_channel | Slack channel for notifications | &nbsp; |
| ecr_repository_uri | ECR repository URI | &nbsp; |
| ecr_repo_name | ECR repository name | &nbsp; |
| docker_repository_uri | Docker repository URI | &nbsp; |
| docker_repo_name | Docker repository name | &nbsp; |
| docker_username | Docker registry username | &nbsp; |
| run_title | Title for the CodeBuild run | "codebuild_ci" |
| trigger_id | Unique ID for the webhook trigger | "_random" |
| privileged_mode | Enable privileged mode for Docker commands | "true" |
| image_type | Container image type | "LINUX_CONTAINER" |
| build_image | Build environment image | "aws/codebuild/standard:5.0" |
| build_timeout | Build timeout in minutes | "444" |
| compute_type | Compute resources for build | "BUILD_GENERAL1_SMALL" |
| secret | Secret for webhook security | "_random" |
| branch | Git branch name | "master" |
| suffix_id | Unique suffix for resource names | &nbsp; |
| suffix_length | Length of generated suffix | "4" |
| docker_registry | Docker registry type | "ecr" |
| cloud_tags_hash | Resource tags for cloud resources | &nbsp; |
| bucket_acl | S3 bucket access permissions | "private" |
| bucket_expire_days | Days until bucket objects expire | "1" |
| subnet_ids | Subnet IDs for VPC configuration | None |
| vpc_id | VPC ID for network configuration | None |
| security_group_id | Security group ID | None |
| aws_default_region | Default AWS region | "us-east-1" |

## Dependencies

### Substacks

- [config0-hub:::aws_storage::aws_ecr_repo](https://api-app.config0.com/web_api/v1.0/stacks/config0-hub/aws_ecr_repo)
- [config0-hub:::aws_storage::aws_s3_bucket](https://api-app.config0.com/web_api/v1.0/stacks/config0-hub/aws_s3_bucket)
- [config0-hub:::github::new_github_ssh_key](https://api-app.config0.com/web_api/v1.0/stacks/config0-hub/new_github_ssh_key)
- [config0-hub:::aws_storage::aws_dynamodb_item](https://api-app.config0.com/web_api/v1.0/stacks/config0-hub/aws_dynamodb_item)
- [config0-hub:::aws_storage::aws_ssm_param](https://api-app.config0.com/web_api/v1.0/stacks/config0-hub/aws_ssm_param)
- [config0-hub:::aws::aws_codebuild](https://api-app.config0.com/web_api/v1.0/stacks/config0-hub/aws_codebuild)
- [config0-hub:::github::github_webhook](https://api-app.config0.com/web_api/v1.0/stacks/config0-hub/github_webhook)

### Execgroups

No execgroups were found in the current code.

### Scripts

No scripts were found in the current code.

## License
<pre>
Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.
</pre>