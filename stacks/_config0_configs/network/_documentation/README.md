# AWS Network Infrastructure Stack

## Description

This stack creates a complete AWS network infrastructure including a VPC, network variables set, and NAT instance. It's designed to set up the networking foundation needed for cloud deployments in AWS environments.

## Variables

### Required Variables

| Name | Description | Default |
|------|-------------|---------|
| env_name | Configuration for env name | |

### Optional Variables

| Name | Description | Default |
|------|-------------|---------|
| aws_default_region | Default AWS region | eu-west-1 |
| cloud_tags_hash | Resource tags for cloud provider | |
| vars_set_arguments_hash | 99checkme99 Arguments hash used for variable set creation | |
| vars_set_labels_hash | 99checkme99 Labels hash used for variable set creation | |
| vpc_id | VPC network identifier | null |
| public_subnet_ids | Public subnet IDs | |
| private_route_table_id | Private route table ID | |
| nat_instance_types | NAT instance compute types | t3.nano,t3a.nano |
| nat_cidr_ingress_accept | Allowed CIDR blocks for NAT | 0.0.0.0/0 |

## Features

- Creates a VPC optimized for AWS deployments
- Establishes network variable sets for configuration reuse
- Deploys NAT instances for outbound connectivity from private subnets
- Supports EKS cluster deployments
- Configurable NAT instance types and security settings

## Dependencies

### Substacks

- [config0-publish:::aws_vpc_simple](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/aws_vpc_simple)
- [config0-publish:::network_vars_set](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/network_vars_set)
- [config0-publish:::aws_nat_inst_vpc](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/aws_nat_inst_vpc)

## License

Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.