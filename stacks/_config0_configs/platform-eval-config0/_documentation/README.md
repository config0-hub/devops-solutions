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
- [config0-publish:::aws_vpc_simple](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/stacks/config0-publish/aws_vpc_simple/default)
- [config0-publish:::network_vars_set](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/stacks/config0-publish/network_vars_set/default)
- [config0-publish:::setup_iac_ci](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/stacks/config0-publish/setup_iac_ci/default)
- [config0-publish:::register_repo_iac_ci](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/stacks/config0-publish/register_repo_iac_ci/default)
- [config0-publish:::add_iac_ci](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/stacks/config0-publish/add_iac_ci/default)
- [config0-publish:::setup_codebuild_ci](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/stacks/config0-publish/setup_codebuild_ci/default)
- [config0-publish:::add_codebuild_ci](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/stacks/config0-publish/add_codebuild_ci/default)
- [config0-publish:::aws_nat_inst_vpc](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/stacks/config0-publish/aws_nat_inst_vpc/default)
- [config0-publish:::aws_nat_vpc](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/stacks/config0-publish/aws_nat_vpc/default)
- [config0-publish:::aws_rds](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/stacks/config0-publish/aws_rds/default)
- [config0-publish:::mongodb_replica_on_ec2](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/stacks/config0-publish/mongodb_replica_on_ec2/default)
- [config0-publish:::kafka_on_ec2](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/stacks/config0-publish/kafka_on_ec2/default)
- [config0-publish:::aws_eks](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/stacks/config0-publish/aws_eks/default)
- [config0-publish:::jenkins_on_do](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/stacks/config0-publish/jenkins_on_do/default)
- [config0-publish:::doks](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/stacks/config0-publish/doks/default)
- [config0-publish:::check_drift_resources](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/stacks/config0-publish/check_drift_resources/default)
- [config0-publish:::env_sql](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/stacks/config0-publish/env_sql/default)
- [config0-publish:::env_nosql](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/stacks/config0-publish/env_nosql/default)
- [config0-publish:::env_streaming](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/stacks/config0-publish/env_streaming/default)

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