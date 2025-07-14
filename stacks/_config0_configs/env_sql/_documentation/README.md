# 3-Tier SQL Environment with RDS and EKS

## Description
This stack creates a complete three-tier environment in AWS, including networking infrastructure, an EKS cluster for application hosting, and an RDS database. It configures the necessary security groups, subnets, and routing to establish a secure, scalable application environment.

## Variables

### Required
| Name | Description | Default |
|------|-------------|---------|
| env_name | Configuration for env name | &nbsp; |
| vpc_id | VPC network identifier | &nbsp; |
| db_sg_id | Database security group ID | &nbsp; |

### Optional
| Name | Description | Default |
|------|-------------|---------|
| aws_default_region | Default AWS region | eu-west-1 |
| cloud_tags_hash | Resource tags for cloud provider | &nbsp; |
| public_subnet_ids | Public subnet IDs | null |
| private_route_table_id | Private route table ID | null |
| private_subnet_ids | Private subnet IDs | null |
| netvars_set_labels_hash | Labels in base64 that are inserted by the network variable set | null |
| netvars_set_arguments_hash | Arguments in base64 that are inserted by the network variable set | null |
| nat_instance_types | NAT instance compute types | t3.nano,t3a.nano |
| nat_cidr_ingress_accept | Allowed CIDR blocks for NAT | 0.0.0.0/0 |
| eks_cluster | EKS cluster name | null |
| eks_cluster_version | Kubernetes version for EKS | 1.29 |
| eks_cluster_sg_id | EKS cluster security group ID | null |
| eks_node_role_arn | IAM role ARN for EKS nodes | null |
| eks_node_max_capacity | Maximum EKS node count | 1 |
| eks_node_min_capacity | Minimum EKS node count | 1 |
| eks_node_desired_capacity | Desired EKS node count | 1 |
| eks_node_disksize | Disk size for EKS nodes (GB) | 25 |
| eks_node_instance_types | EC2 instance types for EKS nodes | ["t3.medium","t3.large"] |
| eks_node_ami_type | AMI type for EKS nodes | AL2_x86_64 |
| db_allocated_storage | Configuration for db allocated storage | 30 |
| db_engine | Configuration for db engine | MySQL |
| db_engine_version | Configuration for db engine version | 8.0.35 |
| db_instance_class | Configuration for db instance class | db.t3.micro |
| db_multi_az | Configuration for db multi az | false |
| db_storage_type | Configuration for db storage type | gp2 |
| db_master_username | Database admin username | &nbsp; |
| db_master_password | Database admin password | &nbsp; |

## Dependencies

### Substacks
- [config0-publish:::network](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/network)
- [config0-publish:::rds_eks](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/rds_eks)

### Execgroups
No execgroups explicitly added in the code.

### Shelloutconfigs
No shelloutconfigs explicitly added in the code.

## License
<pre>
Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.
</pre>