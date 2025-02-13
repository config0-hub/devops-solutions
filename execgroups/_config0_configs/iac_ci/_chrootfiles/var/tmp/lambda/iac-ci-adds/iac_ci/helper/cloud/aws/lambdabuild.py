#!/usr/bin/env python
"""
Module for managing AWS Lambda build processes and executions.
This module provides functionality to handle Lambda function invocations,
environment variable management, and build result processing.
"""

import os
import logging
import boto3
import botocore
import json
from time import time

from iac_ci.common.loggerly import IaCLogger
from iac_ci.common.serialization import b64_encode
from iac_ci.common.serialization import b64_decode

class LambdaResourceHelper:
    """
    Helper class for managing AWS Lambda resources and build processes.
    
    This class handles Lambda function invocations, manages build environments,
    processes build results, and provides utilities for Lambda execution monitoring.
    
    Attributes:
        classname (str): Name of the class for logging purposes
        logger (IaCLogger): Logger instance for the class
    """
    def __init__(self, **kwargs):
        """
        Initialize LambdaResourceHelper with build configuration.
        
        Args:
            **kwargs: Dictionary containing build configuration including:
                build_env_vars (dict): Environment variables for the build
                aws_region (str): AWS region for Lambda execution
                build_timeout (int): Timeout in seconds for the build
                method (str): Build method to execute
        """
        self.classname = "LambdaResourceHelper"
        self.logger = IaCLogger(self.classname)

        self.iac_platform = os.environ.get("IAC_PLATFORM", "config0")

        if self.iac_platform == "config0":
            self.lambda_function_name = f"{self.iac_platform}-iac"
        elif self.iac_platform == "iac-ci":
            self.lambda_function_name = "iac-ci"
        else:
            self.lambda_function_name = "iac-ci"

        self.build_env_vars = kwargs["build_env_vars"]
        self.aws_region = kwargs["aws_region"]
        self.build_timeout = kwargs["build_timeout"]
        self.method = kwargs["method"]

        logging.basicConfig()
        logging.getLogger('botocore').setLevel(logging.WARNING)
        logging.getLogger('botocore.hooks').setLevel(logging.WARNING)
        logging.getLogger('botocore.session').setLevel(logging.WARNING)
        logging.getLogger('boto3.resources.action').setLevel(logging.WARNING)
        logging.getLogger('s3transfer').setLevel(logging.WARNING)
        logging.getLogger('s3transfer.utils').setLevel(logging.WARNING)
        logging.getLogger('s3transfer.tasks').setLevel(logging.WARNING)
        logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)

        self.s3 = boto3.resource('s3')
        self.session = boto3.Session(region_name=self.aws_region)

        cfg = botocore.config.Config(retries={'max_attempts': 0},
                                     read_timeout=900,
                                     connect_timeout=900,
                                     region_name=self.aws_region)

        self.lambda_client = boto3.client('lambda',
                                          config=cfg,
                                          region_name=self.aws_region)

        self.cmds_b64 = b64_encode(kwargs["cmds"])
        self.logs_client = self.session.client('logs')

        self.results = {
            "status": None,
            "status_code": None,
            "build_status": None,
            "run_t0": int(time()),
            "inputargs": {},
            "env_vars": {},
        }

        if not self.results["inputargs"].get("lambda_function_name"):
            self.results["inputargs"]["lambda_function_name"] = self.lambda_function_name

    @staticmethod
    def get_set_env_vars():
        """
        Get the environment variables for the Lambda function.

        Returns:
            dict: A dictionary of environment variables for the Lambda function.
        """
        return {
            "tmp_bucket": True,
            "log_bucket": True,
            "app_dir": None,
            "stateful_id": None,
            "remote_stateful_bucket": None,
            "lambda_function_name": None,
            "run_share_dir": None,
            "share_dir": None
        }

    def _trigger_build(self):
        """
        Trigger the build process by invoking the Lambda function.

        Returns:
            dict: The response from the Lambda function invocation.
        """
        try:
            timeout = int(self.build_timeout)
        except Exception:
            timeout = 600

        if timeout > 600:
            timeout = 600

        self.build_expire_at = time() + timeout

        self.logger.debug("#" * 32)
        self.logger.debug("# ref 324523453 env vars for lambda build")
        self.logger.json(self.build_env_vars)
        self.logger.debug("#" * 32)

        invocation_config = {'FunctionName': f'{self.lambda_function_name}',
            'InvocationType': 'RequestResponse',
            'LogType': 'Tail',
            'Payload': json.dumps(
                {
                    "cmds_b64": self.cmds_b64,
                    "env_vars_b64": b64_encode(self.build_env_vars),
                })
        }

        return self.lambda_client.invoke(**invocation_config)

    def _submit(self):
        """
        Submit the build request and process the response.

        Returns:
            dict: The results of the build submission.
        """
        # ['ResponseMetadata', 'StatusCode', 'LogResult', 'ExecutedVersion', 'Payload']
        self.response = self._trigger_build()

        lambda_status = int(self.response["StatusCode"])
        self.results["lambda_status"] = lambda_status

        payload = json.loads(self.response["Payload"].read().decode())

        try:
            lambda_results = json.loads(payload["body"])
        except Exception:
            lambda_results = payload
            lambda_results["status"] = False
            self.results["failed_message"] = " ".join(lambda_results["stackTrace"])
            self.results["output"] = " ".join(lambda_results["stackTrace"])

        self.results["lambda_results"] = lambda_results

        if lambda_results["status"] is True and lambda_status == 200:
            self.results["status"] = lambda_results["status"]
            self.results["exitcode"] = 0
        elif lambda_status != 200:
            self.results["status"] = False
            self.results["exitcode"] = "78"
            if not self.results.get("failed_message"):
                self.results["failed_message"] = "lambda function failed"
        else:
            self.results["status"] = False
            self.results["exitcode"] = "79"
            if not self.results.get("failed_message"):
                self.results["failed_message"] = "execution of cmd in lambda function failed"

        if not self.results.get("output"):
            self.results["output"] = b64_decode(self.response["LogResult"])

        return self.results

    def submit(self):
        """
        Submit the build process and handle the results.

        Returns:
            dict: The results of the build submission.
        """
        self._submit()

        if self.results.get("status") is False and self.method == "validate":
            self.results["failed_message"] = "the resources have drifted"
        elif self.results.get("status") is False and self.method == "check":
            self.results["failed_message"] = "the resources failed check"
        elif self.results.get("status") is False and self.method == "pre-create":
            self.results["failed_message"] = "the resources failed pre-create"
        elif self.results.get("status") is False and self.method == "apply":
            self.results["failed_message"] = "applying of resources have failed"
        elif self.results.get("status") is False and self.method == "create":
            self.results["failed_message"] = "creation of resources have failed"
        elif self.results.get("status") is False and self.method == "destroy":
            self.results["failed_message"] = "destroying of resources have failed"

        return self.results
