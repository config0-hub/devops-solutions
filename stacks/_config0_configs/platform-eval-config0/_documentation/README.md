# AWS Platform Configuration

## Description
This stack configures a platform environment including networking, security groups, and various AWS services. It sets up the infrastructure for development, evaluation, and deployment of applications in AWS and DigitalOcean cloud environments.

This platform definition enforces governance and control by limiting which developer solutions or stacks can be launched with predefined variables. This ensures that users can only execute approved infrastructure components with standardized configurations.

## Variables

### Required
| Name | Description | Default |
|------|-------------|---------|
| aws_default_region | Default AWS region | eu-west-1 |

### Optional
| Name | Description | Default |
|------|-------------|---------|
| cloud_tags_hash | Resource tags for cloud provider | |
| labels_hash | Resource label in base64 | |
| vpc_id | VPC network identifier | |
| vpc_name | VPC network name | |
| public_subnet_ids | Public subnet IDs | |
| private_subnet_ids | Private subnet IDs | |
| private_route_table_id | Private route table ID | |
| db_sg_id | Database security group ID | |
| bastion_sg_id | Bastion host security group | |
| netvars_set_labels_hash | Labels in base64 that are inserted by the network variable set | |
| netvars_set_arguments_hash | Arguments in base64 that are inserted by the network variable set | |
| eks_node_role_arn | IAM role ARN for EKS nodes | |

## Approved Stacks

This platform definition allows users to launch only the following approved stacks with predefined configurations:

### Networking
- **aws_vpc_simple**: Creates a VPC with public and private subnets
- **network_vars_set**: Sets networking variables for downstream stacks
- **aws_nat_inst_vpc**: Deploys a NAT instance for private subnet internet access
- **aws_nat_vpc**: Sets up AWS NAT gateway for private subnet internet access

### CI/CD Infrastructure
- **setup_iac_ci**: Creates the foundation for Infrastructure as Code CI/CD
- **register_repo_iac_ci**: Registers repositories for IaC CI/CD
- **add_iac_ci**: Adds CI/CD workflows for Infrastructure as Code
- **setup_codebuild_ci**: Sets up AWS CodeBuild for CI/CD
- **add_codebuild_ci**: Adds CodeBuild CI/CD workflows to repositories

### Database & Storage
- **aws_rds**: Deploys managed relational database instances
- **mongodb_replica_on_ec2**: Creates MongoDB replica sets on EC2
- **env_sql**: Comprehensive SQL database environment
- **env_nosql**: Complete NoSQL database environment

### Containerization & Orchestration
- **aws_eks**: Deploys Amazon Elastic Kubernetes Service
- **doks**: Sets up DigitalOcean Kubernetes Service

### Streaming & Messaging
- **kafka_on_ec2**: Deploys Apache Kafka clusters on EC2
- **env_streaming**: Complete streaming platform environment

### CI/CD Tools
- **jenkins_on_do**: Sets up Jenkins CI/CD on DigitalOcean

### Management & Governance
- **check_drift_resources**: Monitors and reports infrastructure drift

## Dependencies

### Substacks
- [config0-publish:::aws_vpc_simple](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/aws_vpc_simple)
- [config0-publish:::network_vars_set](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/network_vars_set)
- [config0-publish:::setup_iac_ci](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/setup_iac_ci)
- [config0-publish:::register_repo_iac_ci](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/register_repo_iac_ci)
- [config0-publish:::add_iac_ci](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/add_iac_ci)
- [config0-publish:::setup_codebuild_ci](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/setup_codebuild_ci)
- [config0-publish:::add_codebuild_ci](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/add_codebuild_ci)
- [config0-publish:::aws_nat_inst_vpc](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/aws_nat_inst_vpc)
- [config0-publish:::aws_nat_vpc](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/aws_nat_vpc)
- [config0-publish:::aws_rds](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/aws_rds)
- [config0-publish:::mongodb_replica_on_ec2](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/mongodb_replica_on_ec2)
- [config0-publish:::kafka_on_ec2](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/kafka_on_ec2)
- [config0-publish:::aws_eks](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/aws_eks)
- [config0-publish:::jenkins_on_do](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/jenkins_on_do)
- [config0-publish:::doks](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/doks)
- [config0-publish:::check_drift_resources](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/check_drift_resources)
- [config0-publish:::env_sql](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/env_sql)
- [config0-publish:::env_nosql](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/env_nosql)
- [config0-publish:::env_streaming](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/env_streaming)

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