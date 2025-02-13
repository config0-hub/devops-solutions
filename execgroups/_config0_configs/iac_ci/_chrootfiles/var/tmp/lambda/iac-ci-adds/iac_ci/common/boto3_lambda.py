#!/usr/bin/env python

import json
from iac_ci.common.loggerly import IaCLogger
from iac_ci.common.boto3_common import Boto3Common

class LambdaBoto3(Boto3Common):
    """
    A class for interacting with AWS Lambda functions using boto3.
    Inherits from Boto3Common for AWS connectivity.

    This class provides functionality to invoke Lambda functions asynchronously.
    """

    def __init__(self,**kwargs):
        """
        Initialize LambdaBoto3 instance.

        Args:
            **kwargs: Arbitrary keyword arguments passed to parent class
        """
        self.classname = 'LambdaBoto3'
        self.logger = IaCLogger(self.classname)
        self.logger.debug(f"Instantiating {self.classname}")
        Boto3Common.__init__(self,'lambda',**kwargs)

    def run(self,**kwargs):
        """
        Invoke a Lambda function asynchronously.

        Args:
            **kwargs: Must contain:
                name (str): Name or ARN of the Lambda function
                message (dict): Payload to send to the Lambda function

        Returns:
            dict: AWS Lambda invoke response object

        Note:
            The function is invoked with 'Event' invocation type, 
            meaning it's asynchronous and doesn't wait for the function to complete.
        """
        name = kwargs["name"]
        message = kwargs["message"]

        return self.client.invoke(
            FunctionName=name,
            InvocationType='Event',
            Payload=json.dumps(message)
        )
