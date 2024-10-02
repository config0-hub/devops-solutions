class Main(newSchedStack):

    def __init__(self, stackargs):

        newSchedStack.__init__(self, stackargs)

        # Add default variables
        self.parse.add_required(key="codebuild_name",
                                types="str")

        self.parse.add_required(key="git_repo",
                                types="str")

        self.parse.add_required(key="git_url",
                                types="str")

        self.parse.add_required(key="project_id",
                                types="str")

        self.parse.add_optional(key="slack_channel",
                                types="str")

        self.parse.add_optional(key="trigger_id",
                                types="str",
                                default="_random")

        self.parse.add_optional(key="privileged_mode",
                                types="bool",
                                default="true")

        self.parse.add_optional(key="image_type",
                                types="str",
                                default="LINUX_CONTAINER")

        self.parse.add_optional(key="build_image",
                                types="str",
                                default="aws/codebuild/standard:5.0")

        self.parse.add_optional(key="build_timeout",
                                types="int",
                                default="444")

        self.parse.add_optional(key="compute_type",
                                types="str",
                                default="BUILD_GENERAL1_SMALL")

        self.parse.add_optional(key="aws_default_region",
                                types="str",
                                default="us-west-1")

        self.parse.add_optional(key="cloud_tags_hash",
                                types="str")

        self.parse.add_optional(key="bucket_acl",
                                types="str",
                                default="private")

        self.parse.add_optional(key="bucket_expire_days",
                                types="int",
                                default="1")

        self.parse.add_optional(key="subnet_ids",
                                default="null")

        self.parse.add_optional(key="vpc_id",
                                default="null",
                                types="str")

        self.parse.add_required(key="security_group_id",
                                default="null",
                                types="str")

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
