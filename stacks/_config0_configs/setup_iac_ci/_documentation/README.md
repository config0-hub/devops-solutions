# IAC CI Stack

## Description
This stack automates the creation of the developer solution "iac-ci" on top of AWS. It creates and configures DynamoDB tables, Lambda functions, Step Functions, API Gateway, and SNS subscriptions to provide a complete CI workflow for IaC projects.

## Variables

### Required
| Name | Description | Default |
|------|-------------|---------|
| app_name | Application name | iac-ci |

### Optional
| Name | Description | Default |
|------|-------------|---------|
| cloud_tags_hash | Resource tags for cloud provider | &nbsp; |
| runtime | Configuration for runtime | python3.9 |

## Dependencies

### Substacks
- [config0-publish:::aws_dynamodb](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/stacks/config0-publish/aws_dynamodb/default)
- [config0-publish:::apigw_lambda-integ](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/stacks/config0-publish/apigw_lambda-integ/default)
- [config0-publish:::aws-lambda-python-codebuild](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/stacks/config0-publish/aws-lambda-python-codebuild/default)
- [config0-publish:::iac_ci_stepf](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/stacks/config0-publish/iac_ci_stepf/default)
- [config0-publish:::iac_ci_complete_trigger](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/stacks/config0-publish/iac_ci_complete_trigger/default)

### Execgroups
- [config0-publish:::github::lambda_trigger_stepf](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/exec/groups/config0-publish/github/lambda_trigger_stepf/default)
- [config0-publish:::devops-solutions::iac_ci](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/exec/groups/config0-publish/devops-solutions/iac_ci/default)

### Shelloutconfigs
- [config0-publish:::terraform::resource_wrapper](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/shelloutconfigs/config0-publish/terraform/resource_wrapper/default)

## License
<pre>
Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.
</pre>