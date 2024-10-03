class Main(newSchedStack):

    def __init__(self, stackargs):

        newSchedStack.__init__(self, stackargs)

        self.parse.add_required(key="repo_name",
                                types="str")

        self.parse.add_required(key="branch",
                                types="str")

        # only supporting terraform to begin with
        self.parse.add_optional(key="source_method",
                                types="str",
                                default="terraform")

        self.parse.add_optional(key="subdir",
                                types="str",
                                default="null")

        # add substack
        self.stack.add_substack('config0-publish:::aws_codebuild')
        self.stack.add_substack('config0-publish:::aws_dynamodb_item','dynamodb_item')

        self.stack.init_substacks()

    def _set_registered_repo_info(self):

        _lookup = {
            "must_be_one": True,
            "resource_type": "iac_ci",
            "provider": "user_input",
            "iac_ci_repo": self.stack.repo_name}

        resource = self.stack.get_resource(**_lookup)[0]

        self.stack.set_variable("app_name",
                                str(resource["app_name"]))

        self.stack.set_variable("trigger_id",
                                str(resource["trigger_id"]))

        self.stack.set_variable("dynamodb_name_runs",f"{self.stack.app_name}-runs")
        self.stack.set_variable("dynamodb_name_settings",f"{self.stack.app_name}-settings")

    def _get_dynamodb_item(self):

        _id = self.stack.get_hash(f'iac_ci.{self.stack.trigger_id}.{self.stack.branch}')

        item = {
            "_id": {"S": _id},
            "repo_name": {"S": str(self.stack.repo_name)},
            "iac_ci_repo": {"S": str(self.stack.repo_name)},
            "trigger_id": {"S": str(self.stack.trigger_id)},
            "cluster": {"S": str(self.stack.cluster)},
            "project": {"S": str(self.stack.cluster)},
            "run_title": {"S": f'{str(self.stack.cluster)}-iac-ci'},
            "source_method": {"S": str(self.stack.source_method)},
            "type": {"S": "iac_setting"}
        }

        if self.stack.get_attr("schedule_id"):
            item["schedule_id"] = {"S": str(self.stack.schedule_id)}

        if self.stack.get_attr("project_id"):
            item["project_id"] = {"S": str(self.stack.project_id)}

        if self.stack.get_attr("job_instance_id"):
            item["job_instance_id"] = {"S": str(self.stack.job_instance_id)}

        if self.stack.subdir:
            item["iac_ci_folder"] = {"S": str(self.stack.subdir)}

        return self.stack.b64_encode(item)

    def _dynamodb_item(self):

        arguments = {
            "table_name": self.stack.dynamodb_name_settings,
            "hash_key": "_id",
            "item_hash": self._get_dynamodb_item(),
            "aws_default_region": self.stack.aws_default_region
        }

        inputargs = {
            "arguments": arguments,
            "automation_phase": "continuous_delivery",
            "human_description": f'Add setting item for iac ci {self.stack.cluster}-iac-ci'
        }

        return self.stack.dynamodb_item.insert(display=True,
                                               **inputargs)

    def run_setup(self):

        self.stack.init_variables()
        self.stack.verify_variables()

        # it must be us-east-1 since the existing
        # lambda/codebuild projects are created in us-east-1
        # by default
        self.stack.set_variable("aws_default_region",
                                "us-east-1")

        self._set_registered_repo_info()

        return self._dynamodb_item()

    def run(self):

        self.stack.unset_parallel(sched_init=True)
        self.add_job("setup")

        return self.finalize_jobs()

    def schedule(self):

        sched = self.new_schedule()
        sched.job = "setup"
        sched.archive.timeout = 900
        sched.archive.timewait = 120
        sched.automation_phase = "continuous_delivery"
        sched.human_description = "Setup IAC CI for existing IAC"
        sched.conditions.retries = 1
        self.add_schedule()

        return self.get_schedules()
