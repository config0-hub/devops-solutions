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
        """
        Initialize the IaC CI/CD stack.

        Args:
            stackargs: Stack arguments containing configuration parameters

        Initializes required and optional parameters for the stack, including
        repository details, branch information, and runtime configurations.
        """

        newSchedStack.__init__(self, stackargs)

        self.parse.add_required(key="repo_name",
                                types="str")

        self.parse.add_required(key="branch",
                                types="str")

        self.parse.add_optional(key="stateful_id",
                                types="str",
                                default="_random")

        self.parse.add_optional(key="tf_runtime",
                                types="str",
                                default="tofu:1.9.1")

        self.parse.add_optional(key="app_name",
                                types="str",
                                default="terraform")

        self.parse.add_optional(key="apply_keyword",
                                types="str",
                                default="null")

        self.parse.add_optional(key="check_keyword",
                                types="str",
                                default="check tf")

        self.parse.add_optional(key="destroy_keyword",
                                types="str",
                                default="null")

        self.parse.add_optional(key="require_approval",
                                types="bool",
                                default=False)

        # only supporting terraform to begin with
        self.parse.add_optional(key="source_method",
                                types="str",
                                default="terraform")

        self.parse.add_optional(key="subdir",
                                types="str",
                                default="null")

        self.parse.add_optional(key="ssm_name",
                                types="str",
                                default="null")

        # add substack
        self.stack.add_substack('config0-publish:::aws_codebuild')
        self.stack.add_substack('config0-publish:::aws_dynamodb_item', 'dynamodb_item')

        self.stack.init_substacks()

    def _set_registered_repo_info(self):
        """
        Set registered repository information.

        Retrieves resource information for the IaC CI repository and sets
        necessary variables including app name, trigger ID, and DynamoDB
        table names for runs and settings.

        Raises:
            Exception: If required resource information cannot be found.
        """

        _lookup = {
            "must_be_one": True,
            "resource_type": "iac_ci",
            "provider": "user_input",
            "iac_ci_repo": self.stack.repo_name}

        resource = self.stack.get_resource(**_lookup)[0]

        self.stack.set_variable("app_name_iac",
                                str(resource["app_name_iac"]))

        self.stack.set_variable("trigger_id",
                                str(resource["trigger_id"]))

        self.stack.set_variable("dynamodb_name_runs", f"{self.stack.app_name_iac}-runs")
        self.stack.set_variable("dynamodb_name_settings", f"{self.stack.app_name_iac}-settings")

    def _get_dynamodb_item(self):
        """
        Generate DynamoDB item configuration.

        Creates a DynamoDB item structure containing all necessary configuration
        parameters for the IaC CI/CD pipeline, including repository details,
        runtime settings, and optional configurations.

        Returns:
            str: Base64 encoded DynamoDB item configuration.
        """

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
            "stateful_id": {"S": str(self.stack.stateful_id)},
            "tf_runtime": {"S": str(self.stack.tf_runtime)},
            "app_name": {"S": str(self.stack.app_name)},
            "app_dir": {"S": f'var/tmp/{str(self.stack.app_name)}'},
            "run_share_dir": {"S": f'/var/tmp/share/{str(self.stack.stateful_id)}'},
            "type": {"S": "iac_setting"}
        }

        if self.stack.require_approval not in ["False", False, "false"]:
            item["require_approval"] = {"S": "True"}

        if self.stack.get_attr("schedule_id"):
            item["schedule_id"] = {"S": str(self.stack.schedule_id)}

        if self.stack.get_attr("project_id"):
            item["project_id"] = {"S": str(self.stack.project_id)}

        if self.stack.get_attr("job_instance_id"):
            item["job_instance_id"] = {"S": str(self.stack.job_instance_id)}

        if self.stack.subdir:
            item["iac_ci_folder"] = {"S": str(self.stack.subdir)}

        if self.stack.apply_keyword:
            item["apply_str"] = {"S": f'apply {self.stack.apply_keyword}'}

        if self.stack.check_keyword:
            item["check_str"] = {"S": f'check {self.stack.check_keyword}'}

        if self.stack.destroy_keyword:
            item["destroy_str"] = {"S": f'destroy {self.stack.destroy_keyword}'}

        if self.stack.ssm_name:
            item["ssm_name"] = {"S": str(self.stack.ssm_name)}

        return self.stack.b64_encode(item)

    def _dynamodb_item(self):
        """
        Create DynamoDB item for pipeline configuration.

        Prepares and executes the insertion of configuration settings into
        DynamoDB, including all necessary parameters for the IaC CI/CD pipeline.

        Returns:
            dict: Result of the DynamoDB item insertion operation.

        Raises:
            Exception: If DynamoDB item insertion fails.
        """

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
        """
        Initialize and setup the IaC CI/CD pipeline.

        Performs initial variable setup, verification, and creates necessary
        DynamoDB entries for pipeline configuration.

        Returns:
            dict: Result of the setup operation.
        """

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
        """
        Execute the main pipeline setup process.

        Manages job scheduling and execution for the pipeline setup process.

        Returns:
            dict: Final job execution results.
        """

        self.stack.unset_parallel(sched_init=True)
        self.add_job("setup")

        return self.finalize_jobs()

    def schedule(self):
        """
        Configure scheduling for pipeline setup jobs.

        Sets up job scheduling parameters including timeouts, retry conditions,
        and human-readable descriptions for the setup process.

        Returns:
            list: List of configured schedules for the pipeline setup.
        """

        sched = self.new_schedule()
        sched.job = "setup"
        sched.archive.timeout = 900
        sched.archive.timewait = 120
        sched.automation_phase = "continuous_delivery"
        sched.human_description = "Setup IAC CI for existing IAC"
        sched.conditions.retries = 1
        self.add_schedule()

        return self.get_schedules()