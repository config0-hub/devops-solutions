# AWS Step Function Stack

## Description
This stack creates and manages an AWS Step Function workflow using Terraform. It configures the necessary resources and permissions for running step functions in AWS.

## Variables

### Required Variables
| Name | Description | Default |
|------|-------------|---------|
| step_function_name | Step Function workflow name |  |

### Optional Variables
| Name | Description | Default |
|------|-------------|---------|
| aws_default_region | Default AWS region | eu-west-1 |

## Features
- Creates an AWS Step Function workflow with appropriate IAM permissions
- Outputs the Step Function ARN and Role ARN for reference
- Integrates with Config0 infrastructure automation

## Dependencies

### Substacks
- [config0-publish:::tf_executor](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/tf_executor)

### Execgroups
- [config0-publish:::devops-solutions::iac_ci_stepf](https://api-app.config0.com/web_api/v1.0/exec/groups/config0-publish/devops-solutions/iac_ci_stepf)

## License
Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.