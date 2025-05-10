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

    stack.parse.add_optional(key="private_subnet_ids",
                             default="null",
                             types="str")

    stack.parse.add_required(key="vpc_id",
                             types="str")

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

    # mongodb
    stack.parse.add_required(key="bastion_sg_id",
                             default="null")

    stack.parse.add_required(key="bastion_subnet_ids",
                             default="null")

    stack.parse.add_optional(key="bastion_ami",
                             default="null")

    stack.parse.add_optional(key="bastion_ami_filter",
                             default="null")

    stack.parse.add_optional(key="bastion_ami_owner",
                             default="null")

    stack.parse.add_required(key="mongodb_num_of_replicas",
                             types="int",
                             default="3")

    stack.parse.add_optional(key="mongodb_ami",
                             types="str",
                             default="null")

    stack.parse.add_optional(key="mongodb_ami_filter",
                             types="str",
                             default="null")

    stack.parse.add_optional(key="mongodb_ami_owner",
                             default="null")

    stack.parse.add_optional(key="mongodb_username",
                             types="str",
                             default="null")

    stack.parse.add_optional(key="mongodb_password",
                             types="str",
                             default="null")

    stack.parse.add_required(key="db_sg_id",
                             default="null")

    stack.parse.add_optional(key="mongodb_instance_type",
                             types="str",
                             default="t3.micro")

    stack.parse.add_optional(key="mongodb_disksize",
                             types="int",
                             default="20")

    stack.parse.add_optional(key="mongodb_volume_size",
                             types="int",
                             default=100)

    stack.parse.add_optional(key="mongodb_cluster",
                             types="str",
                             default="null")

    # add substack
    stack.add_substack("config0-publish:::mongodb_replica_on_ec2")
    stack.add_substack("config0-publish:::aws_eks")

    # initialize
    stack.init_variables()
    stack.init_substacks()

    # we can do both db and eks in parallel
    stack.set_parallel()

    # configure db
    if not stack.get_attr("mongodb_cluster"):
        stack.set_variable("mongodb_cluster",
                           f"{stack.env_name}-mongodb")

    arguments = {
        "aws_default_region": stack.aws_default_region,
        "mongodb_cluster": stack.mongodb_cluster,
        "vpc_id": stack.vpc_id,
        "subnet_ids": stack.public_subnet_ids,
        "cloud_tags_hash": stack.cloud_tags_hash,
        "num_of_replicas": stack.mongodb_num_of_replicas,
        "ami": stack.mongodb_ami,
        "ami_filter": stack.mongodb_ami_filter,
        "ami_owner": stack.mongodb_ami_owner,
        "bastion_sg_id": stack.bastion_sg_id,
        "bastion_subnet_ids": stack.bastion_subnet_ids,
        "bastion_ami": stack.bastion_ami,
        "bastion_ami_filter": stack.bastion_ami_filter,
        "bastion_ami_owner": stack.bastion_ami_owner,
        "sg_id": stack.db_sg_id,
        "instance_type": stack.mongodb_instance_type,
        "disksize": stack.mongodb_disksize,
        "volume_size": stack.mongodb_volume_size,
        "publish_to_saas": True
    }

    if stack.get_attr("mongodb_username"):
        arguments["mongodb_username"] = stack.mongodb_username

    if stack.get_attr("mongodb_password"):
        arguments["mongodb_password"] = stack.mongodb_password

    inputargs = {
        "arguments": arguments,
        "automation_phase": "infrastructure",
        "human_description": f'create mongodb_cluster "{stack.mongodb_cluster}"'
    }

    stack.mongodb_replica_on_ec2.insert(display=True,
                                        **inputargs)

    # eks
    if not stack.get_attr("eks_cluster"):
        stack.set_variable("eks_cluster",
                           f"{stack.env_name}-eks")

    arguments = {
        "aws_default_region": stack.aws_default_region,
        "vpc_id": stack.vpc_id,
        "eks_cluster_version": stack.eks_cluster_version,
        "eks_cluster_subnet_ids": stack.public_subnet_ids,
        "eks_node_group_subnet_ids": stack.private_subnet_ids,
        "eks_node_role_arn": stack.eks_node_role_arn,
        "eks_node_max_capacity": stack.eks_node_max_capacity,
        "eks_node_min_capacity": stack.eks_node_min_capacity,
        "eks_node_desired_capacity": stack.eks_node_desired_capacity,
        "eks_node_disksize": stack.eks_node_disksize,
        "eks_node_instance_types": stack.eks_node_instance_types,
        "eks_node_ami_type": stack.eks_node_ami_type,
        "cloud_tags_hash": stack.cloud_tags_hash,
        "eks_cluster": stack.eks_cluster,
    }

    if stack.eks_cluster_sg_id:
        arguments["eks_cluster_sg_id"] = stack.eks_cluster_sg_id

    inputargs = {
        "arguments": arguments,
        "automation_phase": "infrastructure",
        "human_description": f'create eks cluster "{stack.eks_cluster}"'
    }

    stack.aws_eks.insert(display=True,
                         **inputargs)

    return stack.get_results()