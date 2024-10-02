from xml.dom.pulldom import default_bufsize


class Main(newSchedStack):

    def __init__(self, stackargs):

        newSchedStack.__init__(self, stackargs)

        # Add default variables
        ########################################################################################
        # testtest456 # insert from resource cmd or something?
        ########################################################################################
        self.parse.add_optional(key="tmp_bucket",
                                default="null")

        self.parse.add_optional(key="lambda_bucket",
                                default="null")

        self.parse.add_optional(key="remote_stateful_bucket",
                                default="null")
        ########################################################################################

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

        self.stack.add_substack('config0-publish:::github_webhook')
        self.stack.add_substack('config0-publish:::aws_dynamodb_item','dynamodb_item')
        self.stack.add_substack('config0-publish:::aws_ssm_param')
        self.stack.add_substack('config0-publish:::new_github_ssh_key')
        self.stack.add_substack("config0-publish:::aws_dynamodb")
        self.stack.add_substack("config0-publish:::apigw_lambda-integ","apigw")
        self.stack.add_substack("config0-publish:::aws-lambda-python-codebuild","py_lambda")

        #########################################################################
        # update
        #########################################################################
        self.stack.add_substack("config0-publish:::iac_ci_stepf")
        self.stack.add_substack("config0-publish:::iac_ci_complete_trigger",
                                "sns_subscription")

        # this is lock versioning of execgroups
        self.stack.add_execgroup("config0-publish:::github::lambda_trigger_stepf")
        self.stack.add_execgroup("config0-publish:::devops-solutions::iac_ci","lambda_iac_ci")
        #########################################################################

        self.stack.init_execgroups()
        self.stack.init_substacks()

    def _get_app_name(self):
        return "iac-ci-config0"

    def _get_token(self):

        _lookup = {"must_be_one": True,
                   "resource_type": "config0_token",
                   "provider": "config0",
                   "name": self._get_app_name()}

        return str(self.stack.get_resource(**_lookup)[0]["token"])

    def _token(self):
        return self.stack.create_token(name=self._get_app_name())

    def _set_cloud_tag_hash(self):

        try:
            cloud_tags = self.stack.b64_decode(self.stack.cloud_tags_hash)
        except:
            cloud_tags = {}

        cloud_tags.update({
            "environment": "iac-ci",
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
            self.stack.dynamodb_name_settings
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
                "logs:PutLogEvents"
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

        arn_s3_bucket = f"arn:aws:s3:::{self.stack.tmp_bucket}"
        arn_s3_bucket_lambda = f"arn:aws:s3:::{self.stack.lambda_bucket}"
        arn_s3_bucket_tmp = f"arn:aws:s3:::{self.stack.remote_stateful_bucket}-tmp"

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
        statements.append(self._get_lambda_policy())
        statements.append(self._get_stepf_policy())

        policy = {"Version": "2012-10-17",
                  "Statement": statements}

        return self.stack.b64_encode(policy,
                                     json_dumps=True)

    def _get_stepf_name(self):
         return f"iac_ci-stepf-ci"

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
        lambda_name = "iac-ci-process-webhook"
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
                "iac-ci-trigger-codebuild":"app_codebuild.handler",
                "iac-ci-pkgcode-to-s3":"app_s3.handler",
                "iac-ci-check-codebuild":"app_check_build.handler",
                "iac-ci-trigger-lambda":"app_lambda.handler",
                "iac-ci-update-pr":"app_pr.handler"
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

        #self.stack.set_variable("ssm_github_token",
        #                        "/iac-ci/config0/github_token")

    def _set_buckets(self):

        if not self.stack.lambda_bucket:
            self.stack.set_variable("lambda_bucket",
                                    self.stack.bucket_names["lambda"])

        if not self.stack.remote_stateful_bucket:
            self.stack.set_variable("remote_stateful_bucket",
                                    self.stack.bucket_names["stateful"])

        if not self.stack.tmp_bucket:
            self.stack.set_variable("tmp_bucket",
                                    self.stack.bucket_names["tmp"])

    def _set_misc(self):

        # we need to hardwire to us-east-1 since
        # the existing config0 workers ("config0-iac")
        # are by default deployed to us-east-1
        self.stack.set_variable("aws_default_region",
                                "us-east-1")

        self.stack.set_variable("lambda_layers",
                                f"arn:aws:lambda:{self.stack.aws_default_region}:553035198032:layer:git-lambda2:8")

        _secret = self.stack.get_hash(f'{self.stack.tmp_bucket}.{self.stack.lambda_bucket}.{self.stack.remote_stateful_bucket}')

        self.stack.set_variable("secret",_secret)
        self.stack.set_variable("dynamodb_name_runs","iac_ci-runs")
        self.stack.set_variable("dynamodb_name_settings","iac_ci-settings")

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
                                "/iac-ci/config0/iac_ci_github_token")

    def _set_slack_webhook(self):

        self.stack.set_variable("slack_webhook_hash",
                                self.stack.inputvars.get("slack_webhook_hash"),
                                types="str")

        if self.stack.get_attr("slack_webhook_hash"):
            self.stack.set_variable("ssm_slack_webhook_hash",
                                    "/iac-ci/config0/slack_webhook_hash")
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
                                    "/iac-ci/config0/infracost_api_key")
        else:
            self.stack.set_variable("ssm_infracost_api_key",None)

    def _get_api_url(self):

        import os

        apigateway_name = self._get_app_name()

        _lookup = {
            "must_be_one": True,
            "resource_type": "apigateway_restapi_lambda",
            "provider": "aws",
            "name": apigateway_name}

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
            "name": self._get_app_name(),
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
            "name": self._get_app_name()
            }

        return self.stack.get_resource(decrypt=True,
                                       **_lookup)[0]["private_key"]

    def _sshdeploy(self):

        key_name = self._get_app_name()

        arguments = {
            "key_name": key_name,
            "aws_default_region": self.stack.aws_default_region,
            "repo": self.stack.iac_ci_repo
        }

        inputargs = {
            "arguments": arguments,
            "automation_phase": "continuous_delivery",
            "human_description": f'Create deploy key "{key_name}"'
        }

        return self.stack.new_github_ssh_key.insert(display=True,
                                                    **inputargs)

    def _ssm(self):

        self._add_ssm_callback_token()
        self._add_ssm_ssh_key()
        self._add_ssm_iac_ci_github_token()
        self._add_ssm_slack()
        self._add_ssm_infracost()
        #self._add_ssm_github_token()

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

    #def _add_ssm_github_token(self):

    #    if not self.stack.get_attr("github_token"):
    #        return

    #    arguments={
    #        "ssm_key": self.stack.ssm_github_token,
    #        "ssm_value": self.stack.github_token,
    #        "aws_default_region": self.stack.aws_default_region
    #    }

    #    inputargs={"arguments": arguments,
    #               "automation_phase": "continuous_delivery",
    #               "human_description": "Github token to ssm"}

    #    self.stack.aws_ssm_param.insert(display=True,**inputargs)

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
            "human_description": f'Add setting item for iac ci {self._get_app_name()}'
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

        values["name"] = "iac_ci"
        inputargs["name"] = "iac_ci"

        self.stack.add_resource(values=values,
                                **inputargs)

    def run_connect_repo(self):

        self.stack.init_variables()
        self.stack.verify_variables()
        self._init_common()
        self.stack.set_variable("trigger_id",
                                self.stack.random_id())
        self.stack.set_parallel()

        self._add_iac_ci_to_db()
        self._ssm()
        self._webhook()
        return self._dynamodb_item()

    def run_setup(self):

        self.stack.init_variables()
        self.stack.verify_variables()
        self._init_common()
        self.stack.set_parallel()

        self._dynamodb(self._set_cloud_tag_hash())
        self._sshdeploy()
        self._token()

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
                "STATE_MACHINE_ARN":stepf_arn
            }),
            "cloud_tags_hash": cloud_tags_hash,
            "aws_default_region": self.stack.aws_default_region,
            "lambda_layers":self.stack.lambda_layers
        }

        # lambda_name = "lambda_trigger_stepf"
        lambda_name = "lambda_trigger_stepf"
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

        apigateway_name = self._get_app_name()

        # trigger the lambda function
        lambda_name = "lambda_trigger_stepf"

        arguments = {
            "apigateway_name": apigateway_name,
            "cloud_tags_hash": cloud_tags_hash,
            "lambda_name": lambda_name,
            "aws_default_region": self.stack.aws_default_region
        }

        inputargs = {
            "arguments": arguments,
            "automation_phase": "infrastructure",
            "human_description": f'Create API gateway {apigateway_name}'
        }

        return self.stack.apigw.insert(display=True,
                                       **inputargs)

    def run_sns_subscription(self):

        self.stack.init_variables()
        self.stack.verify_variables()
        self._init_common()

        lambda_name = "iac-ci-check-codebuild"
        topic_name = f"iac-ci-codebuild-compelete-trigger"

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
            "human_description": "Codebuild SNS subscription iac-ci"
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
        self.add_job("connect_repo")

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
        sched.on_success = ["connect_repo"]
        self.add_schedule()

        sched = self.new_schedule()
        sched.job = "connect_repo"
        sched.archive.timeout = 1200
        sched.archive.timewait = 120
        sched.automation_phase = "continuous_delivery"
        sched.human_description = "Connect repo with api gateway"
        self.add_schedule()

        return self.get_schedules()