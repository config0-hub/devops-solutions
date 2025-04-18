# AWS Network Infrastructure Stack

## Description

This stack creates a complete AWS network infrastructure including a VPC, network variables set, and NAT instance. It's designed to set up the networking foundation needed for cloud deployments in AWS environments.

## Variables

### Required Variables

| Name | Description | Default |
|------|-------------|---------|
| env_name | Configuration for env name | &nbsp; |

### Optional Variables

| Name | Description | Default |
|------|-------------|---------|
| aws_default_region | Default AWS region | eu-west-1 |
| cloud_tags_hash | Resource tags for cloud provider | &nbsp; |
| vars_set_arguments_hash | Arguments hash used for variable set creation | &nbsp; |
| vars_set_labels_hash | Labels hash used for variable set creation | &nbsp; |
| vpc_id | VPC network identifier | null |
| public_subnet_ids | Public subnet IDs | &nbsp; |
| private_route_table_id | Private route table ID | &nbsp; |
| nat_instance_types | NAT instance compute types | t3.nano,t3a.nano |
| nat_cidr_ingress_accept | Allowed CIDR blocks for NAT | 0.0.0.0/0 |

## Dependencies

### Substacks

- [config0-publish:::aws_vpc_simple](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/stacks/config0-publish/aws_vpc_simple/default)
- [config0-publish:::network_vars_set](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/stacks/config0-publish/network_vars_set/default)
- [config0-publish:::aws_nat_inst_vpc](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/stacks/config0-publish/aws_nat_inst_vpc/default)

### Execgroups

- [config0-publish:::github::lambda_trigger_stepf](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/exec/groups/config0-publish/github/lambda_trigger_stepf/default)

### Shelloutconfigs

- [config0-publish:::terraform::resource_wrapper](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/shelloutconfigs/config0-publish/terraform/resource_wrapper/default)

## License
<pre>
Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.
</pre>