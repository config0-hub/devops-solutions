class Main(newSchedStack):

    def __init__(self, stackargs):

        newSchedStack.__init__(self, stackargs)

        self.parse.add_required(key="iac_ci_repo",
                                types="str")

        self.parse.add_required(key="branch",
                                types="str")

        self.parse.add_optional(key="iac_ci_folder",
                                types="str",
                                default="null")

        #stack.set_variable("iac_ci_folder",
        #                   f'{stack.project_name}/{stack.stateful_id}')

        # Add substack
        self.stack.add_substack('config0-publish:::aws_codebuild')

        self.stack.init_substacks()

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
