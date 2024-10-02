class Main(newSchedStack):

    def __init__(self, stackargs):

        newSchedStack.__init__(self, stackargs)

        self.parse.add_required(key="iac_ci_repo",
                                types="str")

        self.parse.add_required(key="branch",
                                types="str")

        # only supporting terraform
        self.parse.add_required(key="source_method",
                                types="str",
                                default="terraform")

        self.parse.add_optional(key="iac_ci_folder",
                                types="str",
                                default="null")

        # Add substack
        self.stack.add_substack('config0-publish:::aws_codebuild')
        self.stack.add_substack('config0-publish:::aws_dynamodb_item','dynamodb_item')

        self.stack.init_substacks()

    def _get_dynamodb_item(self):

        _id = self.stack.get_hash(f'iac_ci.{self.stack.trigger_id}.{self.stack.branch}')

        item = {
            "_id": {"S": _id},
            "git_repo": {"S": str(self.stack.iac_ci_repo)},
            "trigger_id": {"S": str(self.stack.trigger_id)},
            "cluster": {"S": str(self.stack.cluster)},
            "project": {"S": str(self.stack.cluster)},
            "run_title": {"S": f'{str(self.stack.cluster)}-iac-ci'},
            "source_method": {"S": str(self.stack.source_method)}
        }

        if self.stack.get_attr("schedule_id"):
            item["schedule_id"] = {"S": str(self.stack.schedule_id)}

        if self.stack.get_attr("project_id"):
            item["project_id"] = {"S": str(self.stack.project_id)}

        if self.stack.get_attr("job_instance_id"):
            item["job_instance_id"] = {"S": str(self.stack.job_instance_id)}

        return self.stack.b64_encode(item)

    def run_setup(self):

        self.stack.init_variables()
        self.stack.verify_variables()
        self.stack.set_parallel()

        return self._token()

    def run(self):

        self.stack.unset_parallel(sched_init=True)
        self.add_job("setup")

        return self.finalize_jobs()

    def schedule(self):

        sched = self.new_schedule()
        sched.job = "setup"
        sched.archive.timeout = 1800
        sched.archive.timewait = 120
        sched.automation_phase = "continuous_delivery"
        sched.human_description = "Setup Basic for Codebuild"
        sched.conditions.retries = 1
        sched.on_success = ["connect_repo"]
        self.add_schedule()

        sched = self.new_schedule()
        sched.job = "connect_repo"
        sched.archive.timeout = 1800
        sched.archive.timewait = 120
        sched.automation_phase = "continuous_delivery"
        sched.human_description = "Add configurations to DynamoDb"
        sched.on_success = ["ssm"]
        self.add_schedule()

        sched = self.new_schedule()
        sched.job = "ssm"
        sched.archive.timeout = 1800
        sched.archive.timewait = 120
        sched.automation_phase = "continuous_delivery"
        sched.human_description = "Upload deploy key to ssm"
        sched.on_success = ["codebuild"]
        self.add_schedule()

        sched = self.new_schedule()
        sched.job = "codebuild"
        sched.archive.timeout = 1800
        sched.archive.timewait = 120
        sched.automation_phase = "continuous_delivery"
        sched.human_description = "Create Codebuild Project"
        self.add_schedule()

        return self.get_schedules()
