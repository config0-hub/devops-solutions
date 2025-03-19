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
| cloud_tags_hash | Resource tags for cloud provider |  |
| runtime | Configuration for runtime | python3.9 |

## Features
- DynamoDB tables for storing run information and settings
- Lambda functions for processing webhooks and events
- Step Function for orchestrating the CI workflow
- API Gateway for webhook integration
- SNS subscription for CodeBuild notifications
- IAM policies for secure resource access

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
Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.