# AWS Step Function Stack

## Description
This stack creates an AWS Step Function using Terraform. It configures and deploys a Step Function workflow in AWS with the specified name in the designated AWS region.

## Variables

### Required

| Name | Description | Default |
|------|-------------|---------|
| step_function_name | Step Function workflow name | &nbsp; |
| ci_environment | The CI environment | &nbsp; |

### Optional

| Name | Description | Default |
|------|-------------|---------|
| aws_default_region | Default AWS region | us-east-1 |

## Dependencies

### Substacks
- [config0-publish:::tf_executor](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/tf_executor)

### Execgroups
- [config0-publish:::devops-solutions::codebuild_ci_stepf](https://api-app.config0.com/web_api/v1.0/exec/groups/config0-publish/devops-solutions/codebuild_ci_stepf)

### Shelloutconfigs
None

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