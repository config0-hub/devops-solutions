#!/usr/bin/env python
from main_webhook import WebhookProcess as Main
from iac_ci.common.loggerly import IaCLogger
import json
import os

def handler(event, context):

    classname = 'handler'
    logger = IaCLogger(classname)

    if event["httpMethod"] == "POST":
        if event["body"] and not isinstance(event["body"],dict):
            try:
                event_body = json.loads(event["body"])
            except Exception as e:
                logger.error(e)
                raise e
        elif event["body"] and isinstance(event["body"],dict):
            event_body = event["body"]
        else:
            return {
                "statusCode": 400,
                "body": json.dumps("No json event_body provided...")
            }
    else:
        return {
            "statusCode": 405,
            "body": json.dumps(f"Invalid HTTP Method {event['httpMethod']} supplied")
        }

    if os.environ.get("DEBUG_IAC_CI"):
        event["body"] = event_body
        logger.debug("\n"+json.dumps(event,indent=4)+"\n")

    trigger_id = event["path"].split("/")[-1]

    main = Main(trigger_id=trigger_id,
                headers=event["headers"],
                event_body=event_body)

    results = main.run()

    return {
        'statusCode': 200,
        'continue':results["continue"],
        'apply':results.get("apply"),
        'destroy':results.get("destroy"),
        'check':results.get("check"),
        'body': json.dumps(results)
    }