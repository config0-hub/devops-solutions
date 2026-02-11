# Kafka/EKS Deployment Stack

## Description
This stack deploys a combined infrastructure consisting of a Kafka cluster on EC2 instances and an Amazon EKS (Elastic Kubernetes Service) cluster. It handles the provisioning of both services in parallel, allowing for a comprehensive data streaming and container orchestration environment.

## Variables

### Required Variables

| Name | Description | Default |
|------|-------------|---------|
| env_name | Configuration for env name | &nbsp; |
| vpc_id | VPC network identifier | &nbsp; |
| bastion_sg_id | Bastion host security group | null |
| bastion_subnet_ids | Subnets for bastion hosts | null |
| db_sg_id | Database security group ID | null |

### Optional Variables

| Name | Description | Default |
|------|-------------|---------|
| aws_default_region | Default AWS region | eu-west-1 |
| cloud_tags_hash | Resource tags for cloud provider | &nbsp; |
| public_subnet_ids | Public subnet IDs | null |
| private_subnet_ids | Private subnet IDs | null |
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
| bastion_ami | Bastion host AMI ID | null |
| bastion_ami_filter | Bastion AMI filter criteria | null |
| bastion_ami_owner | Bastion AMI owner ID | null |
| kafka_ami | Kafka node AMI ID | null |
| kafka_cluster | Kafka cluster name | null |
| kafka_ami_filter | Kafka AMI filter criteria | null |
| kafka_ami_owner | Kafka AMI owner ID | null |
| kafka_instance_type | EC2 instance type for Kafka | t3.micro |
| kafka_disksize | Kafka node disk size (GB) | 20 |
| kafka_num_of_zookeeper | ZooKeeper node count | 1 |
| kafka_num_of_broker | Kafka broker count | 1 |
| kafka_num_of_schema_registry | Schema registry node count | 1 |
| kafka_num_of_connect | Kafka Connect node count | 1 |
| kafka_num_of_rest | Kafka REST proxy count | 1 |
| kafka_num_of_ksql | KSQL server count | 1 |
| kafka_num_of_control_center | Control Center node count | 1 |

## Dependencies

### Substacks
- [config0-publish:::empty_stack](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/empty_stack)
- [config0-publish:::kafka_on_ec2](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/kafka_on_ec2)
- [config0-publish:::aws_eks](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/aws_eks)

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