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

    # eks
    stack.parse.add_required(key="vpc_id",
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

    # add substack
    stack.add_substack("config0-publish:::aws_rds")
    stack.add_substack("config0-publish:::aws_eks")

    # initialize
    stack.init_variables()
    stack.init_execgroups()
    stack.init_substacks()

    # we can do both rds and eks in parallel
    stack.set_parallel()

    # configure rds_name
    rds_name = f'{stack.env_name}-rds'

    arguments = {
        "aws_default_region": stack.aws_default_region,
        "sg_id": stack.db_sg_id,
        "subnet_ids": stack.private_subnet_ids,
        "allocated_storage": stack.db_allocated_storage,
        "engine": stack.db_engine,
        "engine_version": stack.db_engine_version,
        "instance_class": stack.db_instance_class,
        "storage_type": stack.db_storage_type,
        "publicly_accessible": False,
        "storage_encrypted": True,
        "cloud_tags_hash": stack.cloud_tags_hash,
        "rds_name": rds_name,
    }
    
    if stack.db_multi_az:
        arguments["multi_az"] = stack.db_multi_az

    if stack.db_master_username:
        arguments["master_username"] = stack.db_master_username

    if stack.db_master_password:
        arguments["master_password"] = stack.db_master_password

    inputargs = {
        "arguments": arguments,
        "automation_phase": "infrastructure",
        "human_description": f'create rds "{rds_name}"'
    }

    stack.aws_rds.insert(display=True,
                         **inputargs)

    # eks
    eks_cluster = f'{stack.env_name}-eks'

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
        "eks_cluster": eks_cluster,
    }

    if stack.eks_cluster_sg_id:
        arguments["eks_cluster_sg_id"] = stack.eks_cluster_sg_id

    inputargs = {
        "arguments": arguments,
        "automation_phase": "infrastructure",
        "human_description": f'create eks cluster "{eks_cluster}"'
    }

    stack.aws_eks.insert(display=True,
                         **inputargs)

    return stack.get_results()