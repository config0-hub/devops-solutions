# AWS Step Function Stack

## Description
This stack creates and manages an AWS Step Function workflow using Terraform. It configures the necessary resources and permissions for running step functions in AWS.

## Variables

### Required Variables
| Name | Description | Default |
|------|-------------|---------|
| step_function_name | Step Function workflow name | &nbsp; |

### Optional Variables
| Name | Description | Default |
|------|-------------|---------|
| aws_default_region | Default AWS region | eu-west-1 |

## Dependencies

### Substacks
- [config0-publish:::tf_executor](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/stacks/config0-publish/tf_executor/default)

### Execgroups
- [config0-publish:::devops-solutions::iac_ci_stepf](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/exec/groups/config0-publish/devops-solutions/iac_ci_stepf/default)

### Shelloutconfigs
- [config0-publish:::terraform::resource_wrapper](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/shelloutconfigs/config0-publish/terraform/resource_wrapper/default)
- [config0-publish:::github::lambda_trigger_stepf](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/exec/groups/config0-publish/github/lambda_trigger_stepf/default)

## License
<pre>
Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.
</pre>