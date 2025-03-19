# AWS SNS Topic Subscription with Lambda

## Description

This stack configures an AWS SNS topic subscription that connects to a Lambda function, enabling event-driven architectures. The infrastructure is created using Terraform through the Config0 platform.

## Variables

### Required

| Name | Description | Default |
|------|------------|---------|
| topic_name | SNS topic name | |
| lambda_name | Lambda function name | |

### Optional

| Name | Description | Default |
|------|------------|---------|
| aws_default_region | Default AWS region | eu-west-1 |

## Features

- Creates an SNS topic subscription for Lambda event integration
- Configures AWS resources with proper permissions
- Outputs subscription details including topic ARN and endpoint

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