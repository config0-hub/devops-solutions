# MongoDB/EKS Deployment Stack

## Description
This stack deploys both a MongoDB replica set on EC2 instances and an Amazon EKS cluster in parallel. It configures all necessary resources for both services within the specified VPC.
Server access goes through the regional SSM executor (ssm_ec2_exec_eventbridge_install); the legacy bastion host is intentionally not used.

## Variables

### Required Variables

| Name | Description | Default |
|------|-------------|---------|
| env_name | Configuration for env name | &nbsp; |
| vpc_id | VPC network identifier | &nbsp; |
| ssh_key_name | EC2 key pair name for the MongoDB instances | &nbsp; |
| instance_profile_name | IAM instance profile granting SSM access | &nbsp; |
| managed_tag_key | Tag key the SSM executor matches on | &nbsp; |
| managed_tag_value | Tag value the SSM executor matches on | &nbsp; |
| install_name | Name of the `ssm_ec2_exec_eventbridge_install` record the host orders run through | &nbsp; |
| db_sg_id | Database security group ID | null |

### Optional Variables

| Name | Description | Default |
|------|-------------|---------|
| aws_default_region | Default AWS region | eu-west-1 |
| cloud_tags_hash | Resource tags for cloud provider | &nbsp; |
| public_subnet_ids | Public subnet IDs, used for the EKS control plane | null |
| private_subnet_ids | Private subnet IDs, used for the EKS node group and the MongoDB members | null |
| eks_cluster | EKS cluster name | null |
| eks_cluster_version | Kubernetes version for EKS | 1.29 |
| eks_cluster_sg_id | EKS cluster security group ID | null |
| eks_node_role_arn | IAM role ARN for EKS nodes | null |
| eks_node_max_capacity | Maximum EKS node count | 1 |
| eks_node_min_capacity | Minimum EKS node count | 1 |
| eks_node_desired_capacity | Desired EKS node count | 1 |
| eks_node_disksize | Disk size for EKS nodes (GB) | 25 |
| eks_node_instance_types | EC2 instance types for EKS nodes | ["t3.medium", "t3.large"] |
| eks_node_ami_type | AMI type for EKS nodes | AL2_x86_64 |
| mongodb_num_of_replicas | MongoDB replica count | 3 |
| mongodb_ami | MongoDB node AMI ID | null |
| mongodb_ami_filter | MongoDB AMI filter criteria | null |
| mongodb_ami_owner | MongoDB AMI owner ID | null |
| mongodb_username | MongoDB admin username | null |
| mongodb_password | MongoDB admin password | null |
| mongodb_instance_type | MongoDB compute instance type | t3.micro |
| mongodb_disksize | MongoDB node disk size (GB) | 20 |
| mongodb_volume_size | MongoDB data volume size (GB) | 100 |
| mongodb_cluster | MongoDB cluster name | null |

## Dependencies

### Substacks
- [config0-hub:::mongodb::mongodb_replica_on_ec2](https://api-app.config0.com/web_api/v1.0/stacks/config0-hub/mongodb_replica_on_ec2)
- [config0-hub:::aws_eks::aws_eks](https://api-app.config0.com/web_api/v1.0/stacks/config0-hub/aws_eks)

### Execgroups
None

### Scripts
None

## License
<pre>
Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.
</pre>