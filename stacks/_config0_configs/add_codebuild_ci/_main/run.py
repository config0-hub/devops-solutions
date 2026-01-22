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

        self.parse.add_optional(key="ecr_repository_uri",
                                types="str")

        self.parse.add_optional(key="ecr_repo_name",
                                types="str")

        self.parse.add_optional(key="docker_repository_uri",
                                types="str")

        self.parse.add_optional(key="docker_repo_name",
                                types="str")

        self.parse.add_optional(key="docker_username",
                                types="str")

        self.parse.add_optional(key="run_title",
                                types="str",
                                default="codebuild_ci")

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

        self.parse.add_optional(key="secret",
                                types="str",
                                default="_random")

        self.parse.add_optional(key="branch",
                                types="str",
                                default="master")

        self.parse.add_required(key="ci_environment")

        # this is required to make the buckets unique
        self.parse.add_optional(key="suffix_id",
                                types="str")

        self.parse.add_optional(key="suffix_length",
                                types="int",
                                default="4")

        self.parse.add_optional(key="docker_registry",
                                types="str",
                                default="ecr")

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

        self.parse.add_optional(key="aws_default_region",
                                types="str",
                                default="us-east-1")

        # Add substack
        self.stack.add_substack('config0-publish:::aws_ecr_repo')
        self.stack.add_substack('config0-publish:::aws_s3_bucket')
        self.stack.add_substack('config0-publish:::new_github_ssh_key')
        self.stack.add_substack('config0-publish:::aws_dynamodb_item', 'dynamodb')
        self.stack.add_substack('config0-publish:::aws_ssm_param')
        self.stack.add_substack('config0-publish:::aws_codebuild')
        self.stack.add_substack('config0-publish:::github_webhook')

        self.stack.init_substacks()

    def _setup_vars(self):
        self.stack.init_variables()

    def _determine_suffix_id(self):
        """
        Determine the suffix ID for resource naming.
        
        Returns:
            str: A lowercase suffix ID either from the stack's suffix_id attribute
                or generated from the CI environment name
        """
        if self.stack.get_attr("suffix_id"):
            return self.stack.suffix_id.lower()

        return self.stack.b64_encode(self.stack.ci_environment)[0:int(self.stack.suffix_length)].lower()

    def _get_api_url(self):
        """
        Retrieve the API Gateway URL for the CI environment.
        
        Returns:
            str: The complete API URL including the trigger ID
        
        Raises:
            Exception: If the API Gateway resource cannot be found
        """
        import os

        apigateway_name = f"ci-shared-{self.stack.ci_environment}"

        _lookup = {"must_be_one": True,
                  "resource_type": "apigateway_restapi_lambda",
                  "provider": "aws",
                  "name": apigateway_name}

        results = self.stack.get_resource(**_lookup)[0]

        return os.path.join(str(results["base_url"]), str(self.stack.trigger_id))

    def _get_ssh_private_key(self):
        """
        Retrieve the SSH private key for the CodeBuild deployment.
        
        Returns:
            str: Base64 encoded private key
        
        Raises:
            Exception: If the SSH key resource cannot be found
        """
        key_name = f"{self.stack.codebuild_name}-codebuild-deploy-key"

        _lookup = {"must_be_one": True,
                  "resource_type": "ssh_key_pair",
                  "provider": "config0",
                  "name": key_name}

        results = self.stack.get_resource(decrypt=True, **_lookup)[0]

        return self.stack.b64_encode(results["private_key"])

    def _get_ecr_uri(self):
        """
        Get the ECR repository URI.
        
        Returns:
            str: The ECR repository URI if ecr_repo_name is set, None otherwise
        
        Raises:
            Exception: If the ECR repository resource cannot be found
        """
        if not self.stack.get_attr("ecr_repo_name"):
            return

        return self.stack.get_resource(name=self.stack.ecr_repo_name,
                                      resource_type="ecr_repo",
                                      provider="aws",
                                      must_exists=True)[0]["repository_uri"]

    def _set_codebuild_buckets(self):
        """
        Set the S3 bucket names for CodeBuild cache and output.
        
        This method generates unique S3 bucket names using the codebuild_name
        and suffix_id. The buckets are used for:
        - Cache storage (s3_bucket_cache)
        - Build output storage (s3_bucket_output)
        """
        suffix_id = self._determine_suffix_id()

        self.s3_bucket_cache = f"{self.stack.codebuild_name}-codebuild-{suffix_id}-cache"
        self.s3_bucket_output = f"{self.stack.codebuild_name}-codebuild-{suffix_id}-output"

    def _webhook(self):
        """
        Configure GitHub webhook for the CodeBuild project.
        
        Creates a webhook in the GitHub repository that triggers the CodeBuild
        project when code changes are pushed.
        
        Returns:
            dict: Result of webhook creation
        """
        self._setup_vars()
        self.stack.verify_variables()

        _name = f"config0-codebuild-{self.stack.ci_environment}-{self.stack.codebuild_name}"

        _url = self._get_api_url()

        arguments = {
            "aws_default_region": self.stack.aws_default_region,
            "repo": self.stack.git_repo,
            "secret": self.stack.secret,
            "name": _name,
            "url": _url
        }

        human_description = f'Create Github webhook for codebuild "{self.stack.codebuild_name}"'
        inputargs = {"arguments": arguments,
                    "automation_phase": "continuous_delivery",
                    "human_description": human_description}

        return self.stack.github_webhook.insert(display=True, **inputargs)

    def run_setup(self):
        """
        Initialize and run the setup phase of the CodeBuild project.
        
        Sets up ECR repository, SSH deployment keys, and S3 buckets.
        
        Returns:
            dict: Result of S3 bucket creation
        """
        self._setup_vars()
        self._eval_inputvars()
        self.stack.verify_variables()
        self.stack.set_parallel()

        self._add_ecr_repo()
        self._sshdeploy()
        self._token()
        return self._s3()

    def run_connect_repo(self):
        """
        Connect the repository to the CodeBuild project.
        
        This method:
        1. Initializes variables
        2. Evaluates input variables
        3. Verifies required variables
        4. Sets up DynamoDB configuration
        5. Creates GitHub webhook
        
        Returns:
            dict: Result of webhook creation
        """
        self._setup_vars()
        self._eval_inputvars()
        self.stack.verify_variables()
        self._dynamodb()
        return self._webhook()

    def _add_ecr_repo(self):
        arguments = {
            "ecr_repo": self.stack.ecr_repo_name,
            "aws_default_region": self.stack.aws_default_region
        }

        human_description = 'Create ecr repo if it does not exist'

        inputargs = {"arguments": arguments,
                    "automation_phase": "continuous_delivery",
                    "human_description": human_description}

        self.stack.aws_ecr_repo.insert(display=True, **inputargs)

    def _s3(self):
        if "_" in self.stack.get_attr("codebuild_name"):
            msg = "Cannot use underscores (Only hyphens) in the codebuild_name"
            raise Exception(msg)

        self._set_codebuild_buckets()

        arguments = {
            "bucket": self.s3_bucket_cache,
            "acl": self.stack.bucket_acl,
            "expire_days": self.stack.bucket_expire_days,
            "force_destroy": "true",
            "enable_lifecycle": "true",
            "aws_default_region": self.stack.aws_default_region
        }

        if self.stack.get_attr("cloud_tags_hash"):
            arguments["cloud_tags_hash"] = self.stack.cloud_tags_hash

        human_description = f'Create s3 bucket "{self.s3_bucket_cache}" cache'
        inputargs = {"arguments": arguments,
                    "automation_phase": "continuous_delivery",
                    "human_description": human_description}

        self.stack.aws_s3_bucket.insert(display=True, **inputargs)

        arguments = {
            "bucket": self.s3_bucket_output,
            "acl": self.stack.bucket_acl,
            "expire_days": self.stack.bucket_expire_days,
            "force_destroy": "true",
            "enable_lifecycle": "true",
            "aws_default_region": self.stack.aws_default_region
        }

        if self.stack.get_attr("cloud_tags_hash"):
            arguments["cloud_tags_hash"] = self.stack.cloud_tags_hash

        human_description = f'Create s3 bucket "{self.s3_bucket_output}" output'
        inputargs = {"arguments": arguments,
                    "automation_phase": "continuous_delivery",
                    "human_description": human_description}

        return self.stack.aws_s3_bucket.insert(display=True, **inputargs)

    def _sshdeploy(self):
        key_name = f"{self.stack.codebuild_name}-codebuild-deploy-key"

        arguments = {
            "key_name": key_name,
            "aws_default_region": self.stack.aws_default_region,
            "repo": self.stack.git_repo
        }

        human_description = f'Create deploy key "{key_name}"'
        inputargs = {"arguments": arguments,
                    "automation_phase": "continuous_delivery",
                    "human_description": human_description}

        return self.stack.new_github_ssh_key.insert(display=True,
                                                   **inputargs)

    def _set_github_token(self):
        if self.stack.inputvars.get("github_token"):
            self.stack.set_variable("github_token",
                               self.stack.inputvars["github_token"],
                               tags="tf_sensitive",
                               types="str")
        elif self.stack.inputvars.get("GITHUB_TOKEN"):
            self.stack.set_variable("github_token",
                                    self.stack.inputvars["GITHUB_TOKEN"],
                                    tags="tf_sensitive",
                                    types="str")
        elif self.stack.inputvars.get("github_token_hash"):
            self.stack.set_variable("github_token",
                               self.stack.b64_encode(self.stack.inputvars["github_token_hash"]),
                               tags="tf_sensitive",
                               types="str")

    # dup 3453254
    def _set_slack_webhook(self):
        """
        Set the Slack webhook URL for notifications.
        
        This method retrieves the Slack webhook URL from input variables and stores it
        in the stack's variables for later use.
        """
        if self.stack.inputvars.get("slack_webhook_b64"):
            self.stack.set_variable("slack_webhook_hash",
                                    self.stack.inputvars.get("slack_webhook_b64"),
                                    tags="tf_sensitive",
                                    types="str")
        elif self.stack.inputvars.get("slack_webhook_hash"):
            self.stack.set_variable("slack_webhook_hash",
                                    self.stack.inputvars.get("slack_webhook_hash"),
                                    tags="tf_sensitive",
                                    types="str")
        else:
            self.stack.set_variable("slack_webhook_hash",
                                    None,
                                    tags="tf_sensitive",
                                    types="str")

    def _eval_inputvars(self):
        self._set_github_token()
        self._set_slack_webhook()

        self.stack.set_variable("docker_token", 
                                self.stack.inputvars.get("docker_token"),
                                tags="tf_sensitive",
                                types="str")

    def run_ssm(self):
        """
        Configure AWS Systems Manager (SSM) parameters.
        
        Stores sensitive information in SSM Parameter Store including:
        - Config0 callback token
        - SSH private key
        - Docker token (if provided)
        - Slack webhook URL (if provided)
        
        Returns:
            bool: True if successful
        """
        self._setup_vars()
        self.stack.verify_variables()
        self._eval_inputvars()
        self._set_ssm_keys()
        self.stack.set_parallel()

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

        if self.stack.get_attr("docker_token"):
            arguments = {
                "ssm_key": self.stack.ssm_docker_token,
                "ssm_value": self.stack.docker_token,
                "aws_default_region": self.stack.aws_default_region
            }

            inputargs = {
                "arguments": arguments,
                "automation_phase": "continuous_delivery",
                "human_description": "Upload docker token to ssm"
            }

            self.stack.aws_ssm_param.insert(display=True, **inputargs)

        if self.stack.get_attr("slack_webhook_hash"):
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

        return True

    def _get_s3_bucket(self):
        suffix_id = self._determine_suffix_id()
        return f"ci-shared-{self.stack.ci_environment}-{suffix_id}"

    def _set_docker_items(self, item):

        ecr_uri = None

        if self.stack.get_attr("ssm_docker_token"):
            item["ssm_docker_token"] = {"S": str(self.stack.ssm_docker_token)}

        # determine docker repository uri
        if self.stack.get_attr("docker_username"):
            item["docker_username"] = {"S": str(self.stack.docker_username)}

        if self.stack.get_attr("ecr_repository_uri"):
            item["ecr_repository_uri"] = {
                "S": str(self.stack.ecr_repository_uri)
            }
            ecr_uri = self.stack.ecr_repository_uri
        elif self.stack.get_attr("ecr_repo_name"):
            # ecr is primary and should be set
            ecr_uri = self._get_ecr_uri()
            item["ecr_repository_uri"] = {"S": str(ecr_uri)}

        if not ecr_uri:
            failed_message = "need to specify either ecr_repository_uri or ecr_repo_name to look up"
            raise Exception(failed_message)

        # if ecr_repo_name not set, we take it from the ecr_repository_uri
        if self.stack.get_attr("ecr_repo_name"):
            item["ecr_repo_name"] = {"S": str(self.stack.ecr_repo_name)}
        else:
            repo_name = str(ecr_uri.split("/")[-1])
            item["ecr_repo_name"] = {"S": str(repo_name)}

        # if docker_repository_uri not set, we set to ecr_repository_uri
        if self.stack.get_attr("docker_repository_uri"):
            item["docker_repository_uri"] = {
                "S": str(self.stack.docker_repository_uri)}
        elif ecr_uri:
            item["docker_repository_uri"] = item["ecr_repository_uri"]

        if self.stack.get_attr("docker_repo_name"):
            item["docker_repo_name"] = {"S": str(self.stack.docker_repo_name)}
        else:
            repo_name = str(item["docker_repository_uri"]["S"].split("/")[-1])
            item["docker_repo_name"] = {"S": str(repo_name)}

    def _get_dynamodb_item(self):
        """
        Generate the DynamoDB item for storing CodeBuild configuration.
        
        Creates a complete configuration item including:
        - Build settings
        - Repository information
        - Credentials and tokens
        - S3 bucket configurations
        
        Returns:
            str: Base64 encoded DynamoDB item
        """
        suffix_id = self._determine_suffix_id()
        self._eval_inputvars()
        self._set_ssm_keys()

        s3_bucket = self._get_s3_bucket()
        s3_bucket_tmp = f"{s3_bucket}-tmp"

        self._set_codebuild_buckets()

        item = {
            "_id": {"S": str(self.stack.trigger_id)},
            "ci_environment": {"S": str(self.stack.ci_environment)},
            "codebuild_name": {"S": str(self.stack.codebuild_name)},
            "git_repo": {"S": str(self.stack.git_repo)},
            "git_url": {"S": str(self.stack.git_url)},
            "privileged_mode": {"S": str(self.stack.privileged_mode)},
            "image_type": {"S": str(self.stack.image_type)},
            "build_image": {"S": str(self.stack.build_image)},
            "build_timeout": {"S": str(self.stack.build_timeout)},
            "compute_type": {"S": str(self.stack.compute_type)},
            "docker_registry": {"S": str(self.stack.docker_registry)},
            "aws_default_region": {"S": str(self.stack.aws_default_region)},
            "trigger_id": {"S": str(self.stack.trigger_id)},
            "secret": {"S": str(self.stack.secret)},
            "ssm_ssh_key": {"S": str(self.stack.ssm_ssh_key)},
            "ssm_callback_key": {"S": str(self.stack.ssm_callback_token)},
            "s3_bucket": {"S": str(s3_bucket)},
            "s3_bucket_tmp": {"S": str(s3_bucket_tmp)},
            "s3_bucket_cache": {"S": str(self.s3_bucket_cache)},
            "s3_bucket_output": {"S": str(self.s3_bucket_output)},
            "suffix_id": {"S": str(suffix_id)},
            "saas_env": {"S": str(self.stack.saas_env)},
            "branch": {"S": str(self.stack.branch)},
            "run_title": {"S": str(self.stack.run_title)}
            }

        # additional credentials
        if self.stack.get_attr("ssm_slack_webhook_hash"):
            item["ssm_slack_webhook_hash"] = {
                "S": str(self.stack.ssm_slack_webhook_hash)}

        if self.stack.get_attr("slack_channel"):
            item["slack_channel"] = {"S": str(self.stack.slack_channel)}

        self._set_docker_items(item)

        # config0 settings
        item["user_endpoint"] = {"S": str(self.stack.get_user_endpt())}

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

        # REF: revisit 54324345234535
        item["sched_type"] = {"S": "build"}

        if self.stack.get_attr("sched_type") != "build":
            self.stack.logger.warn('sched_type should be build - overide ci/commit UI display')

        return self.stack.b64_encode(item)

    def _set_ssm_keys(self):
        self.stack.set_variable("ssm_docker_token", None)
        self.stack.set_variable("ssm_slack_webhook_hash", None)

        self.stack.set_variable("ssm_ssh_key", 
                                f"/codebuild/{self.stack.codebuild_name}/sshkeys/private")

        self.stack.set_variable("ssm_callback_token", 
                                f"/codebuild/{self.stack.codebuild_name}/config0/callback_token")

        if self.stack.get_attr("docker_token"):
            self.stack.set_variable("ssm_docker_token", 
                                    f"/codebuild/{self.stack.codebuild_name}/config0/docker_token")

        if self.stack.get_attr("slack_webhook_hash"):
            self.stack.set_variable("ssm_slack_webhook_hash",
                                    f"/codebuild/{self.stack.codebuild_name}/config0/slack_webhook_hash")

    def _get_token(self):
        _lookup = {
            "must_be_one": True,
            "resource_type": "config0_token",
            "provider": "config0",
            "name": self.stack.codebuild_name
        }

        return str(self.stack.get_resource(**_lookup)[0]["token"])

    def _token(self):
        self.stack.create_token(name=self.stack.codebuild_name)

        return True

    def _dynamodb(self):
        table_name = f"ci-shared-settings"
        item_hash = self._get_dynamodb_item()

        arguments = {
            "table_name": table_name,
            "hash_key": "_id",
            "item_hash": item_hash,
            "aws_default_region": self.stack.aws_default_region
        }

        human_description = f'Add setting item for codebuild name {self.stack.codebuild_name}'
        inputargs = {
            "arguments": arguments,
            "automation_phase": "continuous_delivery",
            "human_description": human_description
        }

        return self.stack.dynamodb.insert(display=True, **inputargs)

    def run_codebuild(self):
        """
        Create and configure the AWS CodeBuild project.
        
        Sets up:
        - Build environment variables
        - SSM parameter mappings
        - S3 bucket configurations
        - VPC settings (if provided)
        
        Returns:
            dict: Result of CodeBuild project creation
        """
        self._setup_vars()
        self.stack.verify_variables()
        self._eval_inputvars()
        self._set_ssm_keys()

        ssm_params = {"SSH_KEY": self.stack.ssm_ssh_key}

        if self.stack.get_attr("ssm_docker_token"):
            ssm_params["DOCKER_TOKEN"] = self.stack.ssm_docker_token

        if self.stack.get_attr("ssm_slack_webhook_hash"):
            ssm_params["SLACK_WEBHOOK_HASH"] = self.stack.ssm_slack_webhook_hash

        codebuild_env_vars = {"GIT_URL": self.stack.git_url}

        arguments = {
            "docker_registry": self.stack.docker_registry,
            "ssm_params_hash": self.stack.b64_encode(ssm_params),
            "codebuild_env_vars_hash": self.stack.b64_encode(codebuild_env_vars),
            "aws_default_region": self.stack.aws_default_region,
            "codebuild_name": self.stack.codebuild_name
        }

        if self.stack.get_attr("cloud_tags_hash"):
            arguments["cloud_tags_hash"] = self.stack.cloud_tags_hash

        if self.stack.get_attr("subnet_ids"):
            arguments["subnet_ids"] = self.stack.subnet_ids

        if self.stack.get_attr("vpc_id"):
            arguments["vpc_id"] = self.stack.vpc_id

        if self.stack.get_attr("security_group_id"):
            arguments["security_group_id"] = self.stack.security_group_id

        # using tmp bucket for logs
        self._set_codebuild_buckets()

        arguments.update({
            "s3_bucket": f"{self._get_s3_bucket()}-tmp",
            "s3_bucket_cache": self.s3_bucket_cache,
            "s3_bucket_output": self.s3_bucket_output
            })

        human_description = f'Create Codebuild project "{self.stack.codebuild_name}"'

        inputargs = {
            "arguments": arguments,
            "automation_phase": "continuous_delivery",
            "human_description": human_description
        }

        return self.stack.aws_codebuild.insert(display=True, **inputargs)

    def run(self):
        """
        Execute the complete CodeBuild setup process.
        
        This method orchestrates the entire setup by:
        1. Disabling parallel execution
        2. Adding setup jobs
        3. Adding repository connection jobs
        4. Adding SSM parameter configuration jobs
        5. Adding CodeBuild project creation jobs
        
        Returns:
            dict: Results of all job executions
        """
        self.stack.unset_parallel(sched_init=True)
        self.add_job("setup")
        self.add_job("connect_repo")
        self.add_job("ssm")
        self.add_job("codebuild")
        # self.add_job("webhook")

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
