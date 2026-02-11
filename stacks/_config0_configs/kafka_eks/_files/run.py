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

class Main(newSchedStack):

    def __init__(self, stackargs):
        newSchedStack.__init__(self, stackargs)

        # General
        self.parse.add_optional(key="aws_default_region", 
                               default="eu-west-1", 
                               types="str")
        
        self.parse.add_required(key="env_name", 
                               types="str")
        
        self.parse.add_optional(key="cloud_tags_hash", 
                               types="str")
        
        self.parse.add_optional(key="public_subnet_ids", 
                               default="null", 
                               types="str")
        
        self.parse.add_optional(key="private_subnet_ids", 
                               default="null", 
                               types="str")
        
        self.parse.add_required(key="vpc_id", 
                               types="str")

        # EKS
        self.parse.add_optional(key="eks_cluster", 
                               default="null", 
                               types="str")
        
        self.parse.add_optional(key="eks_cluster_version", 
                               types="str", 
                               default="1.29")
        
        self.parse.add_optional(key="eks_cluster_sg_id", 
                               default="null", 
                               types="str")
        
        self.parse.add_optional(key="eks_node_role_arn", 
                               default="null", 
                               types="str")
        
        self.parse.add_optional(key="eks_node_max_capacity", 
                               default=1, 
                               types="int")
        
        self.parse.add_optional(key="eks_node_min_capacity", 
                               default=1, 
                               types="int")
        
        self.parse.add_optional(key="eks_node_desired_capacity", 
                               default=1, 
                               types="int")
        
        self.parse.add_optional(key="eks_node_disksize", 
                               default=25, 
                               types="int")
        
        self.parse.add_optional(key="eks_node_instance_types", 
                               default=["t3.medium", "t3.large"], 
                               types="list")
        
        self.parse.add_optional(key="eks_node_ami_type", 
                               default="AL2_x86_64", 
                               types="str")

        # Kafka
        self.parse.add_required(key="bastion_sg_id", 
                               default="null")
        
        self.parse.add_required(key="bastion_subnet_ids", 
                               default="null")
        
        self.parse.add_optional(key="bastion_ami", 
                               default="null")
        
        self.parse.add_optional(key="bastion_ami_filter", 
                               default="null")
        
        self.parse.add_optional(key="bastion_ami_owner", 
                               default="null")
        
        self.parse.add_optional(key="kafka_ami", 
                               types="str", 
                               default="null")
        
        self.parse.add_optional(key="kafka_cluster", 
                               types="str", 
                               default="null")
        
        self.parse.add_optional(key="kafka_ami_filter", 
                               types="str", 
                               default="null")
        
        self.parse.add_optional(key="kafka_ami_owner", 
                               default="null")
        
        self.parse.add_optional(key="kafka_instance_type", 
                               types="str", 
                               default="t3.micro")
        
        self.parse.add_optional(key="kafka_disksize", 
                               types="int", 
                               default="20")
        
        self.parse.add_required(key="kafka_num_of_zookeeper", 
                               types="int", 
                               default=1)
        
        self.parse.add_required(key="kafka_num_of_broker", 
                               types="int", 
                               default=1)
        
        self.parse.add_required(key="kafka_num_of_schema_registry", 
                               types="int", 
                               default=1)
        
        self.parse.add_required(key="kafka_num_of_connect", 
                               types="int", 
                               default=1)
        
        self.parse.add_required(key="kafka_num_of_rest", 
                               types="int", 
                               default=1)
        
        self.parse.add_required(key="kafka_num_of_ksql", 
                               types="int", 
                               default=1)
        
        self.parse.add_required(key="kafka_num_of_control_center", 
                               types="int", 
                               default=1)
        
        self.parse.add_required(key="db_sg_id", 
                               default="null")

        # Add substack
        self.stack.add_substack("config0-publish:::empty_stack")
        self.stack.add_substack("config0-publish:::kafka_on_ec2")
        self.stack.add_substack("config0-publish:::aws_eks")

        self.stack.init_substacks()

    def _set_vars(self):
        if not self.stack.get_attr("kafka_cluster"):
            self.stack.set_variable("kafka_cluster", 
                                   f"{self.stack.env_name}-kafka")

        if not self.stack.get_attr("eks_cluster"):
            self.stack.set_variable("eks_cluster", 
                                   f"{self.stack.env_name}-eks")

    def _kafka(self):
        arguments = {
            "aws_default_region": self.stack.aws_default_region,
            "kafka_cluster": self.stack.kafka_cluster,
            "subnet_ids": self.stack.public_subnet_ids,
            "cloud_tags_hash": self.stack.cloud_tags_hash,
            "ami": self.stack.kafka_ami,
            "ami_filter": self.stack.kafka_ami_filter,
            "ami_owner": self.stack.kafka_ami_owner,
            "bastion_sg_id": self.stack.bastion_sg_id,
            "bastion_subnet_ids": self.stack.bastion_subnet_ids,
            "bastion_ami": self.stack.bastion_ami,
            "bastion_ami_filter": self.stack.bastion_ami_filter,
            "bastion_ami_owner": self.stack.bastion_ami_owner,
            "sg_id": self.stack.db_sg_id,
            "instance_type": self.stack.kafka_instance_type,
            "num_of_zookeeper": self.stack.kafka_num_of_zookeeper,
            "num_of_broker": self.stack.kafka_num_of_broker,
            "num_of_schema_registry": self.stack.kafka_num_of_schema_registry,
            "num_of_connect": self.stack.kafka_num_of_connect,
            "num_of_rest": self.stack.kafka_num_of_rest,
            "num_of_ksql": self.stack.kafka_num_of_ksql,
            "num_of_control_center": self.stack.kafka_num_of_control_center,
            "disksize": self.stack.kafka_disksize,
            "publish_to_saas": True
        }

        inputargs = {
            "arguments": arguments,
            "automation_phase": "infrastructure",
            "human_description": f'create kafka_cluster "{self.stack.kafka_cluster}"'
        }

        return self.stack.kafka_on_ec2.insert(display=True, 
                                             **inputargs)

    def _eks(self):
        arguments = {
            "aws_default_region": self.stack.aws_default_region,
            "vpc_id": self.stack.vpc_id,
            "eks_cluster_version": self.stack.eks_cluster_version,
            "eks_cluster_subnet_ids": self.stack.public_subnet_ids,
            "eks_node_group_subnet_ids": self.stack.private_subnet_ids,
            "eks_node_role_arn": self.stack.eks_node_role_arn,
            "eks_node_max_capacity": self.stack.eks_node_max_capacity,
            "eks_node_min_capacity": self.stack.eks_node_min_capacity,
            "eks_node_desired_capacity": self.stack.eks_node_desired_capacity,
            "eks_node_disksize": self.stack.eks_node_disksize,
            "eks_node_instance_types": self.stack.eks_node_instance_types,
            "eks_node_ami_type": self.stack.eks_node_ami_type,
            "cloud_tags_hash": self.stack.cloud_tags_hash,
            "eks_cluster": self.stack.eks_cluster,
        }

        if self.stack.eks_cluster_sg_id:
            arguments["eks_cluster_sg_id"] = self.stack.eks_cluster_sg_id

        inputargs = {
            "arguments": arguments,
            "automation_phase": "infrastructure",
            "human_description": f'create eks cluster "{self.stack.eks_cluster}"'
        }

        return self.stack.aws_eks.insert(display=True, 
                                        **inputargs)

    def run_kafka_eks(self):
        self.stack.init_variables()
        self.stack.verify_variables()
        self._set_vars()

        self.stack.set_parallel()
        self._eks()
        self._kafka()

    def run(self):
        self.stack.unset_parallel(sched_init=True)
        self.add_job("kafka_eks")

        return self.finalize_jobs()

    def schedule(self):
        sched = self.new_schedule()
        sched.job = "kafka_eks"
        sched.archive.timeout = 2700
        sched.archive.timewait = 120
        sched.conditions.retries = 1
        sched.automation_phase = "infrastructure"
        sched.human_description = 'create kafka/eks'
        self.add_schedule()

        return self.get_schedules()