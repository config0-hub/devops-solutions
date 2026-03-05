# AWS Platform Configuration

## Description
This stack configures a platform environment including networking, security groups, and various AWS services. It sets up infrastructure for development, evaluation, and deployment of applications in AWS and DigitalOcean cloud environments.

## Variables

### Required
| Name | Description | Default |
|------|-------------|---------|
| aws_default_region | Default AWS region | eu-west-1 |

### Optional
| Name | Description | Default |
|------|-------------|---------|
| cloud_tags_hash | Resource tags for cloud provider | &nbsp; |
| labels_hash | Resource label in base64 | &nbsp; |
| vpc_id | VPC network identifier | &nbsp; |
| vpc_name | VPC network name | &nbsp; |
| public_subnet_ids | Public subnet IDs | &nbsp; |
| private_subnet_ids | Private subnet IDs | &nbsp; |
| private_route_table_id | Private route table ID | &nbsp; |
| db_sg_id | Database security group ID | &nbsp; |
| bastion_sg_id | Bastion host security group | &nbsp; |
| netvars_set_labels_hash | Labels in base64 for network variable set | &nbsp; |
| netvars_set_arguments_hash | Arguments in base64 for network variable set | &nbsp; |
| eks_node_role_arn | IAM role ARN for EKS nodes | &nbsp; |

## Dependencies

### Substacks
- [config0-hub:::aws_networking::aws_vpc_simple](https://api-app.config0.com/web_api/v1.0/stacks/config0-hub/aws_vpc_simple)
- [config0-hub:::config0_core::network_vars_set](https://api-app.config0.com/web_api/v1.0/stacks/config0-hub/network_vars_set)
- [config0-hub:::devops-solutions::setup_iac_ci](https://api-app.config0.com/web_api/v1.0/stacks/config0-hub/setup_iac_ci)
- [config0-hub:::devops-solutions::register_repo_iac_ci](https://api-app.config0.com/web_api/v1.0/stacks/config0-hub/register_repo_iac_ci)
- [config0-hub:::devops-solutions::add_iac_ci](https://api-app.config0.com/web_api/v1.0/stacks/config0-hub/add_iac_ci)
- [config0-hub:::devops-solutions::setup_codebuild_ci](https://api-app.config0.com/web_api/v1.0/stacks/config0-hub/setup_codebuild_ci)
- [config0-hub:::devops-solutions::add_codebuild_ci](https://api-app.config0.com/web_api/v1.0/stacks/config0-hub/add_codebuild_ci)
- [config0-hub:::aws_networking::aws_nat_inst_vpc](https://api-app.config0.com/web_api/v1.0/stacks/config0-hub/aws_nat_inst_vpc)
- [config0-hub:::aws_networking::aws_nat_vpc](https://api-app.config0.com/web_api/v1.0/stacks/config0-hub/aws_nat_vpc)
- [config0-hub:::aws_storage::aws_rds](https://api-app.config0.com/web_api/v1.0/stacks/config0-hub/aws_rds)
- [config0-hub:::mongodb::mongodb_replica_on_ec2](https://api-app.config0.com/web_api/v1.0/stacks/config0-hub/mongodb_replica_on_ec2)
- [config0-hub:::kafka::kafka_on_ec2](https://api-app.config0.com/web_api/v1.0/stacks/config0-hub/kafka_on_ec2)
- [config0-hub:::aws_eks::aws_eks](https://api-app.config0.com/web_api/v1.0/stacks/config0-hub/aws_eks)
- [config0-hub:::do::jenkins_on_do](https://api-app.config0.com/web_api/v1.0/stacks/config0-hub/jenkins_on_do)
- [config0-hub:::do::doks](https://api-app.config0.com/web_api/v1.0/stacks/config0-hub/doks)
- [config0-hub:::config0_core::check_drift_resources](https://api-app.config0.com/web_api/v1.0/stacks/config0-hub/check_drift_resources)
- [config0-hub:::devops-solutions::env_sql](https://api-app.config0.com/web_api/v1.0/stacks/config0-hub/env_sql)
- [config0-hub:::devops-solutions::env_nosql](https://api-app.config0.com/web_api/v1.0/stacks/config0-hub/env_nosql)
- [config0-hub:::devops-solutions::env_streaming](https://api-app.config0.com/web_api/v1.0/stacks/config0-hub/env_streaming)

## License
<pre>
Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.
</pre>