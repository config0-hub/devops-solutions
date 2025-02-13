#!/usr/bin/env python

from iac_ci.helper.cloud.lambda_helper import LambdaHandler
from iac_ci.helper.cloud.lambda_helper import return_thru_lambda
from main_pr import GitPr as Main

def handler(event, context):

    lambda_handler = LambdaHandler(event)
    message = lambda_handler.get_init_msg()

    main = Main(**message)
    results = main.run()

    return return_thru_lambda(results)

