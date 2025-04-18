# AWS CodeBuild CI/CD Setup

This stack automates the setup of AWS CodeBuild CI/CD pipelines, including the necessary AWS resources like S3 buckets, ECR repositories, SSH keys, and GitHub webhooks.

## Variables

### Required Variables

| Name | Description | Default |
|------|-------------|---------|
| codebuild_name | CodeBuild project name | &nbsp; |
| git_repo | GitHub repository name | &nbsp; |
| git_url | Git repository URL | &nbsp; |
| project_id | Config0 project ID | &nbsp; |
| ci_environment | CI/CD environment name | &nbsp; |
| security_group_id | Security group ID | null |

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
| aws_default_region | Default AWS region | "us-west-1" |
| cloud_tags_hash | Resource tags for cloud resources | &nbsp; |
| bucket_acl | S3 bucket access permissions | "private" |
| bucket_expire_days | Days until bucket objects expire | "1" |
| subnet_ids | Subnet IDs for VPC configuration | "null" |
| vpc_id | VPC ID for network configuration | "null" |

## Dependencies

### Substacks

- [config0-publish:::aws_ecr_repo](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/stacks/config0-publish/aws_ecr_repo/default)
- [config0-publish:::aws_s3_bucket](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/stacks/config0-publish/aws_s3_bucket/default)
- [config0-publish:::new_github_ssh_key](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/stacks/config0-publish/new_github_ssh_key/default)
- [config0-publish:::aws_dynamodb_item](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/stacks/config0-publish/aws_dynamodb_item/default)
- [config0-publish:::aws_ssm_param](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/stacks/config0-publish/aws_ssm_param/default)
- [config0-publish:::aws_codebuild](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/stacks/config0-publish/aws_codebuild/default)
- [config0-publish:::github_webhook](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/stacks/config0-publish/github_webhook/default)

### Execgroups

- [config0-publish:::github::lambda_trigger_stepf](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/exec/groups/config0-publish/github/lambda_trigger_stepf/default)

### Shelloutconfigs

- [config0-publish:::terraform::resource_wrapper](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/shelloutconfigs/config0-publish/terraform/resource_wrapper/default)

## License
<pre>
Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.
</pre>