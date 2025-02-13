#!/usr/bin/env python
#
import boto3
import os

from iac_ci.common.loggerly import IaCLogger

class Boto3Common(object):

    def __init__(self, product, **kwargs):

        self.classname = 'Boto3Common'
        self.logger = IaCLogger(self.classname)
        self.logger.debug(f"Instantiating {self.classname}")

        self.aws_default_region = None
        self.region = None
        self.product = product

        self.set_region(**kwargs)

        inputargs = self._get_boto3_inputargs(**kwargs)

        self.client = boto3.client(self.product, **inputargs)

        resource_products = [ "cloudformation",
                              "cloudwatch",
                              "dynamodb",
                              "ec2",
                              "glacier",
                              "iam",
                              "opsworks",
                              "s3",
                              "sns",
                              "sqs" ]

        if self.product in resource_products:
            self.resource = boto3.resource(self.product, **inputargs)
        else:
            self.resource = None


    def _get_boto3_inputargs(self, **kwargs):
        """
        Constructs a dictionary of input arguments for boto3 client/resource initialization.

        This function gathers AWS credentials and region information from the provided keyword arguments
        or environment variables, and returns them in a dictionary format suitable for boto3 client/resource
        initialization.

        Parameters:
        kwargs: dict
            A dictionary of keyword arguments that may contain AWS credentials and region information.
            - aws_access_key_id: str, optional
                The AWS access key ID.
            - aws_secret_access_key: str, optional
                The AWS secret access key.
            - aws_session_token: str, optional
                The AWS session token.
            - get_creds_frm_role: bool, optional
                If True, indicates that credentials should be obtained from a role, and the function
                will return an empty dictionary.

        Returns:
        dict
            A dictionary containing the AWS credentials and region information. The keys may include:
            - 'aws_access_key_id': The AWS access key ID.
            - 'aws_secret_access_key': The AWS secret access key.
            - 'aws_session_token': The AWS session token.
            - 'region_name': The AWS region name.
        """
        if kwargs.get("get_creds_frm_role"):
            return {}

        keys2pass = [ "aws_access_key_id",
                      "aws_secret_access_key",
                      "aws_session_token" ]

        inputargs = {_key: kwargs[_key] for _key in keys2pass if kwargs.get(_key)}
        
        if not inputargs.get("aws_access_key_id") and os.environ.get("AWS_ACCESS_KEY_ID"):
            self.logger.debug(
                f'Getting AWS_ACCESS_KEY_ID {os.environ["AWS_ACCESS_KEY_ID"]} from environmental variable AWS_ACCESS_KEY_ID'
            )
            inputargs["aws_access_key_id"] = os.environ["AWS_ACCESS_KEY_ID"]

        if not inputargs.get("aws_secret_access_key") and os.environ.get("AWS_SECRET_ACCESS_KEY"):
            self.logger.debug("Getting AWS_SECRET_ACCESS_KEY from environmental variable AWS_SECRET_ACCESS_KEY")
            inputargs["aws_secret_access_key"] = os.environ["AWS_SECRET_ACCESS_KEY"]

        inputargs["region_name"] = self.aws_default_region
        self.logger.debug(f"Using aws region: {self.aws_default_region}")

        if not inputargs.get("aws_session_token") and os.environ.get("AWS_SESSION_TOKEN"):
            inputargs["aws_session_token"] = os.environ["AWS_SESSION_TOKEN"]

        return inputargs

    def set_region(self, **kwargs):

        self.aws_default_region = kwargs.get("aws_default_region")

        if not self.aws_default_region and os.environ.get("AWS_DEFAULT_REGION"): 
            self.aws_default_region = os.environ["AWS_DEFAULT_REGION"]
        
        if not self.aws_default_region:
            self.aws_default_region = "us-east-1"

        self.region = self.aws_default_region
