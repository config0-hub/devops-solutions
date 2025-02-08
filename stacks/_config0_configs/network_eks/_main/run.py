class Main(newSchedStack):

    def __init__(self,stackargs):

        newSchedStack.__init__(self,stackargs)

        # general
        self.parse.add_required(key="env_name",
                                types="str")

        self.parse.add_optional(key="cloud_tags_hash",
                                types="str")

        self.parse.add_optional(key="aws_default_region",
                                default="eu-west-1",
                                types="str")

        # variable set
        self.parse.add_optional(key="vars_set_labels_hash",
                                default='null',
                                types="str")

        self.parse.add_optional(key="vars_set_arguments_hash",
                                default='null',
                                types="str")

        self.parse.add_optional(key="vpc_id",
                                default="null",
                                types="str")

        self.parse.add_optional(key="public_subnet_ids",
                                default="null",
                                types="str")

        self.parse.add_optional(key="private_route_table_id",
                                default="null",
                                types="str")

        # nat instance
        self.parse.add_optional(key="nat_instance_types",
                                types="str",
                                default="t3.nano,t3a.nano")

        # eks
        self.parse.add_optional(key="eks_cluster_version",
                                types="str",
                                default="1.29")

        self.parse.add_optional(key="eks_cluster_subnet_ids",
                                default="null",
                                types="str")

        self.parse.add_optional(key="eks_cluster_sg_id",
                                default="null",
                                types="str")

        self.parse.add_optional(key="eks_node_group_subnet_ids",
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
                                default=["t3.medium","t3.large"],
                                types="list")

        self.parse.add_optional(key="eks_node_ami_type",
                                default="AL2_x86_64",
                                types="str")

        # add substack
        self.stack.add_substack("config0-publish:::network")
        self.stack.add_substack("config0-publish:::aws_eks")

        self.stack.init_substacks()

    def _get_eks_cluster_name(self):
        return f'{self.stack.env_name}-eks'

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

    def run_network(self):

        self.stack.init_variables()
        self.stack.verify_variables()

        arguments = {
            "env_name": self.stack.env_name,
            "eks_cluster": self._get_eks_cluster_name(),
            "vpc_id": self.stack.vpc_id,
            "public_subnet_ids": self.stack.public_subnet_ids,
            "private_route_table_id": self.stack.private_route_table_id,
            "vars_set_labels_hash": self.stack.vars_set_labels_hash,
            "vars_set_arguments_hash": self.stack.vars_set_arguments_hash,
            "cloud_tags_hash": self._set_cloud_tag_hash(),
            "aws_default_region": self.stack.aws_default_region,
            "nat_instance_types":self.stack.nat_instance_types,
            "nat_cidr_ingress_accept":"0.0.0.0/0"  # be opinionated with this
        }

        human_description = f'Create aws network for env "{self.stack.env_name}"'

        inputargs = {
            "arguments": arguments,
            "automation_phase": "infrastructure",
            "human_description": human_description
        }

        return self.stack.network.insert(display=True,
                                         **inputargs)

    def run_eks(self):

        self.stack.init_variables()
        self.stack.verify_variables()

        arguments = {
            "publish_to_saas": True,
            "aws_default_region": self.stack.aws_default_region,
            "cloud_tags_hash": self._set_cloud_tag_hash(),
            "vpc_id":self.stack.vpc_id,
            "eks_cluster": self._get_eks_cluster_name(),
            "eks_cluster_version": self.stack.eks_cluster_version,
            "eks_cluster_subnet_ids": self.stack.eks_cluster_subnet_ids,
            "eks_cluster_sg_id": self.stack.eks_cluster_sg_id,
            "eks_node_capacity_type": "ON_DEMAND",
            "eks_node_ami_type": self.stack.eks_node_ami_type,
            "eks_node_max_capacity": self.stack.eks_node_max_capacity,
            "eks_node_min_capacity": self.stack.eks_node_min_capacity,
            "eks_node_desired_capacity": self.stack.eks_node_desired_capacity,
            "eks_node_disksize": self.stack.eks_node_disksize,
            "eks_node_instance_types":self.stack.eks_node_instance_types,
            "eks_node_group_subnet_ids":self.stack.eks_node_group_subnet_ids,
            "eks_node_role_arn":self.stack.eks_node_role_arn
        }

        human_description = f'Create eks"'

        inputargs = {
            "arguments": arguments,
            "automation_phase": "infrastructure",
            "human_description": human_description
        }

        return self.stack.aws_eks.insert(display=True,
                                         **inputargs)


    def run(self):

        self.stack.unset_parallel()
        self.add_job("network")
        self.add_job("eks")

        return self.finalize_jobs()

    def schedule(self):

        sched = self.new_schedule()
        sched.job = "network"
        sched.archive.timeout = 1800
        sched.archive.timewait = 120
        sched.automation_phase = "infrastructure"
        sched.human_description = "Creates network"
        sched.conditions.retries = 1
        sched.on_success = ["eks"]
        self.add_schedule()

        sched = self.new_schedule()
        sched.job = "eks"
        sched.archive.timeout = 2700
        sched.archive.timewait = 300
        sched.automation_phase = "infrastructure"
        sched.human_description = 'Create Eks cluster'
        self.add_schedule()

        return self.get_schedules()

