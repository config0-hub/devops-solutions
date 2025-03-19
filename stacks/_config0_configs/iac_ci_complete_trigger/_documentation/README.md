# AWS SNS Topic Subscription with Lambda Integration

## Description
This stack creates an AWS SNS topic subscription that integrates with Lambda functions. It sets up the necessary infrastructure for event-driven architectures where SNS messages trigger Lambda functions.

## Variables

### Required Variables

| Name | Description | Default |
|------|-------------|---------|
| topic_name | SNS topic name | |
| lambda_name | Lambda function name | |

### Optional Variables

| Name | Description | Default |
|------|-------------|---------|
| aws_default_region | Default AWS region | eu-west-1 |

## Features
- Creates SNS topic subscription
- Integrates with Lambda functions
- Supports event-driven architecture patterns
- Configurable AWS region

## Dependencies

### Substacks
- [config0-publish:::tf_executor](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/tf_executor)

### Execgroups
- [config0-publish:::aws::codebuild_evntbrdg_sns_lambda](https://api-app.config0.com/web_api/v1.0/exec/groups/config0-publish/aws/codebuild_evntbrdg_sns_lambda)

## License
Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.