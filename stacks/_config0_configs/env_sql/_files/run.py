"""
# Copyright (C) 2025 Gary Leong <gary@config0.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

def run(stackargs):

    # instantiate authoring stack
    stack = newStack(stackargs)

    # Parse and validate stack parameters
    # general
    stack.parse.add_optional(key="aws_default_region",
                             default="eu-west-1",
                             types="str")

    stack.parse.add_required(key="env_name",
                             types="str")

    stack.parse.add_optional(key="cloud_tags_hash",
                             types="str")

    stack.parse.add_optional(key="public_subnet_ids",
                             default="null",
                             types="str")

    stack.parse.add_optional(key="private_route_table_id",
                             default="null",
                             types="str")

    stack.parse.add_optional(key="private_subnet_ids",
                             default="null",
                             types="str")

    stack.parse.add_required(key="vpc_id",
                             types="str")

    # variable set
    stack.parse.add_optional(key="netvars_set_labels_hash",
                             default='null',
                             types="str")

    stack.parse.add_optional(key="netvars_set_arguments_hash",
                             default='null',
                             types="str")

    stack.parse.add_optional(key="nat_instance_types",
                             types="str",
                             default="t3.nano,t3a.nano")

    stack.parse.add_optional(key="nat_cidr_ingress_accept",
                             types="str",
                             default="0.0.0.0/0")

    # eks
    stack.parse.add_optional(key="eks_cluster",
                             default="null",
                             types="str")

    stack.parse.add_optional(key="eks_cluster_version",
                             types="str",
                             default="1.29")

    stack.parse.add_optional(key="eks_cluster_sg_id",
                             default="null",
                             types="str")

    stack.parse.add_optional(key="eks_node_role_arn",
                             default="null",
                             types="str")

    stack.parse.add_optional(key="eks_node_max_capacity",
                             default=1,
                             types="int")

    stack.parse.add_optional(key="eks_node_min_capacity",
                             default=1,
                             types="int")

    stack.parse.add_optional(key="eks_node_desired_capacity",
                             default=1,
                             types="int")

    stack.parse.add_optional(key="eks_node_disksize",
                             default=25,
                             types="int")

    stack.parse.add_optional(key="eks_node_instance_types",
                             default=["t3.medium", "t3.large"],
                             types="list")

    stack.parse.add_optional(key="eks_node_ami_type",
                             default="AL2_x86_64",
                             types="str")

    # rds
    stack.parse.add_required(key="db_sg_id",
                             types="str")

    stack.parse.add_optional(key="db_allocated_storage",
                             default=30,
                             types="int")

    stack.parse.add_optional(key="db_engine",
                             default="MySQL",
                             types="str")

    stack.parse.add_optional(key="db_engine_version",
                             default="8.0.35",
                             types="float")

    stack.parse.add_optional(key="db_instance_class",
                             default="db.t3.micro",
                             types="str")

    stack.parse.add_optional(key="db_multi_az",
                             default="false",
                             types="bool")

    stack.parse.add_optional(key="db_storage_type",
                             default="gp2",
                             types="str")

    stack.parse.add_optional(key="db_master_username",
                             default=None,
                             types="str")

    stack.parse.add_optional(key="db_master_password",
                             default=None,
                             types="str")

    # Initialize required infrastructure components
    stack.add_substack("config0-publish:::network")
    stack.add_substack("config0-publish:::rds_eks")

    # initialize
    stack.init_variables()
    stack.init_substacks()

    # configure network
    # Set up networking infrastructure including VPC, subnets, and routing
    arguments = {
        "env_name": stack.env_name,
        "cloud_tags_hash": stack.cloud_tags_hash,
        "aws_default_region": stack.aws_default_region,
        "vars_set_labels_hash": stack.netvars_set_labels_hash,
        "vars_set_arguments_hash": stack.netvars_set_arguments_hash,
        "vpc_id": stack.vpc_id,
        "public_subnet_ids": stack.public_subnet_ids,
        "private_route_table_id": stack.private_route_table_id,
        "nat_instance_types": stack.nat_instance_types,
        "nat_cidr_ingress_accept": stack.nat_cidr_ingress_accept
    }

    inputargs = {
        "arguments": arguments,
        "automation_phase": "infrastructure",
        "human_description": f'create 3tier env {stack.eks_cluster}'
    }

    stack.network.insert(display=True, **inputargs)

    # configure kafka & eks
    # Configure and deploy EKS cluster and associated resources
    if not stack.get_attr("kafka"):
        stack.set_variable("kafka", f'{stack.env_name}-kafka')

    # eks
    if not stack.get_attr("eks_cluster"):
        stack.set_variable("eks_cluster", f'{stack.env_name}-eks')

    arguments = {
        "aws_default_region": stack.aws_default_region,
        "vpc_id": stack.vpc_id,
        "env_name": stack.env_name,
        "cloud_tags_hash": stack.cloud_tags_hash,
        "db_sg_id": stack.db_sg_id,
        "public_subnet_ids": stack.public_subnet_ids,
        "private_subnet_ids": stack.private_subnet_ids,
        "db_allocated_storage": stack.db_allocated_storage,
        "db_engine": stack.db_engine,
        "db_engine_version": stack.db_engine_version,
        "db_instance_class": stack.db_instance_class,
        "db_storage_type": stack.db_storage_type,
        "publish_to_saas": True,
        "eks_cluster_version": stack.eks_cluster_version,
        "eks_node_role_arn": stack.eks_node_role_arn,
        "eks_node_max_capacity": stack.eks_node_max_capacity,
        "eks_node_min_capacity": stack.eks_node_min_capacity,
        "eks_node_desired_capacity": stack.eks_node_desired_capacity,
        "eks_node_disksize": stack.eks_node_disksize,
        "eks_node_instance_types": stack.eks_node_instance_types,
        "eks_node_ami_type": stack.eks_node_ami_type,
        "eks_cluster": stack.eks_cluster
    }

    if stack.db_multi_az:
        arguments["db_multi_az"] = stack.db_multi_az

    if stack.db_master_username:
        arguments["db_master_username"] = stack.db_master_username

    if stack.db_master_password:
        arguments["db_master_password"] = stack.db_master_password

    if stack.eks_cluster_sg_id:
        arguments["eks_cluster_sg_id"] = stack.eks_cluster_sg_id

    inputargs = {
        "arguments": arguments,
        "automation_phase": "infrastructure",
        "human_description": f'create kafka/eks cluster "{stack.eks_cluster}"'
    }

    stack.rds_eks.insert(display=True, **inputargs)

    return stack.get_results()