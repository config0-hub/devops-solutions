#!/usr/bin/env python
"""
Module for handling AWS Lambda events and responses.
Provides utilities for processing Lambda event inputs and formatting responses.
"""

import json
import os

class LambdaHandler:
    """
    Handler class for AWS Lambda events.
    
    This class processes Lambda event inputs and provides utilities
    for handling both direct invocations and SNS triggered events.
    
    Attributes:
        sns_event (bool): Indicates if event is from SNS
        event (dict): Processed Lambda event
    """
    def __init__(self,event):
        """
        Initialize LambdaHandler with an event.
        
        Args:
            event (dict/str): Lambda event to process
        """
        self.sns_event = None

        try:
            self.event = json.loads(event)
        except Exception:
            print("")
            print("event already a dictionary")
            self.event = event

    def get_init_msg(self):
        """
        Retrieve the initial message from the Lambda event.

        Handles both direct invocations and SNS-triggered events,
        extracting the core message based on the event structure.

        Args:
            self (object): LambdaHandler instance

        Returns:
            dict: Initial message extracted from the event
        """
        if "Records" in self.event:
            self.sns_event = True
            try:
                init_msg = json.loads(self.event['Records'][0]['Sns']['Message'])
            except Exception:
                init_msg = self.event
        else:
            init_msg = self.event

        if os.environ.get("DEBUG_IAC_CI"):
            print("")
            print(f"init_msg: {json.dumps(init_msg, indent=2)}")
            print("")

        return init_msg

def return_thru_lambda(results):
    """
    Format results for Lambda function return.
    
    Args:
        results (dict): Results to format for Lambda return
    
    Returns:
        dict: Formatted response with statusCode and body
    """
    if os.environ.get("DEBUG_IAC_CI"):
        print("*"*32)
        print(json.dumps(results,indent=4))
        print("*"*32)

    return { 'statusCode': 200,
             'continue':results["continue"],
             'body': json.dumps(results) }
