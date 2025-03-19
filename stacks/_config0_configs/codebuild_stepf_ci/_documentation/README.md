# AWS Step Function Stack

## Description
This stack creates an AWS Step Function using Terraform. It configures and deploys a Step Function workflow in AWS with the specified name in the designated AWS region.

## Variables

### Required

| Name | Description | Default |
|------|-------------|---------|
| step_function_name | Step Function workflow name | |

### Optional

| Name | Description | Default |
|------|-------------|---------|
| aws_default_region | Default AWS region | eu-west-1 |

## Features
- Creates an AWS Step Function with proper IAM role
- Outputs the Step Function's ARN and role ARN for further usage
- Integrates with Terraform for infrastructure-as-code management

## Dependencies

### Substacks
- [config0-publish:::tf_executor](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/tf_executor)

### Execgroups
- [config0-publish:::devops-solutions::codebuild_ci_stepf](https://api-app.config0.com/web_api/v1.0/exec/groups/config0-publish/devops-solutions/codebuild_ci_stepf)

## License
Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.