# Platform Versioning Stack

## Description
This stack provides a controlled platform versioning for development environments with predefined governance rules. It sets up Jenkins and Kubernetes (DOKS) on DigitalOcean, implements drift detection for resources, and defines which developer solutions can be launched with predefined variables to ensure governance and control.

## Variables

### Required
| Name | Description | Default |
|------|-------------|---------|
| cloud_tags_hash | Resource tags for cloud provider | &nbsp; |

### Optional
| Name | Description | Default |
|------|-------------|---------|
| billing_tag | Configuration for billing tag | "eval-config0-2024" |
| environment | Configuration for environment | "dev" |
| purpose | Configuration for purpose | "eval-config0" |

## Dependencies

### Substacks
- [config0-publish:::jenkins_on_do](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/stacks/config0-publish/jenkins_on_do/default)
- [config0-publish:::doks](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/stacks/config0-publish/doks/default)
- [config0-publish:::check_drift_resources](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/stacks/config0-publish/check_drift_resources/default)

### Execgroups
- [config0-publish:::github::lambda_trigger_stepf](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/exec/groups/config0-publish/github/lambda_trigger_stepf/default)

### Shelloutconfigs
- [config0-publish:::terraform::resource_wrapper](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/shelloutconfigs/config0-publish/terraform/resource_wrapper/default)

## License
<pre>
Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.
</pre>