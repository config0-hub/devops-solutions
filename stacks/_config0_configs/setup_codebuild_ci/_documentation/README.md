# AWS CI/CD Environment Stack

## Description
This stack sets up a complete CI/CD environment in AWS, including S3 buckets, DynamoDB tables, Lambda functions, Step Functions, API Gateway, and SNS subscriptions to create a serverless CI/CD pipeline.

## Variables

### Required Variables
| Name | Description | Default |
|------|-------------|---------|
| ci_environment | CI/CD environment name | &nbsp; |

### Optional Variables
| Name | Description | Default |
|------|-------------|---------|
| suffix_id | Configuration for suffix id | &nbsp; |
| suffix_length | Configuration for suffix length | 4 |
| aws_default_region | Default AWS region | eu-west-1 |
| cloud_tags_hash | Resource tags for cloud provider | &nbsp; |
| bucket_acl | S3 bucket access permissions | private |
| bucket_expire_days | Days until object expiration | 7 |
| runtime | Lambda runtime environment | python3.9 |
| lambda_layers | Lambda function layers | arn:aws:lambda:eu-west-1:553035198032:layer:git-lambda2:8 |

## Dependencies

### Substacks
- [config0-publish:::aws_s3_bucket](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/stacks/config0-publish/aws_s3_bucket/default)
- [config0-publish:::aws_dynamodb](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/stacks/config0-publish/aws_dynamodb/default)
- [config0-publish:::aws-lambda-python-codebuild](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/stacks/config0-publish/aws-lambda-python-codebuild/default)
- [config0-publish:::apigw_lambda-integ](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/stacks/config0-publish/apigw_lambda-integ/default)
- [config0-publish:::codebuild_stepf_ci](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/stacks/config0-publish/codebuild_stepf_ci/default)
- [config0-publish:::codebuild_complete_trigger](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/stacks/config0-publish/codebuild_complete_trigger/default)

### Execgroups
- [config0-publish:::github::lambda_trigger_stepf](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/exec/groups/config0-publish/github/lambda_trigger_stepf/default)
- [config0-publish:::github::lambda_codebuild_ci](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/exec/groups/config0-publish/github/lambda_codebuild_ci/default)

### Shelloutconfigs
- [config0-publish:::terraform::resource_wrapper](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/shelloutconfigs/config0-publish/terraform/resource_wrapper/default)

## License
<pre>
Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.
</pre>