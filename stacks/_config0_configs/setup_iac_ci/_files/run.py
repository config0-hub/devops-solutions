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
        Initialize the Main class with the provided stack arguments.

        Args:
            stackargs (dict): Arguments required to initialize the stack.
        """
        newSchedStack.__init__(self, stackargs)

        self.parse.add_required(key="app_name", types="str", default="iac-ci")
        self.parse.add_optional(key="cloud_tags_hash", types="str")
        self.parse.add_optional(key="runtime", types="str", default="python3.11")
        self.parse.add_optional(key="aws_default_region", types="str", default="us-east-1")

        # Initialize substacks
        self.stack.add_substack("config0-publish:::aws_dynamodb")
        self.stack.add_substack("config0-publish:::apigw_lambda-integ", "apigw")
        self.stack.add_substack("config0-publish:::aws-lambda-python-codebuild", "py_lambda")
        self.stack.add_substack("config0-publish:::iac_ci_stepf")
        self.stack.add_substack("config0-publish:::iac_ci_complete_trigger", "sns_subscription")

        # Initialize execution groups
        self.stack.add_execgroup("config0-publish:::github::lambda_trigger_stepf")
        self.stack.add_execgroup("config0-publish:::devops-solutions::iac_ci", "lambda_iac_ci")

        self.stack.init_execgroups()
        self.stack.init_substacks()

    def _set_cloud_tag_hash(self):
        """
        Set and encode the cloud tags hash with additional metadata.

        Returns:
            str: Encoded cloud tags hash.
        """
        try:
            cloud_tags = self.stack.b64_decode(self.stack.cloud_tags_hash)
        except:
            cloud_tags = {}

        cloud_tags.update({
            "environment": self.stack.app_name,
            "aws_default_region": self.stack.aws_default_region
        })

        return self.stack.b64_encode(cloud_tags)

    def _get_env_vars_lambda_hashes(self):
        """
        Get environment variable hashes for Lambda functions.

        Returns:
            tuple: Base environment variable hash and webhook environment variable hash.
        """
        base_hash = self.stack.b64_encode({"ENV": "build"})

        env_vars = {
            "ENV": "build",
            "DEBUG_IAC_CI": "true",
            "BUILD_TTL": "60"
        }
        webhook_hash = self.stack.b64_encode(env_vars)

        return base_hash, webhook_hash

    def _dynamodb(self, cloud_tags_hash):
        """
        Create DynamoDB tables with the provided cloud tags.

        Args:
            cloud_tags_hash (str): Encoded cloud tags hash.
        """
        dynamodb_names = [
            self.stack.dynamodb_name_runs,
            self.stack.dynamodb_name_settings,
        ]

        for dynamodb_name in dynamodb_names:
            arguments = {
                "dynamodb_name": dynamodb_name,
                "cloud_tags_hash": cloud_tags_hash,
                "aws_default_region": self.stack.aws_default_region
            }

            inputargs = {
                "arguments": arguments,
                "automation_phase": "infrastructure",
                "human_description": f"Create DynamoDB {dynamodb_name}"
            }

            self.stack.aws_dynamodb.insert(display=True, **inputargs)

    @staticmethod
    def _get_log_policy():
        """
        Get the IAM policy for CloudWatch Logs.

        Returns:
            dict: IAM policy for CloudWatch Logs.
        """
        _statement = {
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:DescribeLogGroups",
                "logs:DescribeLogStreams",
                "logs:PutLogEvents",
                "logs:GetLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:*",
            "Effect": "Allow"
        }
        return _statement

    def _get_dynamodb_policy(self):
        """
        Get the IAM policy for DynamoDB tables.

        Returns:
            dict: IAM policy for DynamoDB tables.
        """
        arn_dynamodb_name_runs = f"arn:aws:dynamodb:{self.stack.aws_default_region}:${{aws_account_id}}:table/{self.stack.dynamodb_name_runs}"
        arn_dynamodb_name_settings = f"arn:aws:dynamodb:{self.stack.aws_default_region}:${{aws_account_id}}:table/{self.stack.dynamodb_name_settings}"

        _statement = {
            "Effect": "Allow",
            "Action": [
                "dynamodb:DescribeTable",
                "dynamodb:PartiQLInsert",
                "dynamodb:GetItem",
                "dynamodb:BatchGetItem",
                "dynamodb:BatchWriteItem",
                "dynamodb:UpdateTimeToLive",
                "dynamodb:PutItem",
                "dynamodb:PartiQLUpdate",
                "dynamodb:Scan",
                "dynamodb:UpdateItem",
                "dynamodb:UpdateTable",
                "dynamodb:GetRecords",
                "dynamodb:ListTables",
                "dynamodb:DeleteItem",
                "dynamodb:ListTagsOfResource",
                "dynamodb:PartiQLSelect",
                "dynamodb:ConditionCheckItem",
                "dynamodb:Query",
                "dynamodb:DescribeTimeToLive",
                "dynamodb:ListStreams",
                "dynamodb:PartiQLDelete"
            ],
            "Resource": [
                arn_dynamodb_name_runs,
                arn_dynamodb_name_settings
            ]
        }
        return _statement

    def _get_s3_policies(self):
        """
        Get the IAM policies for accessing S3 buckets.

        Returns:
            list: List of IAM policy statements for S3 access.
        """
        arn_s3_bucket = f"arn:aws:s3:::{self.stack.remote_stateful_bucket}"
        arn_s3_bucket_lambda = f"arn:aws:s3:::{self.stack.lambda_bucket}"
        arn_s3_bucket_log = f"arn:aws:s3:::{self.stack.log_bucket}"
        arn_s3_bucket_tmp = f"arn:aws:s3:::{self.stack.tmp_bucket}"

        statements = []

        _statement = {
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket",
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject"
            ],
            "Resource": [
                arn_s3_bucket,
                arn_s3_bucket_lambda,
                arn_s3_bucket_tmp,
                arn_s3_bucket_log,
                f"{arn_s3_bucket}/*",
                f"{arn_s3_bucket_lambda}/*",
                f"{arn_s3_bucket_tmp}/*",
                f"{arn_s3_bucket_log}/*"
            ]
        }
        statements.append(_statement)

        _statement = {
            "Effect": "Allow",
            "Action": [
                "s3:ListAllMyBuckets",
                "ssm:*"
            ],
            "Resource": "*"
        }
        statements.append(_statement)

        return statements

    @staticmethod
    def _get_lambda_policy():
        """
        Get the IAM policy for Lambda functions.

        Returns:
            dict: IAM policy for Lambda functions.
        """
        _action = [
            "lambda:TagResource",
            "lambda:GetFunctionConfiguration",
            "lambda:ListProvisionedConcurrencyConfigs",
            "lambda:GetProvisionedConcurrencyConfig",
            "lambda:ListLayerVersions",
            "lambda:ListLayers",
            "lambda:ListCodeSigningConfigs",
            "lambda:GetAlias",
            "lambda:ListFunctions",
            "lambda:GetEventSourceMapping",
            "lambda:InvokeFunction",
            "lambda:ListAliases",
            "lambda:GetFunctionCodeSigningConfig",
            "lambda:ListFunctionEventInvokeConfigs",
            "lambda:ListFunctionsByCodeSigningConfig",
            "lambda:GetFunctionConcurrency",
            "lambda:ListEventSourceMappings",
            "lambda:ListVersionsByFunction",
            "lambda:GetLayerVersion",
            "lambda:InvokeAsync",
            "lambda:GetAccountSettings",
            "lambda:GetLayerVersionPolicy",
            "lambda:UntagResource",
            "lambda:ListTags",
            "lambda:GetFunction",
            "lambda:GetFunctionEventInvokeConfig",
            "lambda:GetCodeSigningConfig",
            "lambda:GetPolicy"
        ]

        _statement = {
            "Action": _action,
            "Resource": "*",
            "Effect": "Allow"
        }

        return _statement

    @staticmethod
    def _get_codebuild_policy():
        """
        Get the IAM policy for CodeBuild.

        Returns:
            dict: IAM policy for CodeBuild.
        """
        _action = [
            "codebuild:ListReportsForReportGroup",
            "codebuild:ListBuildsForProject",
            "codebuild:BatchGetBuilds",
            "codebuild:StopBuildBatch",
            "codebuild:ListReports",
            "codebuild:DeleteBuildBatch",
            "codebuild:BatchGetReports",
            "codebuild:ListCuratedEnvironmentImages",
            "codebuild:ListBuildBatches",
            "codebuild:ListBuilds",
            "codebuild:BatchDeleteBuilds",
            "codebuild:StartBuild",
            "codebuild:BatchGetBuildBatches",
            "codebuild:GetResourcePolicy",
            "codebuild:StopBuild",
            "codebuild:RetryBuild",
            "codebuild:ImportSourceCredentials",
            "codebuild:BatchGetReportGroups",
            "codebuild:BatchGetProjects",
            "codebuild:RetryBuildBatch",
            "codebuild:StartBuildBatch"
        ]

        _statement = {
            "Action": _action,
            "Resource": "*",
            "Effect": "Allow"
        }

        return _statement

    @staticmethod
    def _get_stepf_policy():
        """
        Get the IAM policy for Step Functions.

        Returns:
            dict: IAM policy for Step Functions.
        """
        _action = [
            "states:StartExecution",
            "states:StopExecution",
            "states:DescribeExecution",
            "states:ListExecutions",
            "states:DescribeStateMachine",
            "states:GetExecutionHistory"
        ]

        _statement = {
            "Action": _action,
            "Resource": "*",
            "Effect": "Allow"
        }

        return _statement

    def _get_policy_template_hash(self):
        """
        Generate a base64-encoded IAM policy template.

        Returns:
            str: Base64-encoded policy template.
        """
        statements = []

        _statement = {
            "Action": ["ssm:*"],
            "Resource": "*",
            "Effect": "Allow"
        }

        statements.append(_statement)
        statements.append(self._get_log_policy())
        statements.append(self._get_dynamodb_policy())
        statements.extend(self._get_s3_policies())
        statements.append(self._get_lambda_policy())
        statements.append(self._get_codebuild_policy())

        policy = {
            "Version": "2012-10-17",
            "Statement": statements
        }

        return self.stack.b64_encode(policy, json_dumps=True)

    def _get_stepf_policy_template_hash(self):
        """
        Generate a base64-encoded IAM policy template for Step Functions.

        Returns:
            str: Base64-encoded Step Function policy template.
        """
        statements = [self._get_log_policy()]
        statements.extend(self._get_s3_policies())
        statements.append(self._get_dynamodb_policy())
        statements.append(self._get_lambda_policy())
        statements.append(self._get_stepf_policy())

        policy = {
            "Version": "2012-10-17",
            "Statement": statements
        }

        return self.stack.b64_encode(policy, json_dumps=True)

    def _get_stepf_name(self):
        """
        Get the Step Function name based on the application name.

        Returns:
            str: Step Function name.
        """
        return f"{self.stack.app_name}-stepf-ci"

    def _get_stepf_arn(self):
        """
        Retrieve the ARN of the Step Function.

        Returns:
            str: ARN of the Step Function.
        """
        stepf_name = self._get_stepf_name()
        _info = self.stack.get_resource(name=stepf_name, resource_type="step_function", must_be_one=True)[0]
        return _info["arn"]

    def _stepf(self, cloud_tags_hash):
        """
        Create the Step Function with the provided cloud tags.

        Args:
            cloud_tags_hash (str): Encoded cloud tags hash.
        """
        stepf_name = self._get_stepf_name()
        arguments = {
            "step_function_name": stepf_name,
            "cloud_tags_hash": cloud_tags_hash,
            "aws_default_region": self.stack.aws_default_region
        }

        inputargs = {
            "arguments": arguments,
            "automation_phase": "infrastructure",
            "human_description": f"Create Step Function {stepf_name}"
        }

        self.stack.iac_ci_stepf.insert(display=True, **inputargs)

    def _lambda(self, cloud_tags_hash):
        """
        Create AWS Lambda functions with the provided cloud tags.

        Args:
            cloud_tags_hash (str): Encoded cloud tags hash.
        """
        self.stack.set_parallel()

        policy_template_hash = self._get_policy_template_hash()
        base_env_vars_hash, webhook_env_vars_hash = self._get_env_vars_lambda_hashes()

        base_arguments = {
            "s3_bucket": self.stack.lambda_bucket,
            "runtime": self.stack.runtime,
            "policy_template_hash": policy_template_hash,
            "lambda_env_vars_hash": base_env_vars_hash,
            "cloud_tags_hash": cloud_tags_hash,
            "aws_default_region": self.stack.aws_default_region,
            "lambda_layers": self.stack.lambda_layers,
            "config0_lambda_execgroup_name": self.stack.lambda_iac_ci.name
        }

        # Create webhook function
        lambda_name = f"{self.stack.app_name}-process-webhook"
        handler = "app_webhook.handler"

        arguments = base_arguments.copy()
        arguments.update({
            "lambda_env_vars_hash": webhook_env_vars_hash,
            "lambda_name": lambda_name,
            "handler": handler
        })

        inputargs = {
            "arguments": arguments,
            "automation_phase": "infrastructure",
            "human_description": f"Create Lambda function {lambda_name}"
        }

        self.stack.py_lambda.insert(display=True, **inputargs)

        ##############################################################
        # debug777
        ##############################################################
        # Create additional Lambda functions
        #lambda_params = {
        #    f"{self.stack.app_name}-trigger-codebuild": "app_codebuild.handler",
        #    f"{self.stack.app_name}-pkgcode-to-s3": "app_s3.handler",
        #    f"{self.stack.app_name}-check-codebuild": "app_check_build.handler",
        #    f"{self.stack.app_name}-trigger-lambda": "app_lambda.handler",
        #    f"{self.stack.app_name}-update-pr": "app_pr.handler"
        #}

        #for lambda_name, handler in lambda_params.items():
        #    arguments = base_arguments.copy()
        #    arguments.update({
        #        "lambda_name": lambda_name,
        #        "handler": handler
        #    })

        #    inputargs = {
        #        "arguments": arguments,
        #        "automation_phase": "infrastructure",
        #        "human_description": f"Create Lambda function {lambda_name}"
        #    }

        #    self.stack.py_lambda.insert(display=True, **inputargs)
        ##############################################################

        self.stack.unset_parallel()

    def _init_common(self):
        """
        Initialize common variables required for the infrastructure setup.
        """
        self.stack.set_variable("lambda_bucket", self.stack.bucket_names["lambda"])
        self.stack.set_variable("remote_stateful_bucket", self.stack.bucket_names["stateful"])
        self.stack.set_variable("log_bucket", self.stack.bucket_names["log"])
        self.stack.set_variable("tmp_bucket", self.stack.bucket_names["tmp"])

        self.stack.set_variable("aws_default_region", "us-east-1")
        self.stack.set_variable("lambda_layers", f"arn:aws:lambda:{self.stack.aws_default_region}:553035198032:layer:git-lambda2:8")
        self.stack.set_variable("dynamodb_name_runs", f"{self.stack.app_name}-runs")
        self.stack.set_variable("dynamodb_name_settings", f"{self.stack.app_name}-settings")

    def run_setup(self):
        """
        Run the setup phase, which initializes variables and creates DynamoDB tables.

        Returns:
            bool: True if setup is successful.
        """
        self.stack.init_variables()
        self.stack.verify_variables()
        self._init_common()
        self._dynamodb(self._set_cloud_tag_hash())
        return True

    def run_lambda_stepf(self):
        """
        Run the phase to create Lambda functions and Step Functions.

        Returns:
            bool: True if successful.
        """
        self.stack.init_variables()
        self.stack.verify_variables()
        self._init_common()

        cloud_tags_hash = self._set_cloud_tag_hash()
        self.stack.unset_parallel()

        self._lambda(cloud_tags_hash)
        self._stepf(cloud_tags_hash)

        return True

    def run_trigger_stepf(self):
        """
        Run the phase to trigger the Step Function.

        Returns:
            None
        """
        self.stack.init_variables()
        self.stack.verify_variables()
        self._init_common()

        cloud_tags_hash = self._set_cloud_tag_hash()
        stepf_arn = self._get_stepf_arn()

        arguments = {
            "s3_bucket": self.stack.lambda_bucket,
            "runtime": self.stack.runtime,
            "policy_template_hash": self._get_stepf_policy_template_hash(),
            "lambda_env_vars_hash": self.stack.b64_encode({
                "DYNAMODB_TABLE_SETTINGS": self.stack.dynamodb_name_settings,
                "DYNAMODB_TABLE_RUNS": self.stack.dynamodb_name_runs,
                "STATE_MACHINE_ARN": stepf_arn
            }),
            "cloud_tags_hash": cloud_tags_hash,
            "aws_default_region": self.stack.aws_default_region,
            "lambda_layers": self.stack.lambda_layers
        }

        lambda_name = f"{self.stack.app_name}-lambda_trigger_stepf"
        handler = "app.handler"

        arguments.update({
            "lambda_name": lambda_name,
            "handler": handler,
            "config0_lambda_execgroup_name": self.stack.lambda_trigger_stepf.name
        })

        inputargs = {
            "arguments": arguments,
            "automation_phase": "infrastructure",
            "human_description": f"Create Lambda function {lambda_name}"
        }

        self.stack.py_lambda.insert(display=True, **inputargs)

    def run_apigw(self):
        """
        Run the phase to create an API Gateway.

        Returns:
            dict: API Gateway creation details.
        """
        self.stack.init_variables()
        self.stack.verify_variables()
        self._init_common()

        cloud_tags_hash = self._set_cloud_tag_hash()
        lambda_name = f"{self.stack.app_name}-lambda_trigger_stepf"

        arguments = {
            "apigateway_name": self.stack.app_name,
            "cloud_tags_hash": cloud_tags_hash,
            "lambda_name": lambda_name,
            "aws_default_region": self.stack.aws_default_region
        }

        inputargs = {
            "arguments": arguments,
            "automation_phase": "infrastructure",
            "human_description": f"Create API Gateway {self.stack.app_name}"
        }

        return self.stack.apigw.insert(display=True, **inputargs)

    def run_sns_subscription(self):
        """
        Run the phase to create an SNS subscription for CodeBuild.

        Returns:
            dict: SNS subscription creation details.
        """
        self.stack.init_variables()
        self.stack.verify_variables()
        self._init_common()

        lambda_name = f"{self.stack.app_name}-check-codebuild"
        topic_name = f"{self.stack.app_name}-codebuild-complete-trigger"

        cloud_tags_hash = self._set_cloud_tag_hash()

        arguments = {
            "lambda_name": lambda_name,
            "cloud_tags_hash": cloud_tags_hash,
            "topic_name": topic_name,
            "aws_default_region": self.stack.aws_default_region
        }

        inputargs = {
            "arguments": arguments,
            "automation_phase": "infrastructure",
            "human_description": f"Codebuild SNS subscription {self.stack.app_name}"
        }

        return self.stack.sns_subscription.insert(display=True, **inputargs)

    def run(self):
        """
        Define and execute the sequence of job steps required for the infrastructure setup.

        Returns:
            dict: Finalized details of all executed jobs.
        """
        self.stack.unset_parallel(sched_init=True)
        self.add_job("setup")
        self.add_job("lambda_stepf")
        self.add_job("trigger_stepf")
        self.add_job("apigw")
        self.add_job("sns_subscription")

        return self.finalize_jobs()

    def schedule(self):
        # Schedule for "setup" job
        sched = self.new_schedule()
        sched.job = "setup"
        sched.archive.timeout = 1800
        sched.archive.timewait = 120
        sched.automation_phase = "infrastructure"
        sched.human_description = "Setup S3 and DynamoDB"
        sched.conditions.retries = 1
        sched.on_success = ["lambda_stepf"]
        self.add_schedule()
    
        # Schedule for "lambda_stepf" job
        sched = self.new_schedule()
        sched.job = "lambda_stepf"
        sched.archive.timeout = 2700
        sched.archive.timewait = 120
        sched.automation_phase = "infrastructure"
        sched.human_description = "Setup Lambdas and Step Functions"
        sched.on_success = ["trigger_stepf"]
        self.add_schedule()
    
        # Schedule for "trigger_stepf" job
        sched = self.new_schedule()
        sched.job = "trigger_stepf"
        sched.archive.timeout = 1200
        sched.archive.timewait = 120
        sched.automation_phase = "infrastructure"
        sched.human_description = "Create Lambda Trigger for Step Function"
        sched.on_success = ["apigw"]
        self.add_schedule()
    
        # Schedule for "apigw" job
        sched = self.new_schedule()
        sched.job = "apigw"
        sched.archive.timeout = 1200
        sched.archive.timewait = 120
        sched.automation_phase = "infrastructure"
        sched.human_description = "Create API Gateway"
        sched.on_success = ["sns_subscription"]
        self.add_schedule()
    
        # Schedule for "sns_subscription" job
        sched = self.new_schedule()
        sched.job = "sns_subscription"
        sched.archive.timeout = 1200
        sched.archive.timewait = 120
        sched.automation_phase = "infrastructure"
        sched.human_description = "Create CodeBuild Complete Trigger"
        self.add_schedule()
    
        return self.get_schedules()
