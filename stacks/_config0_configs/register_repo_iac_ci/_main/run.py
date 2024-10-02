class Main(newSchedStack):

    def __init__(self, stackargs):

        newSchedStack.__init__(self, stackargs)

        self.parse.add_required(key="app_name",
                                types="str",
                                default="iac-ci-config0")

        self.stack.add_substack('config0-publish:::github_webhook')
        self.stack.add_substack('config0-publish:::aws_dynamodb_item','dynamodb_item')
        self.stack.add_substack('config0-publish:::aws_ssm_param')
        self.stack.add_substack('config0-publish:::new_github_ssh_key')

        self.stack.init_substacks()

    def _get_token(self):

        _lookup = {"must_be_one": True,
                   "resource_type": "config0_token",
                   "provider": "config0",
                   "name": self.stack.app_name}

        return str(self.stack.get_resource(**_lookup)[0]["token"])

    def _token(self):
        return self.stack.create_token(name=self.stack.app_name)

    def _set_github_token(self):

        if self.stack.inputvars.get("github_token"):
            self.stack.set_variable("github_token",
                                    self.stack.inputvars["github_token"],
                                    types="str")
        elif self.stack.inputvars.get("github_token_hash"):
            self.stack.set_variable("github_token",
                                    self.stack.b64_encode(self.stack.inputvars["github_token_hash"]),
                                    types="str")

        if not self.stack.get_attr("github_token"):
            raise Exception("github token is needed to create ssh deploy key")

    def _set_buckets(self):

        self.stack.set_variable("lambda_bucket",
                                self.stack.bucket_names["lambda"])

        self.stack.set_variable("remote_stateful_bucket",
                                self.stack.bucket_names["stateful"])

        self.stack.set_variable("tmp_bucket",
                                self.stack.bucket_names["tmp"])

    def _set_misc(self):

        # we need to hardwire to us-east-1 since
        # the existing config0 workers ("config0-iac")
        # are by default deployed to us-east-1
        self.stack.set_variable("aws_default_region",
                                "us-east-1")

        _secret = self.stack.get_hash(f'{self.stack.tmp_bucket}.{self.stack.lambda_bucket}.{self.stack.remote_stateful_bucket}')

        self.stack.set_variable("trigger_id",
                                self.stack.get_hash(f'{_secret}.{self.stack.app_name}'))

        self.stack.set_variable("secret",_secret)
        self.stack.set_variable("dynamodb_name_runs",f"{self.stack.app_name}-runs")
        self.stack.set_variable("dynamodb_name_settings",f"{self.stack.app_name}-settings")

    def _set_iac_ci_repo(self):

        self.stack.set_variable("iac_ci_repo",
                                self.stack.inputvars.get("iac_ci_repo"))

        if not self.stack.iac_ci_repo:
            raise Exception("cannot set up iac ci - missing a repository")

        self.stack.set_variable("iac_ci_github_token",
                                self.stack.inputvars.get("iac_ci_github_token"))

        if not self.stack.iac_ci_github_token:
            raise Exception("cannot set up iac ci - token missing")

        self.stack.set_variable("ssm_iac_ci_github_token",
                                f"/{self.stack.app_name}/config0/iac_ci_github_token")

    def _set_slack_webhook(self):

        self.stack.set_variable("slack_webhook_hash",
                                self.stack.inputvars.get("slack_webhook_hash"),
                                types="str")

        if self.stack.get_attr("slack_webhook_hash"):
            self.stack.set_variable("ssm_slack_webhook_hash",
                                    f"/{self.stack.app_name}/config0/slack_webhook_hash")
        else:
            self.stack.set_variable("ssm_slack_webhook_hash",None)

    def _set_infracost(self):

        if self.stack.inputvars.get("infracost_api_key_hash"):
            self.stack.set_variable("infracost_api_key",self.stack.b64_decode(self.stack.inputvars["infracost_api_key_hash"]))
        elif self.stack.inputvars.get("infracost_api_key"):
            self.stack.set_variable("infracost_api_key",self.stack.inputvars["infracost_api_key"])
        else:
            self.stack.set_variable("infracost_api_key",None)

        if self.stack.get_attr("infracost_api_key"):
            self.stack.set_variable("ssm_infracost_api_key",
                                    f"/{self.stack.app_name}/config0/infracost_api_key")
        else:
            self.stack.set_variable("ssm_infracost_api_key",None)

    def _get_api_url(self):

        import os

        _lookup = {
            "must_be_one": True,
            "resource_type": "apigateway_restapi_lambda",
            "provider": "aws",
            "name": self.stack.app_name
        }

        results = self.stack.get_resource(**_lookup)[0]

        return os.path.join(str(results["base_url"]), str(self.stack.trigger_id))

    def _init_common(self):

        self._set_github_token()
        self._set_buckets()
        self._set_iac_ci_repo()
        self._set_slack_webhook()
        self._set_infracost()
        self._set_misc()

    def _webhook(self):

        arguments = {
            "aws_default_region": self.stack.aws_default_region,
            "repo": self.stack.iac_ci_repo,
            "secret": self.stack.secret,
            "name": self.stack.app_name,
            "url": self._get_api_url()
        }

        inputargs = {
            "arguments": arguments,
            "automation_phase": "continuous_delivery",
            "human_description": f'Create webhook {arguments["name"]}'
        }

        return self.stack.github_webhook.insert(display=True, **inputargs)

    def _get_ssh_private_key(self):

        _lookup = {
            "must_be_one": True,
            "resource_type": "ssh_key_pair",
            "provider": "config0",
            "name": self.stack.app_name
            }

        return self.stack.get_resource(decrypt=True,
                                       **_lookup)[0]["private_key"]

    def _sshdeploy(self):

        arguments = {
            "key_name": self.stack.app_name,
            "aws_default_region": self.stack.aws_default_region,
            "repo": self.stack.iac_ci_repo
        }

        inputargs = {
            "arguments": arguments,
            "automation_phase": "continuous_delivery",
            "human_description": f'Create deploy key "{self.stack.app_name}"'
        }

        return self.stack.new_github_ssh_key.insert(display=True,
                                                    **inputargs)

    def _ssm(self):

        self._add_ssm_callback_token()
        self._add_ssm_ssh_key()
        self._add_ssm_iac_ci_github_token()
        self._add_ssm_slack()
        self._add_ssm_infracost()

    def _get_dynamodb_item(self):

        item = {
            "_id": {"S": str(self.stack.trigger_id)},
            "git_repo": {"S": str(self.stack.iac_ci_repo)},
            "trigger_id": {"S": str(self.stack.trigger_id)},
            "secret": {"S": str(self.stack.secret)},
            "saas_env": {"S": str(self.stack.saas_env)},
            "run_title": {"S": str(self.stack.run_title)},
            "user_endpoint": {"S": str(self.stack.get_user_endpt())},
            "ssm_callback_token": {"S": str(self.stack.ssm_callback_token)},
            "ssm_ssh_key": {"S": str(self.stack.ssm_ssh_key)},
            "ssm_iac_ci_github_token": {"S": str(self.stack.ssm_iac_ci_github_token)}
        }

        # additional optional credentials
        if self.stack.get_attr("ssm_infracost_api_key"):
            item["ssm_infracost_api_key"]={
                "S": str(self.stack.ssm_infracost_api_key)
            }

        if self.stack.get_attr("ssm_slack_webhook_hash"):
            item["ssm_slack_webhook_hash"] = {
                "S": str(self.stack.ssm_slack_webhook_hash)
            }

        # config0 settings
        if self.stack.get_attr("sched_name"):
            item["sched_name"] = {"S": str(self.stack.sched_name)}
            item["job_name"] = {"S": str(self.stack.sched_name)}

        if self.stack.get_attr("schedule_id"):
            item["schedule_id"] = {"S": str(self.stack.schedule_id)}

        if self.stack.get_attr("project_id"):
            item["project_id"] = {"S": str(self.stack.project_id)}

        if self.stack.get_attr("job_instance_id"):
            item["job_instance_id"] = {"S": str(self.stack.job_instance_id)}

        if self.stack.get_attr("cluster"):
            item["cluster"] = {"S": str(self.stack.cluster)}
            item["project"] = {"S": str(self.stack.cluster)}

        return self.stack.b64_encode(item)

    def _add_ssm_iac_ci_github_token(self):

        if not self.stack.get_attr("ssm_iac_ci_github_token"):
            return

        arguments={
            "ssm_key": self.stack.ssm_iac_ci_github_token,
            "ssm_value": self.stack.iac_ci_github_token,
            "aws_default_region": self.stack.aws_default_region
        }

        inputargs={
            "arguments": arguments,
            "automation_phase": "continuous_delivery",
            "human_description": "Repo IaC CI Token to ssm"
        }

        self.stack.aws_ssm_param.insert(display=True,**inputargs)

    def _add_ssm_infracost(self):

        if not self.stack.get_attr("ssm_infracost_api_key"):
            return

        arguments={
            "ssm_key": self.stack.ssm_infracost_api_key,
            "ssm_value": self.stack.infracost_api_key,
            "aws_default_region": self.stack.aws_default_region
        }

        inputargs={"arguments": arguments,
                   "automation_phase": "continuous_delivery",
                   "human_description": "Infracost token to ssm"}

        self.stack.aws_ssm_param.insert(display=True,**inputargs)

    def _add_ssm_callback_token(self):

        self.stack.set_variable("ssm_callback_token",
                                f"/{self.stack.app_name}/config0/callback_token")

        # add config0 token
        arguments = {
            "ssm_key": self.stack.ssm_callback_token,
            "ssm_value": self._get_token(),
            "aws_default_region": self.stack.aws_default_region
        }

        inputargs = {"arguments": arguments,
                     "automation_phase": "continuous_delivery",
                     "human_description": "Config0 callback token to ssm"}

        self.stack.aws_ssm_param.insert(display=True, **inputargs)

    def _add_ssm_ssh_key(self):

        self.stack.set_variable("ssm_ssh_key",
                                f"/{self.stack.app_name}/config0/sshkeys/private")

        # add ssh key
        arguments = {
            "ssm_key": self.stack.ssm_ssh_key,
            "ssm_value": self._get_ssh_private_key(),
            "aws_default_region": self.stack.aws_default_region
        }

        inputargs = {"arguments": arguments,
                     "automation_phase": "continuous_delivery",
                     "human_description": "Upload private ssh key to ssm"}

        self.stack.aws_ssm_param.insert(display=True, **inputargs)

    def _add_ssm_slack(self):

        if not self.stack.get_attr("slack_webhook_hash"):
            return

        arguments = {"ssm_key": self.stack.ssm_slack_webhook_hash,
                     "ssm_value": self.stack.slack_webhook_hash,
                     "aws_default_region": self.stack.aws_default_region}

        inputargs = {"arguments": arguments,
                     "automation_phase": "continuous_delivery",
                     "human_description": "Upload slack webhook url to ssm"}

        self.stack.aws_ssm_param.insert(display=True, **inputargs)

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
            "human_description": f'Add setting item for iac ci {self.stack.app_name}'
        }

        return self.stack.dynamodb_item.insert(display=True,
                                               **inputargs)

    def _add_iac_ci_to_db(self):

        values = {
            "_id": self.stack.trigger_id,
            "trigger_id": self.stack.trigger_id,
            "source_method": "stack",
            "resource_type": "iac_ci"
        }

        _keys_to_add = [
            "schedule_id",
            "job_instance_id",
            "run_id",
            "project_id"
        ]

        inputargs = {}

        for _key in _keys_to_add:
            if not self.stack.get_attr(_key):
                continue
            values[_key] = self.stack.get_attr(_key)
            inputargs[_key] = self.stack.get_attr(_key)

        values["name"] = self.stack.app_name
        inputargs["name"] = self.stack.app_name

        self.stack.add_resource(values=values,
                                **inputargs)

    def run_connect_repo(self):

        self.stack.init_variables()
        self.stack.verify_variables()
        self._init_common()
        self.stack.set_parallel()

        self._add_iac_ci_to_db()
        self._ssm()
        return self._dynamodb_item()

    def run_setup(self):

        self.stack.init_variables()
        self.stack.verify_variables()
        self._init_common()
        self.stack.set_parallel()

        self._webhook()
        self._sshdeploy()
        return self._token()

    def run(self):

        self.stack.unset_parallel(sched_init=True)
        self.add_job("setup")
        self.add_job("connect_repo")

        return self.finalize_jobs()

    def schedule(self):

        sched = self.new_schedule()
        sched.job = "setup"
        sched.archive.timeout = 1800
        sched.archive.timewait = 120
        sched.conditions.retries = 1
        sched.automation_phase = "infrastructure"
        sched.human_description = "Setup repo deploy key and token"
        sched.on_success = ["connect_repo"]
        self.add_schedule()

        sched = self.new_schedule()
        sched.job = "connect_repo"
        sched.archive.timeout = 1800
        sched.archive.timewait = 120
        sched.automation_phase = "continuous_delivery"
        sched.human_description = "Connect repo with api gateway"
        self.add_schedule()

        return self.get_schedules()