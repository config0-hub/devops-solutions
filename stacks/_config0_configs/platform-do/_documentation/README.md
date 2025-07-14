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
- [config0-publish:::jenkins_on_do](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/jenkins_on_do)
- [config0-publish:::doks](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/doks)
- [config0-publish:::check_drift_resources](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/check_drift_resources)

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