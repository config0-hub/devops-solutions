# AWS RDS & EKS Infrastructure Stack

## Description
This stack creates an AWS RDS database instance and an EKS cluster in parallel. It provisions the necessary infrastructure for a containerized application with a managed database backend.

## Variables

### Required Variables

| Name | Description | Default |
|------|-------------|---------|
| env_name | Environment name | &nbsp; |
| db_sg_id | Database security group ID | &nbsp; |
| vpc_id | VPC network identifier | &nbsp; |

### Optional Variables

| Name | Description | Default |
|------|-------------|---------|
| aws_default_region | Default AWS region | eu-west-1 |
| cloud_tags_hash | Resource tags for cloud provider | &nbsp; |
| public_subnet_ids | Public subnet IDs | null |
| private_subnet_ids | Private subnet IDs | null |
| db_allocated_storage | Configuration for db allocated storage | 30 |
| db_engine | Configuration for db engine | MySQL |
| db_engine_version | Configuration for db engine version | 8.0.35 |
| db_instance_class | Configuration for db instance class | db.t3.micro |
| db_multi_az | Configuration for db multi az | false |
| db_storage_type | Configuration for db storage type | gp2 |
| db_master_username | Database admin username | &nbsp; |
| db_master_password | Database admin password | &nbsp; |
| eks_cluster_version | Kubernetes version for EKS | 1.29 |
| eks_cluster_sg_id | EKS cluster security group ID | null |
| eks_node_role_arn | IAM role ARN for EKS nodes | null |
| eks_node_max_capacity | Maximum EKS node count | 1 |
| eks_node_min_capacity | Minimum EKS node count | 1 |
| eks_node_desired_capacity | Desired EKS node count | 1 |
| eks_node_disksize | Disk size for EKS nodes (GB) | 25 |
| eks_node_instance_types | EC2 instance types for EKS nodes | ["t3.medium", "t3.large"] |
| eks_node_ami_type | AMI type for EKS nodes | AL2_x86_64 |

## Dependencies

### Substacks
- [config0-publish:::aws_rds](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/aws_rds)
- [config0-publish:::aws_eks](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/aws_eks)

### Execgroups
None identified in the code.

### Shelloutconfigs
None identified in the code.

## License
<pre>
Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.
</pre>