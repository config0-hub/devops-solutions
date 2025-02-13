#!/usr/bin/python

import os
import json
import base64
import uuid
import traceback
import hmac
import hashlib
import six

from time import sleep
from datetime import datetime
from datetime import timedelta

from iac_ci.common.boto3_dynamo import Dynamodb_boto3
from iac_ci.common.loggerly import IaCLogger
from iac_ci.common.notify_slack import SlackNotify


def check_webhook_secret(secret, event_body, header_signature):
    """
    Verify the authenticity of a webhook request using HMAC-SHA1.

    Args:
        secret (str or bytes): The secret key used for HMAC generation
        event_body (str): The request body to verify
        header_signature (str): The signature from the request header in format 'sha1=<signature>'

    Returns:
        bool or str: True if verification succeeds, error message string if verification fails
    """
    if not header_signature:
        print("header_signature not provided - no secret check")
        return

    if secret is not None and not isinstance(secret, six.binary_type):
        secret = secret.encode('utf-8')

    sha_name, signature = header_signature.split('=')

    if sha_name != 'sha1':
        return "sha_name needs to be sha1"

    try:
        mac = hmac.new(secret, msg=event_body, digestmod=hashlib.sha1)
    except Exception:
        return "cannot determine the mac from secret"

    if not hmac.compare_digest(str(mac.hexdigest()), str(signature)):
        msg = "Digest does not match signature"
        print("*"*32)
        print(msg)
        print("*"*32)
        return False

    return True

def verify_signature(secret, body_dict, signature):
    """
    Verify webhook signature using HMAC-SHA256.

    Args:
        secret (str): Secret key for HMAC generation
        body_dict (dict): Request body as dictionary
        signature (str): Signature to verify against in format 'sha256=<signature>'

    Returns:
        bool: True if signature is valid, False otherwise
    """
    body = json.dumps(body_dict, sort_keys=True)
    computed_signature = 'sha256=' + hmac.new(
        key=secret.encode(),
        msg=body.encode(),
        digestmod=hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(computed_signature, signature)

class CreateTempParamStoreEntry:
    """
    Creates temporary entries in AWS Systems Manager Parameter Store with expiration.
    """

    def __init__(self, expire_mins=60):
        """
        Initialize with expiration time for parameters.

        Args:
            expire_mins (int): Minutes until parameter expiration
        """
        self.ssm_tmp_prefix = os.environ.get("IAC_CI_SSM_TMP_PREFIX",
                                             '/iac-ci/imported/tmp')
        self.ssm_expire_mins = expire_mins

    def _fetch_ssm_param(self, name):
        """
        Fetch a parameter from AWS Systems Manager Parameter Store.

        Args:
            name (str): Parameter name to fetch

        Returns:
            str: Parameter value
        """
        response = self.ssm.get_parameter(Name=name, WithDecryption=True)
        return response['Parameter']['Value']
    
    def _get_expiration_parameter_policy(self):
        """
        Generate expiration policy for SSM parameter.

        Returns:
            str: JSON string containing expiration policy
        """
        current_datetime = datetime.now()
        future_datetime = current_datetime + timedelta(minutes=self.ssm_expire_mins)
        iso_instant_str = future_datetime.isoformat(timespec='seconds') + 'Z'

        policy = [{"Type": "Expiration",
                  "Version": "1.0",
                  "Attributes": {
                      "Timestamp": iso_instant_str
                  }}]

        return json.dumps(policy)

    def _put_advance_param(self, name, value):
        """
        Put a parameter in SSM Parameter Store with advanced features.

        Args:
            name (str): Parameter name
            value (str): Parameter value

        Returns:
            dict: Response from SSM put_parameter
        """
        inputargs = {
            "Name": name,
            "Value": value,
            "Type": "SecureString",
            "Overwrite": True,
            "Tier": "Advanced",
            "Description": 'Temp Parameter with expiration',
            "Policies": self._get_expiration_parameter_policy()
        }

        return self.ssm.put_parameter(**inputargs)

    @staticmethod
    def _decode_env_to_dict(encoded_env):
        """
        Decode base64 encoded environment variables to dictionary.

        Args:
            encoded_env (str): Base64 encoded environment variables

        Returns:
            dict: Decoded environment variables
        """
        decoded_bytes = base64.b64decode(encoded_env)
        decoded_str = decoded_bytes.decode('utf-8')
        return dict(
            line.split('=', 1)
            for line in decoded_str.strip().split('\n')
            if line and not line.startswith('#')
        )

    @staticmethod
    def _dict_to_env_str(env_dict):
        """
        Convert dictionary to environment variable string format.

        Args:
            env_dict (dict): Environment variables dictionary

        Returns:
            str: Environment variables in string format
        """
        return '\n'.join(f'{key}={value}' for key, value in env_dict.items())

    def create_temp_ssm_name(self, ssm_name, additional_values):
        """
        Create temporary SSM parameter with combined values.

        Args:
            ssm_name (str): Existing SSM parameter name to fetch values from
            additional_values (dict): Additional values to combine

        Returns:
            str: New SSM parameter name
        """
        env_dict = {}

        if ssm_name:
            try:
                base64_env = self._fetch_ssm_param(ssm_name)
                env_dict = self._decode_env_to_dict(base64_env)
            except Exception:
                env_dict = {}
                self.logger.warn(f"could not get env from ssm_name {ssm_name}")

        if additional_values:
            env_dict.update(additional_values)

        if not env_dict:
            return

        new_env_string = self._dict_to_env_str(env_dict)
        new_base64_env = base64.b64encode(new_env_string.encode('utf-8')).decode('utf-8')
        random_suffix = str(uuid.uuid4())
        new_ssm_name = f"{self.ssm_tmp_prefix}/{random_suffix}"
        self._put_advance_param(new_ssm_name, new_base64_env)

        return new_ssm_name

class Notification:
    """
    Handles notifications to Slack for IaC CI events.
    """
    
    def __init__(self):
        """Initialize notification handler."""
        self.classname = "Notification"
        self.logger = IaCLogger(self.classname)
        self.slack = SlackNotify(username="IaCCINotifyBot",
                               header_text="IaCCI")

        self.slack_webhook_b64 = None
        self.infracost_api_key = None

    def _set_slack_token(self):
        """
        Set Slack webhook token from SSM parameter.

        Returns:
            str: Slack webhook hash
        """
        if self.slack_webhook_b64:
            return self.slack_webhook_b64

        ssm_name = self.trigger_info.get("ssm_slack_webhook_b64")

        if not ssm_name:
            ssm_name = self.trigger_info.get("ssm_slack_webhook_hash")

        if not ssm_name:
            self.logger.warn("ssm_name for slack not found - notification not enabled")
            return

        try:
            _ssm_info = self.ssm.get_parameter(Name=ssm_name,WithDecryption=True)
            self.slack_webhook_b64 = _ssm_info["Parameter"]["Value"]
        except Exception:
            self.logger.warn("could not fetch slack webhook")

        return self.slack_webhook_b64

    def _eval_links(self):
        """
        Evaluate and collect links for notification.

        Returns:
            list: List of link dictionaries
        """
        links = []

        if self.results["notify"].get("links"):
            links = self.results["notify"]["links"]

        if self.webhook_info.get("commit_hash"):
            commit_hash = self.webhook_info["commit_hash"]
            url = f'https://github.com/{self.webhook_info["owner"]}/{self.webhook_info["repo_name"]}/commit/{commit_hash}'
            links.append({f'commit - {commit_hash[:6]}': url})

        if self.run_info.get("console_url"):
            links.append({"ci pipeline": self.run_info["console_url"]})

        if self.run_info.get("build_url"):
            links.append({"execution details": self.run_info["build_url"]})

        if self.report_url:
            links.append({f"IaC-CI summary": self.report_url})

        return links

    def _get_slack_inputargs(self, **kwargs):
        """
        Prepare arguments for Slack notification.

        Args:
            **kwargs: Additional arguments for notification

        Returns:
            dict: Input arguments for Slack notification
        """
        self._set_slack_token()

        message = self._get_notify_message()

        inputargs = {
            "message": message,
            "slack_webhook_b64": self.slack_webhook_b64
        }

        if self.results.get("status") in ["failed", "timed_out", False, "false"]:
            inputargs["emoji"] = ":x:"
        elif self.results.get("status") in ["successful", "success", True, "true"]:
            inputargs["emoji"] = ":white_check_mark:"
        else:
            inputargs["emoji"] = ":information_source:"

        try:
            inputargs["title"] = self.results["notify"]["title"]
        except Exception:
            if kwargs.get("title"):
                inputargs["title"] = kwargs["title"]
            else:
                inputargs["title"] = f'{inputargs["emoji"]} - iac-ci report'

        if links := self._eval_links():
            inputargs["links"] = links

        if self.trigger_info.get("slack_channel"): 
            inputargs["slack_channel"] = self.trigger_info["slack_channel"]

        return inputargs

    def notify(self):
        """
        Send notification to Slack.
        """
        if not self.results.get("notify"):
            self.logger.debug("no notification messages requested")
            return

        inputargs = self._get_slack_inputargs()

        if not inputargs:
            return

        try:
            self.slack.run(inputargs)
        except Exception:
            self.logger.error(f"could not slack notify:\n {traceback.format_exc()}")

class GetFrmDb:
    """
    Retrieve information from DynamoDB tables.
    """

    def __init__(self, **kwargs):
        """
        Initialize database connection.

        Args:
            **kwargs: Must include 'app_name' for table names
        """
        self.classname = "GetFrmDb"
        self.logger = IaCLogger(self.classname)
        dynamodb_boto3 = Dynamodb_boto3()

        app_name = kwargs["app_name"]

        self.table_runs_name = f'{app_name}-runs'
        self.table_settings_name = f'{app_name}-settings'

        self.table_runs = dynamodb_boto3.set(table=self.table_runs_name)
        self.table_settings = dynamodb_boto3.set(table=self.table_settings_name)

    def get_run_info(self, run_id=None, build_id=None):
        """
        Get run information by run_id or build_id.

        Args:
            run_id (str, optional): Run ID to search for
            build_id (str, optional): Build ID to search for

        Returns:
            dict: Run information
        """
        if run_id:
            return self._run_info_by_run_id(run_id)
        elif build_id:
            return self._run_info_by_build_id(build_id)

    def _run_info_by_run_id(self, run_id):
        """
        Get run information by run ID.

        Args:
            run_id (str): Run ID to search for

        Returns:
            dict: Run information
        """
        _match = {"_id": run_id}

        try:
            run_info = self.table_runs.get(_match)["Item"]
        except Exception:
            run_info = None
            self.logger.warn(f"could not find {_match} in {self.table_runs}")

        return run_info

    def _run_info_by_build_id(self, build_id):
        """
        Get run information by build ID with retries.

        Args:
            build_id (str): Build ID to search for

        Returns:
            dict: Run information
        """
        run_info = None

        try:
            for _ in range(24):
                query = self.table_runs.search_key("build_id", build_id)
                if query.get("Items"):
                    self.logger.warn(f"found build_id: {build_id} in {self.table_runs_name}")
                    run_info = query["Items"][0]
                    break
                else:
                    sleep(5)
        except Exception:
            self.logger.warn(f"could not find build_id: {build_id} in {self.table_runs_name}")
            run_info = None

        return run_info

    def get_trigger_info(self, trigger_id=None, repo_name=None):
        """
        Get trigger information by trigger_id or repo_name.

        Args:
            trigger_id (str, optional): Trigger ID to search for
            repo_name (str, optional): Repository name to search for

        Returns:
            list: List of trigger information
        """
        if trigger_id:
            return self._trigger_info_by_trigger_id(trigger_id)
        elif repo_name:
            return self._trigger_info_by_repo_name(repo_name)

    def _trigger_info_by_trigger_id(self, trigger_id):
        """
        Get trigger information by trigger ID.

        Args:
            trigger_id (str): Trigger ID to search for

        Returns:
            list: List containing trigger information
        """
        match = {"_id": trigger_id}
        self.logger.debug(f"looking for trigger match {match}")

        try:
            trigger_info = [self.table_settings.get(match)["Item"]]
        except Exception:
            trigger_info = []

        return trigger_info

    def _trigger_info_by_repo_name(self, repo_name):
        """
        Get trigger information by repository name with retries.

        Args:
            repo_name (str): Repository name to search for

        Returns:
            list: List of trigger information
        """
        trigger_info = []

        for _ in range(24):
            try:
                query = self.table_settings.search_key("repo_name", repo_name)
                trigger_info = query["Items"]
                break
            except Exception:
                trigger_info = []
                sleep(5)

        return trigger_info

    def get_iac_info(self, iac_ci_id):
        """
        Get IaC information by ID.

        Args:
            iac_ci_id (str): IaC CI ID to search for

        Returns:
            dict: IaC CI information
        """
        match = {"_id": iac_ci_id}
        query = self.table_settings.get(match)

        try:
            iac_ci_info = query["Item"]
        except Exception:
            iac_ci_info = None

        return iac_ci_info
