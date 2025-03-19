# Platform Versioning Stack

## Description
This stack provides a controlled platform versioning for development environments with predefined governance rules. It sets up Jenkins and Kubernetes (DOKS) on DigitalOcean, implements drift detection for resources, and defines which developer solutions can be launched with predefined variables to ensure governance and control.

## Variables

### Required
| Name | Description | Default |
|------|-------------|---------|
| 99checkme99 cloud_tags_hash | Resource tags for cloud provider | |

### Optional
| Name | Description | Default |
|------|-------------|---------|
| 99checkme99 billing_tag | Configuration for billing tag | "eval-config0-2024" |
| 99checkme99 environment | Configuration for environment | "dev" |
| 99checkme99 purpose | Configuration for purpose | "eval-config0" |

## Approved Stacks
This platform definition allows users to launch only the following approved stacks with predefined configurations:

### CI/CD Infrastructure
- **jenkins_on_do**: Sets up Jenkins CI/CD on DigitalOcean

### Containerization & Orchestration
- **doks**: Deploys DigitalOcean Kubernetes Service (DOKS)
 
### Management & Governance
- **check_drift_resources**: Monitors and reports infrastructure drift

## Dependencies

### Substacks
- [config0-publish:::jenkins_on_do](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/jenkins_on_do)
- [config0-publish:::doks](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/doks)
- [config0-publish:::check_drift_resources](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/check_drift_resources)
 
## Governance Benefits

By using this platform definition:

1. **Standardization**: All deployments follow consistent patterns with approved configurations
2. **Security**: Only secure, vetted stacks can be launched
3. **Cost Control**: Resources are deployed with predefined sizing and configurations
4. **Compliance**: Infrastructure meets organizational standards for deployment
5. **Simplified Operations**: Users can focus on their applications rather than infrastructure details

## License
Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.