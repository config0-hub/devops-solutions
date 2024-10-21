from xml.dom.pulldom import default_bufsize


class Main(newSchedStack):

    def __init__(self, stackargs):

        newSchedStack.__init__(self, stackargs)

        self.parse.add_required(key="app_name",
                                types="str",
                                default="iac-ci-config0")

        self.parse.add_optional(key="cloud_tags_hash",
                                types="str")

        self.parse.add_optional(key="runtime",
                                types="str",
                                default="python3.9")

        ########################################################################################
        # testtest456 - need to implement the two here
        ########################################################################################
        # these should already exists to execute terraform/shell scripts
        # with the right roles and permissions
        self.parse.add_optional(key="codebuild_tf_project_name",
                                types="str",
                                default="config0-iac")

        self.parse.add_optional(key="lambda_tf_project_name",
                                types="str",
                                default="config0-iac")
        ########################################################################################

        self.stack.add_substack("config0-publish:::aws_dynamodb")
        self.stack.add_substack("config0-publish:::apigw_lambda-integ","apigw")
        self.stack.add_substack("config0-publish:::aws-lambda-python-codebuild","py_lambda")

        self.stack.add_substack("config0-publish:::iac_ci_stepf")
        self.stack.add_substack("config0-publish:::iac_ci_complete_trigger",
                                "sns_subscription")

        # this is lock versioning of execgroups
        self.stack.add_execgroup("config0-publish:::github::lambda_trigger_stepf")
        self.stack.add_execgroup("config0-publish:::devops-solutions::iac_ci","lambda_iac_ci")

        self.stack.init_execgroups()
        self.stack.init_substacks()

    def _set_cloud_tag_hash(self):

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

        base_hash = self.stack.b64_encode({"ENV": "build"})

        # this setting is for
        # processing the webhook
        env_vars = {
            "ENV": "build",
            "DEBUG_LAMBDA": "true",
            "BUILD_TTL": "60"
        }

        webhook_hash = self.stack.b64_encode(env_vars)

        return base_hash, webhook_hash

    def _dynamodb(self,cloud_tags_hash):

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
                "human_description": f"Create dynamodb {dynamodb_name}"
            }

            self.stack.aws_dynamodb.insert(display=True,
                                           **inputargs)

    def _get_log_policy(self):

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

        arn_dynamodb_name_runs = f"arn:aws:dynamodb:{self.stack.aws_default_region}:" + '${aws_account_id}:table/' + self.stack.dynamodb_name_runs
        arn_dynamodb_name_settings = f"arn:aws:dynamodb:{self.stack.aws_default_region}:" + '${aws_account_id}:table/' + self.stack.dynamodb_name_settings

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

        # testtest456 - need to update this
        arn_s3_bucket = f"arn:aws:s3:::{self.stack.remote_stateful_bucket}"
        arn_s3_bucket_lambda = f"arn:aws:s3:::{self.stack.lambda_bucket}"
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
                f"{arn_s3_bucket}/*",
                f"{arn_s3_bucket_lambda}/*",
                f"{arn_s3_bucket_tmp}/*"
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

    def _get_lambda_policy(self):

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

        _statement = {"Action": _action,
                      "Resource": "*",
                      "Effect": "Allow"
                      }

        return _statement

    def _get_codebuild_policy(self):

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

        _statement = {"Action": _action,
                      "Resource": "*",
                      "Effect": "Allow"
                      }

        return _statement

    def _get_stepf_policy(self):
        
        _action = [
            "states:StartExecution",
            "states:StopExecution",
            "states:DescribeExecution",
            "states:ListExecutions",
            "states:DescribeStateMachine",
            "states:GetExecutionHistory"
        ]

        _statement = {"Action": _action,
                      "Resource": "*",
                      "Effect": "Allow"
                      }

        return _statement

    def _get_policy_template_hash(self):

        statements = []

        _statement = {"Action": ["ssm:*"],
                      "Resource": "*",
                      "Effect": "Allow"
                      }

        statements.append(_statement)
        statements.append(self._get_log_policy())
        statements.append(self._get_dynamodb_policy())
        statements.extend(self._get_s3_policies())

        # testtest456
        # need to update
        statements.append(self._get_lambda_policy())
        statements.append(self._get_codebuild_policy())

        policy = {"Version": "2012-10-17",
                  "Statement": statements}

        return self.stack.b64_encode(policy,
                                     json_dumps=True)

    def _get_stepf_policy_template_hash(self):

        statements = [self._get_log_policy()]
        statements.extend(self._get_s3_policies())
        statements.append(self._get_dynamodb_policy())
        statements.append(self._get_lambda_policy())
        statements.append(self._get_stepf_policy())

        policy = {"Version": "2012-10-17",
                  "Statement": statements}

        return self.stack.b64_encode(policy,
                                     json_dumps=True)

    def _get_stepf_name(self):
         return f"{self.stack.app_name}-stepf-ci"

    def _get_stepf_arn(self):

        stepf_name = self._get_stepf_name()

        _info = self.stack.get_resource(name=stepf_name,
                                        resource_type="step_function",
                                        must_be_one=True)[0]

        return _info["arn"]

    def _stepf(self,cloud_tags_hash):

        stepf_name = self._get_stepf_name()

        arguments = {
            "step_function_name": stepf_name,
            "cloud_tags_hash": cloud_tags_hash,
            "aws_default_region": self.stack.aws_default_region
        }

        inputargs = {
            "arguments": arguments,
            "automation_phase": "infrastructure",
            "human_description": f"Create step function {stepf_name}"
        }

        self.stack.iac_ci_stepf.insert(display=True,
                                                 **inputargs)

        return

    def _lambda(self,cloud_tags_hash):

        #self.stack.unset_parallel()
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

        ###########################################################################
        # create the first function with py_lambda
        ###########################################################################
        lambda_name = f"{self.stack.app_name}-process-webhook"
        handler = "app_webhook.handler"

        arguments = base_arguments.copy()

        arguments.update({
            "lambda_env_vars_hash": webhook_env_vars_hash,   # this is special for the processing of the webhook
            "lambda_name": lambda_name,
            "handler": handler
        })


        inputargs = {
            "arguments": arguments,
            "automation_phase": "infrastructure",
            "human_description": f"Create lambda function {lambda_name}"
        }

        self.stack.py_lambda.insert(display=True,
                                    **inputargs)

        # call tf lambda now the lambda function has been uploaded
        #self.stack.set_parallel()

        lambda_params = {
                f"{self.stack.app_name}-trigger-codebuild":"app_codebuild.handler",
                f"{self.stack.app_name}-pkgcode-to-s3":"app_s3.handler",
                f"{self.stack.app_name}-check-codebuild":"app_check_build.handler",
                f"{self.stack.app_name}-trigger-lambda":"app_lambda.handler",
                f"{self.stack.app_name}-update-pr":"app_pr.handler"
        }

        for lambda_name, handler in lambda_params.items():
            arguments = base_arguments.copy()
            arguments.update({
                "lambda_name": lambda_name,
                "handler": handler
            })

            inputargs = {
                "arguments": arguments,
                "automation_phase": "infrastructure",
                "human_description": f'Create lambda function {lambda_name}'
            }

            self.stack.py_lambda.insert(display=True,
                                        **inputargs)

        self.stack.unset_parallel()

    def _init_common(self):

        self.stack.set_variable("lambda_bucket",
                                self.stack.bucket_names["lambda"])

        self.stack.set_variable("remote_stateful_bucket",
                                self.stack.bucket_names["stateful"])

        self.stack.set_variable("tmp_bucket",
                                self.stack.bucket_names["tmp"])

        # we need to hardwire to us-east-1 since
        # the existing config0 workers ("config0-iac")
        # are by default deployed to us-east-1
        self.stack.set_variable("aws_default_region",
                                "us-east-1")

        self.stack.set_variable("lambda_layers",
                                f"arn:aws:lambda:{self.stack.aws_default_region}:553035198032:layer:git-lambda2:8")

        self.stack.set_variable("dynamodb_name_runs",f"{self.stack.app_name}-runs")
        self.stack.set_variable("dynamodb_name_settings",f"{self.stack.app_name}-settings")

    def run_setup(self):

        self.stack.init_variables()
        self.stack.verify_variables()
        self._init_common()

        # create dynamodb table
        self._dynamodb(self._set_cloud_tag_hash())

        return True

    def run_lambda_stepf(self):

        self.stack.init_variables()
        self.stack.verify_variables()
        self._init_common()

        cloud_tags_hash = self._set_cloud_tag_hash()

        self.stack.unset_parallel()

        # create lambda functions
        self._lambda(cloud_tags_hash)

        # create step function after lambda funcs
        self._stepf(cloud_tags_hash)

        return True

    def run_trigger_stepf(self):

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
                "DYNAMODB_TABLE":self.stack.dynamodb_name_runs,
                "STATE_MACHINE_ARN":stepf_arn
            }),
            "cloud_tags_hash": cloud_tags_hash,
            "aws_default_region": self.stack.aws_default_region,
            "lambda_layers":self.stack.lambda_layers
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
            "human_description": f"Create lambda function {lambda_name}"
        }

        self.stack.py_lambda.insert(display=True,
                                    **inputargs)

    def run_apigw(self):

        self.stack.init_variables()
        self.stack.verify_variables()
        self._init_common()

        cloud_tags_hash = self._set_cloud_tag_hash()

        # trigger the lambda function
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
            "human_description": f'Create API gateway {self.stack.app_name}'
        }

        return self.stack.apigw.insert(display=True,
                                       **inputargs)

    def run_sns_subscription(self):

        self.stack.init_variables()
        self.stack.verify_variables()
        self._init_common()

        lambda_name = f"{self.stack.app_name}-check-codebuild"
        topic_name = f"{self.stack.app_name}-codebuild-compelete-trigger"

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

        return self.stack.sns_subscription.insert(display=True, 
                                                  **inputargs)

    def run(self):

        self.stack.unset_parallel(sched_init=True)
        self.add_job("setup")
        self.add_job("lambda_stepf")
        self.add_job("trigger_stepf")
        self.add_job("apigw")
        self.add_job("sns_subscription")

        return self.finalize_jobs()

    def schedule(self):

        sched = self.new_schedule()
        sched.job = "setup"
        sched.archive.timeout = 1800
        sched.archive.timewait = 120
        sched.conditions.retries = 1
        sched.automation_phase = "infrastructure"
        sched.human_description = "Setup dynamodb"
        sched.on_success = ["lambda_stepf"]
        self.add_schedule()

        sched = self.new_schedule()
        sched.job = "lambda_stepf"
        sched.archive.timeout = 1800
        sched.archive.timewait = 120
        sched.automation_phase = "infrastructure"
        sched.human_description = "Setup lambdas and stepf"
        sched.on_success = ["trigger_stepf"]
        self.add_schedule()

        sched = self.new_schedule()
        sched.job = "trigger_stepf"
        sched.archive.timeout = 1200
        sched.archive.timewait = 120
        sched.automation_phase = "infrastructure"
        sched.human_description = 'Create Lambda Trigger Step function'
        sched.on_success = ["apigw"]
        self.add_schedule()

        sched = self.new_schedule()
        sched.job = "apigw"
        sched.archive.timeout = 1200
        sched.archive.timewait = 120
        sched.automation_phase = "infrastructure"
        sched.human_description = 'Create apigateway'
        sched.on_success = ["sns_subscription"]
        self.add_schedule()

        sched = self.new_schedule()
        sched.job = "sns_subscription"
        sched.archive.timeout = 1200
        sched.archive.timewait = 120
        sched.automation_phase = "infrastructure"
        sched.human_description = 'Create Codebuild Complete Trigger'
        self.add_schedule()

        return self.get_schedules()
