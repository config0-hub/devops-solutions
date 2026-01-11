# AWS CI/CD Environment Stack

## Description
This stack sets up a complete CI/CD environment in AWS, including S3 buckets, DynamoDB tables, Lambda functions, Step Functions, API Gateway, and SNS subscriptions to create a serverless CI/CD pipeline.

## Variables

### Required Variables
| Name | Description | Default |
|------|-------------|---------|
| ci_environment | CI/CD environment name | config0-eval |

### Optional Variables
| Name | Description | Default |
|------|-------------|---------|
| suffix_id | Configuration for suffix id | &nbsp; |
| suffix_length | Configuration for suffix length | 4 |
| aws_default_region | Default AWS region | us-east-1 |
| cloud_tags_hash | Resource tags for cloud provider | &nbsp; |
| bucket_acl | S3 bucket access permissions | private |
| bucket_expire_days | Days until object expiration | 7 |
| runtime | Lambda runtime environment | python3.11 |
| lambda_layers | Lambda function layers | &nbsp; |

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

### Shelloutconfigs
None identified in the provided code.

## License
<pre>
Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
</pre>
