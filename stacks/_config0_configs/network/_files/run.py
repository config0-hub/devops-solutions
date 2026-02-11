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

        self.parse.add_optional(key="aws_default_region",
                                default="eu-west-1",
                                types="str")

        self.parse.add_optional(key="cloud_tags_hash",
                                types="str")

        self.parse.add_optional(key="vars_set_arguments_hash",
                                types="str")

        self.parse.add_optional(key="vars_set_labels_hash",
                                types="str")

        self.parse.add_required(key="env_name",
                                types="str")

        # nat instance vars
        self.parse.add_optional(key="vpc_id",
                                default="null",
                                types="str")

        self.parse.add_optional(key="public_subnet_ids",
                                types="str")

        self.parse.add_optional(key="private_route_table_id",
                                types="str")

        # sensible defaults
        self.parse.add_optional(key="nat_instance_types",
                                types="str",
                                default="t3.nano,t3a.nano")

        self.parse.add_optional(key="nat_cidr_ingress_accept",
                                types="str",
                                default="0.0.0.0/0")

        # add substack
        self.stack.add_substack("config0-publish:::aws_vpc_simple")
        self.stack.add_substack("config0-publish:::network_vars_set")
        self.stack.add_substack("config0-publish:::aws_nat_inst_vpc")

        self.stack.init_substacks()

    def _get_vpc_name(self):
        return f'{self.stack.env_name}-vpc'

    def _get_default_eks_cluster_name(self):
        return f'{self.stack.env_name}-eks'

    def _get_vars_set(self):
        return f'{self.stack.env_name}-network_vars_set'

    def _set_cloud_tag_hash(self):
        try:
            cloud_tags = self.stack.b64_decode(self.stack.cloud_tags_hash)
        except:
            cloud_tags = {}

        cloud_tags.update({
            "env_name": self.stack.env_name,
            "aws_default_region": self.stack.aws_default_region
        })

        return self.stack.b64_encode(cloud_tags)

    def run_vpc(self):
        self.stack.init_variables()
        self.stack.verify_variables()

        if self.stack.get_attr("eks_cluster"):
            eks_cluster = self.stack.eks_cluster
        else:
            eks_cluster = self._get_default_eks_cluster_name()  # default

        vpc_name = self._get_vpc_name()
        arguments = {
            "vpc_name": vpc_name,
            "eks_cluster": eks_cluster,
            "publish_to_saas": True,
            "cloud_tags_hash": self._set_cloud_tag_hash(),
            "aws_default_region": self.stack.aws_default_region
        }

        human_description = f'Create vpc "{vpc_name}"'

        inputargs = {
            "arguments": arguments,
            "automation_phase": "infrastructure",
            "human_description": human_description
        }

        return self.stack.aws_vpc_simple.insert(display=True, **inputargs)

    def run_network_vars_set(self):
        self.stack.init_variables()
        self.stack.verify_variables()

        arguments = {
            "evaluate": False,
            "vars_set_name": self._get_vars_set()
        }

        if self.stack.vars_set_arguments_hash:
            arguments["arguments_hash"] = self.stack.vars_set_arguments_hash

        if self.stack.vars_set_labels_hash:
            arguments["labels_hash"] = self.stack.vars_set_labels_hash

        human_description = f'Create network_vars_set "{self.stack.network_vars_set}"'

        inputargs = {
            "arguments": arguments,
            "automation_phase": "infrastructure",
            "human_description": human_description
        }

        return self.stack.network_vars_set.insert(display=True, **inputargs)

    def run_nat_instance(self):
        self.stack.init_variables()
        self.stack.verify_variables()

        for req_key in ["vpc_id", "public_subnet_ids", "private_route_table_id"]:
            if self.stack.get_attr(req_key):
                continue
            raise Exception(f'nat instance requires argument "{req_key}"')

        arguments = {
            "cloud_tags_hash": self._set_cloud_tag_hash(),
            "service_name": self.stack.env_name,
            "cidr_ingress_accept": self.stack.nat_cidr_ingress_accept,
            "instance_types": self.stack.nat_instance_types,
            "public_subnet_ids": self.stack.public_subnet_ids,
            "private_route_table_id": self.stack.private_route_table_id,
            "vpc_id": self.stack.vpc_id
        }

        human_description = f'Create natgw "{self.stack.env_name}"'

        inputargs = {
            "arguments": arguments,
            "automation_phase": "infrastructure",
            "human_description": human_description
        }

        return self.stack.aws_nat_inst_vpc.insert(display=True, **inputargs)

    def run(self):
        self.stack.unset_parallel()
        self.add_job("vpc")
        self.add_job("network_vars_set")
        self.add_job("nat_instance")

        return self.finalize_jobs()

    def schedule(self):
        sched = self.new_schedule()
        sched.job = "vpc"
        sched.archive.timeout = 1800
        sched.archive.timewait = 120
        sched.automation_phase = "infrastructure"
        sched.human_description = "Creates vpc"
        sched.conditions.retries = 1
        sched.on_success = ["network_vars_set"]
        self.add_schedule()

        sched = self.new_schedule()
        sched.job = "network_vars_set"
        sched.archive.timeout = 900
        sched.archive.timewait = 120
        sched.automation_phase = "infrastructure"
        sched.human_description = "Creates variable set"
        sched.on_success = ["nat_instance"]
        self.add_schedule()

        sched = self.new_schedule()
        sched.job = "nat_instance"
        sched.archive.timeout = 1200
        sched.archive.timewait = 120
        sched.automation_phase = "infrastructure"
        sched.human_description = 'Create nat instance'
        self.add_schedule()

        return self.get_schedules()