# IaC CI/CD Stack

## Description

This stack implements an Infrastructure as Code (IaC) Continuous Integration/Continuous Deployment pipeline. It configures automated build, test, and deployment processes for infrastructure code repositories, primarily designed for Terraform/OpenTofu workflows.

## Variables

### Required

| Name | Description | Default |
|------|-------------|---------|
| repo_name | Repository name containing infrastructure code | |
| branch | Git branch name | |

### Optional

| Name | Description | Default |
| ---- | ----------- | ------- |
| stateful_id | Stateful ID for storing the resource code/state | _random |
| tf_runtime | Terraform runtime version | tofu:1.6.2 |
| app_name | Application name | terraform |
| apply_keyword | 99checkme99 Keyword to trigger apply operations | null |
| check_keyword | 99checkme99 Keyword to trigger check operations | check tf |
| destroy_keyword | 99checkme99 Keyword to trigger destroy operations | null |
| require_approval | 99checkme99 Whether changes require approval before applying | False |
| source_method | 99checkme99 Method for sourcing infrastructure code | terraform |
| subdir | 99checkme99 Subdirectory within repository containing IaC code | null |
| ssm_name | SSM parameter name | null |

## Features

- Automated infrastructure code testing and deployment
- Integration with AWS CodeBuild for execution environment
- State management using DynamoDB for run history and settings
- Support for approval workflows before applying changes
- Configurable keywords for triggering specific operations

## Dependencies

### Substacks
- [config0-publish:::aws_codebuild](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/aws_codebuild)
- [config0-publish:::aws_dynamodb_item](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/aws_dynamodb_item)

## License

Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.