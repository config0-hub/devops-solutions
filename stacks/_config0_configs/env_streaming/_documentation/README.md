# 3-Tier Streaming Environment with Kafka and EKS

## Description
This stack creates a three-tier environment with Kafka and EKS clusters on AWS. It sets up the necessary networking components, security groups, and resources for a complete deployment.

## Variables

### Required Variables
| Name | Description | Default |
|------|-------------|---------|
| env_name | Configuration for env name | |
| vpc_id | VPC network identifier | |
| bastion_sg_id | Bastion host security group | |
| bastion_subnet_ids | Subnets for bastion hosts | |
| db_sg_id | Database security group ID | |
| kafka_num_of_zookeeper | ZooKeeper node count | 1 |
| kafka_num_of_broker | Kafka broker count | 1 |
| kafka_num_of_schema_registry | Schema registry node count | 1 |
| kafka_num_of_connect | Kafka Connect node count | 1 |
| kafka_num_of_rest | Kafka REST proxy count | 1 |
| kafka_num_of_ksql | KSQL server count | 1 |
| kafka_num_of_control_center | Control Center node count | 1 |

### Optional Variables
| Name | Description | Default |
|------|-------------|---------|
| aws_default_region | Default AWS region | eu-west-1 |
| cloud_tags_hash | Resource tags for cloud provider | |
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
| bastion_ami | Bastion host AMI ID | null |
| bastion_ami_filter | Bastion AMI filter criteria | null |
| bastion_ami_owner | Bastion AMI owner ID | null |
| kafka_ami | Kafka node AMI ID | null |
| kafka_cluster | Kafka cluster name | null |
| kafka_ami_filter | Kafka AMI filter criteria | null |
| kafka_ami_owner | Kafka AMI owner ID | null |
| kafka_instance_type | EC2 instance type for Kafka | t3.micro |
| kafka_disksize | Kafka node disk size (GB) | 20 |

## Features
- Automated deployment of a three-tier network architecture
- Kafka cluster with configurable node types and sizing
- EKS cluster with customizable node groups
- Integration with AWS networking and security components
- Support for custom AMIs and instance types
- Bastion host for executing Ansible and installing through private subnet

## Dependencies

### Substacks
- [config0-publish:::network](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/network)
- [config0-publish:::kafka_eks](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/kafka_eks)

## License
Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.