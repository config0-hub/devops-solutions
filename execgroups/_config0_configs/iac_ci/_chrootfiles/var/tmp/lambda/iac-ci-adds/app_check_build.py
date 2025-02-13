#!/usr/bin/env python

import json
from iac_ci.helper.cloud.lambda_helper import LambdaHandler
from iac_ci.helper.cloud.lambda_helper import return_thru_lambda
from main_check_build import CheckBuild as Main

def handler(event, context):

    lambda_handler = LambdaHandler(event)

    if "body" in lambda_handler.event:
        try:
            message = json.loads(lambda_handler.event['body'])
        except Exception as e:
            message = event
    else:
        _init_msg = lambda_handler.get_init_msg()
        if lambda_handler.sns_event:
            message = {
                "phase": "check_build",
                "build_status": _init_msg["detail"]["build-status"],
                "build_arn": _init_msg["detail"]["build-id"]
            }
            message["build_id"] = message["build_arn"].split("/")[-1]
        else:
            message = _init_msg

    main = Main(**message)
    results = main.run()

    return return_thru_lambda(results)