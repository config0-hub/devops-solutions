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
| runtime | Configuration for runtime | python3.11 |
| aws_default_region | AWS region for deployment | us-east-1 |

## Dependencies

### Substacks
- [config0-publish:::aws_dynamodb](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/aws_dynamodb)
- [config0-publish:::apigw_lambda-integ](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/apigw_lambda-integ)
- [config0-publish:::aws-lambda-python-codebuild](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/aws-lambda-python-codebuild)
- [config0-publish:::iac_ci_stepf](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/iac_ci_stepf)
- [config0-publish:::iac_ci_complete_trigger](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/iac_ci_complete_trigger)

### Execgroups
- [config0-publish:::github::lambda_trigger_stepf](https://api-app.config0.com/web_api/v1.0/exec/groups/config0-publish/github/lambda_trigger_stepf)
- [config0-publish:::devops-solutions::iac_ci](https://api-app.config0.com/web_api/v1.0/exec/groups/config0-publish/devops-solutions/iac_ci)

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
