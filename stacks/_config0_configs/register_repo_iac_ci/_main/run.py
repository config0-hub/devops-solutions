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
    """
    The Main class extends newSchedStack to manage the configuration and deployment
    of infrastructure components related to a CI/CD pipeline, including GitHub webhooks,
    AWS resources, and various tokens.

    Attributes:
        stackargs: Arguments for initializing the stack.
    """

    def __init__(self, stackargs):
        """
        Initializes the Main class and sets up required parameters and substacks.

        Args:
            stackargs: Arguments for the stack initialization.
        """
        newSchedStack.__init__(self, stackargs)

        self.parse.add_required(key="app_name_iac", types="str", default="iac-ci")

        self.stack.add_substack('config0-publish:::github_webhook')
        self.stack.add_substack('config0-publish:::aws_dynamodb_item', 'dynamodb_item')
        self.stack.add_substack('config0-publish:::aws_ssm_param')
        self.stack.add_substack('config0-publish:::new_github_ssh_key')

        self.stack.init_substacks()

    def _get_token(self):
        """
        Retrieves the user's config0 token

        Returns:
            str: The retrieved token.
        """
        _lookup = {
            "must_be_one": True,
            "resource_type": "config0_token",
            "provider": "config0",
            "name": self.stack.app_name_iac
        }
        return str(self.stack.get_resource(**_lookup)[0]["token"])

    def _token(self):
        """
        Creates a new token

        Returns:
            str: The newly created token.
        """
        return self.stack.create_token(name=self.stack.app_name_iac)

    def _set_github_token(self):
        """
        Sets the GitHub token for the application from input variables.

        Raises:
            Exception: If no GitHub token is provided.
        """
        github_token = None

        if self.stack.inputvars.get("github_token"):
            github_token = self.stack.inputvars["github_token"],
        elif self.stack.inputvars.get("GITHUB_TOKEN"):
            github_token = self.stack.inputvars["GITHUB_TOKEN"],
        elif self.stack.inputvars.get("github_token_hash"):
            github_token = self.stack.b64_encode(self.stack.inputvars["github_token_hash"]),

        self.stack.set_variable("github_token",
                                github_token,
                                types="str")

        if not self.stack.get_attr("github_token"):
            raise Exception("github token is needed to create ssh deploy key")

    def _set_buckets(self):
        """
        Sets the bucket names in the stack for different purposes, such as Lambda and temporary storage.
        """
        self.stack.set_variable("lambda_bucket", self.stack.bucket_names["lambda"])
        self.stack.set_variable("remote_stateful_bucket", self.stack.bucket_names["stateful"])
        self.stack.set_variable("tmp_bucket", self.stack.bucket_names["tmp"])

    def _set_misc(self):
        """
        Sets miscellaneous variables including AWS region and DynamoDB table names.
        """
        # config0 workers (config0-iac) are by default only in us-esat-1
        self.stack.set_variable("aws_default_region", "us-east-1")

        # ref 453452643
        _secret = self.stack.get_hash(f'{self.stack.tmp_bucket}.{self.stack.lambda_bucket}.{self.stack.remote_stateful_bucket}')

        self.stack.set_variable("trigger_id",
                                self.stack.get_hash(f'{_secret}.{self.stack.app_name_iac}'))

        self.stack.set_variable("secret", _secret)
        self.stack.set_variable("dynamodb_name_runs", f"{self.stack.app_name_iac}-runs")
        self.stack.set_variable("dynamodb_name_settings", f"{self.stack.app_name_iac}-settings")

    def _set_iac_ci_repo(self):
        """
        Sets up the IaC CI repository and validates the required tokens.

        Raises:
            Exception: If the repository or GitHub token is missing.
        """
        self.stack.set_variable("iac_ci_repo", self.stack.inputvars.get("iac_ci_repo"))

        if not self.stack.iac_ci_repo:
            raise Exception("cannot set up iac ci - missing a repository")

        self.stack.set_variable("iac_ci_github_token",
                                self.stack.inputvars.get("iac_ci_github_token"))

        if not self.stack.iac_ci_github_token:
            raise Exception("cannot set up iac ci - github token missing")

        self.stack.set_variable("ssm_iac_ci_github_token",
                                f"/config0-iac/imported/{self.stack.app_name_iac}/{self.stack.iac_ci_repo}/iac_ci/github_token")

    def _set_slack_webhook(self):
        """
        Sets the Slack webhook hash from input variables.
        """
        slack_webhook_hash = None

        if self.stack.inputvars.get("slack_webhook_b64"):
            slack_webhook_hash = self.stack.inputvars.get("slack_webhook_b64")
        elif self.stack.inputvars.get("slack_webhook_hash"):
            slack_webhook_hash = self.stack.inputvars.get("slack_webhook_hash")

        self.stack.set_variable("slack_webhook_hash",
                                slack_webhook_hash,
                                tags="tf_sensitive",
                                types="str")

        self._set_slack_webhook_ssm()

    def _set_slack_webhook_ssm(self):
        """
        Sets the Slack webhook hash SSM parameter if it exists.
        """
        if self.stack.get_attr("slack_webhook_hash"):
            self.stack.set_variable("ssm_slack_webhook_hash",
                                    f"/config0-iac/imported/{self.stack.app_name_iac}/{self.stack.iac_ci_repo}/slack/webhook/url_hash")
        else:
            self.stack.set_variable("ssm_slack_webhook_hash", None)

    def _set_infracost(self):
        """
        Sets the Infracost API key from input variables and configures its SSM parameter.
        """
        if self.stack.inputvars.get("infracost_api_key_hash"):
            infracost_api_key = self.stack.b64_decode(self.stack.inputvars["infracost_api_key_hash"])
        elif self.stack.inputvars.get("infracost_api_key"):
            infracost_api_key = self.stack.inputvars["infracost_api_key"]
        else:
            infracost_api_key = None

        self.stack.set_variable("infracost_api_key", infracost_api_key)

        if self.stack.get_attr("infracost_api_key"):
            self.stack.set_variable("ssm_infracost_api_key",
                                    f"/config0-iac/imported/{self.stack.app_name_iac}/{self.stack.iac_ci_repo}/infracost/api_key")
        else:
            self.stack.set_variable("ssm_infracost_api_key", None)

    def _get_api_url(self):
        """
        Constructs and returns the API URL for the webhook

        Returns:
            str: The constructed API URL.
        """
        import os

        _lookup = {
            "must_be_one": True,
            "resource_type": "apigateway_restapi_lambda",
            "provider": "aws",
            "name": self.stack.app_name_iac
        }

        results = self.stack.get_resource(**_lookup)[0]
        return os.path.join(str(results["base_url"]), str(self.stack.trigger_id))

    def _init_common(self):
        """
        Initializes common settings for the application, including tokens, buckets, and repositories.
        """
        self._set_github_token()
        self._set_buckets()
        self._set_iac_ci_repo()
        self._set_slack_webhook()
        self._set_infracost()
        self._set_misc()

    def _webhook(self):
        """
        Creates a GitHub webhook for the application.
        """
        arguments = {
            "aws_default_region": self.stack.aws_default_region,
            "repo": self.stack.iac_ci_repo,
            "secret": self.stack.secret,
            "name": self.stack.app_name_iac,
            "url": self._get_api_url(),
            "events": 'push,pull_request,issue_comment'
        }

        inputargs = {
            "arguments": arguments,
            "automation_phase": "continuous_delivery",
            "human_description": f'Create webhook {arguments["name"]}'
        }

        return self.stack.github_webhook.insert(display=True, **inputargs)

    def _get_ssh_private_key(self):
        """
        Retrieves and encodes the SSH private key for the application.

        Returns:
            str: The encoded SSH private key.
        """
        _lookup = {
            "must_be_one": True,
            "resource_type": "ssh_key_pair",
            "provider": "config0",
            "name": self.stack.app_name_iac
        }

        resource = self.stack.get_resource(decrypt=True,
                                           **_lookup)[0]
    
        return self.stack.b64_encode(resource["private_key"])

    def _sshdeploy(self):
        """
        Deploys the SSH key for the application.
        """
        arguments = {
            "key_name": self.stack.app_name_iac,
            "aws_default_region": self.stack.aws_default_region,
            "repo": self.stack.iac_ci_repo
        }

        inputargs = {
            "arguments": arguments,
            "automation_phase": "continuous_delivery",
            "human_description": f'Create deploy key "{self.stack.app_name_iac}"'
        }

        return self.stack.new_github_ssh_key.insert(display=True,
                                                    **inputargs)

    def _ssm(self):
        """
        Adds various secrets to AWS SSM, including tokens and keys.
        """
        self._add_ssm_callback_token()
        self._add_ssm_ssh_key()
        self._add_ssm_iac_ci_github_token()
        self._add_ssm_slack()
        self._add_ssm_infracost()

    def _get_dynamodb_item(self):
        """
        Constructs the DynamoDB item for the current application.

        Returns:
            str: The encoded item for DynamoDB.
        """
        item = {
            "_id": {"S": str(self.stack.trigger_id)},
            "trigger_id": {"S": str(self.stack.trigger_id)},
            "app_name_iac": {"S": str(self.stack.app_name_iac)},
            "iac_ci_repo": {"S": str(self.stack.iac_ci_repo)},
            "repo_name": {"S": str(self.stack.iac_ci_repo)},
            "secret": {"S": str(self.stack.secret)},
            "saas_env": {"S": str(self.stack.saas_env)},
            "run_title": {"S": str(self.stack.app_name_iac)},
            "user_endpoint": {"S": str(self.stack.get_user_endpt())},
            "ssm_callback_token": {"S": str(self.stack.ssm_callback_token)},
            "ssm_ssh_key": {"S": str(self.stack.ssm_ssh_key)},
            "ssm_iac_ci_github_token": {"S": str(self.stack.ssm_iac_ci_github_token)},
            "s3_bucket_tmp": {"S": str(self.stack.tmp_bucket)},
            "remote_stateful_bucket": {"S": str(self.stack.remote_stateful_bucket)},
            "type": {"S": "registered_repo"}
        }

        # additional optional credentials
        if self.stack.get_attr("ssm_infracost_api_key"):
            item["ssm_infracost_api_key"] = {
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
        """
        Adds the IaC CI GitHub token to AWS SSM if it exists.
        """
        if not self.stack.get_attr("ssm_iac_ci_github_token"):
            return

        arguments = {
            "ssm_key": self.stack.ssm_iac_ci_github_token,
            "ssm_value": self.stack.iac_ci_github_token,
            "aws_default_region": self.stack.aws_default_region
        }

        inputargs = {
            "arguments": arguments,
            "automation_phase": "continuous_delivery",
            "human_description": "Repo IaC CI Token to ssm"
        }

        self.stack.aws_ssm_param.insert(display=True, **inputargs)

    def _add_ssm_infracost(self):
        """
        Adds the Infracost API key to AWS SSM if it exists.
        """
        if not self.stack.get_attr("ssm_infracost_api_key"):
            return

        arguments = {
            "ssm_key": self.stack.ssm_infracost_api_key,
            "ssm_value": self.stack.infracost_api_key,
            "aws_default_region": self.stack.aws_default_region
        }

        inputargs = {
            "arguments": arguments,
            "automation_phase": "continuous_delivery",
            "human_description": "Infracost token to ssm"
        }

        self.stack.aws_ssm_param.insert(display=True, **inputargs)

    def _add_ssm_callback_token(self):
        """
        Adds the callback token to AWS SSM.
        """
        self.stack.set_variable("ssm_callback_token",
                                f"/config0-iac/imported/{self.stack.app_name_iac}/{self.stack.iac_ci_repo}/config0/callback_token")

        # add config0 token
        arguments = {
            "ssm_key": self.stack.ssm_callback_token,
            "ssm_value": self._get_token(),
            "aws_default_region": self.stack.aws_default_region
        }

        inputargs = {
            "arguments": arguments,
            "automation_phase": "continuous_delivery",
            "human_description": "Config0 callback token to ssm"
        }

        self.stack.aws_ssm_param.insert(display=True, **inputargs)

    def _add_ssm_ssh_key(self):
        """
        Adds the SSH private key to AWS SSM.
        """
        self.stack.set_variable("ssm_ssh_key",
                                f"/config0-iac/imported/{self.stack.app_name_iac}/{self.stack.iac_ci_repo}/sshkeys/private_key")

        # add ssh key
        arguments = {
            "ssm_key": self.stack.ssm_ssh_key,
            "ssm_value": self._get_ssh_private_key(),
            "aws_default_region": self.stack.aws_default_region
        }

        inputargs = {
            "arguments": arguments,
            "automation_phase": "continuous_delivery",
            "human_description": "Upload private ssh key to ssm"
        }

        self.stack.aws_ssm_param.insert(display=True, **inputargs)

    def _add_ssm_slack(self):

        if not self.stack.get_attr("slack_webhook_hash"):
            return

        arguments = {
            "ssm_key": self.stack.ssm_slack_webhook_hash,
            "ssm_value": self.stack.slack_webhook_hash,
            "aws_default_region": self.stack.aws_default_region
        }

        inputargs = {
            "arguments": arguments,
            "automation_phase": "continuous_delivery",
            "human_description": "Upload slack webhook url to ssm"
        }

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
            "human_description": f'Add register repo for iac ci {self.stack.app_name_iac}'
        }

        return self.stack.dynamodb_item.insert(display=True,
                                               **inputargs)

    def _add_iac_ci_to_db(self):

        values = {
            "_id": self.stack.trigger_id,
            "trigger_id": self.stack.trigger_id,
            "source_method": "stack",
            "iac_ci_repo": self.stack.iac_ci_repo,
            "repo_name": self.stack.iac_ci_repo,
            "app_name_iac": self.stack.app_name_iac,
            "provider": "user_input",
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

        values["name"] = self.stack.app_name_iac
        inputargs["name"] = self.stack.app_name_iac

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
