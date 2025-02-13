#!/usr/bin/env python
import traceback

import boto3
import gzip
from io import BytesIO
from time import sleep
from time import time

from iac_ci.common.loggerly import IaCLogger
from iac_ci.common.orders import OrdersStagesHelper as PlatformReporter
from iac_ci.common.github_pr import GitHubRepo

class CheckBuild(PlatformReporter):

    def __init__(self,**kwargs):

        """
        Constructor for CheckBuild class.

        The constructor sets up the build object for the codebuild run.

        Parameters:
        inputargs (dict): A dictionary of keyword arguments passed to the class
        build_id (str): The AWS CodeBuild id for the build
        build_status (str): The status of the AWS CodeBuild build
        chk_t0 (int): The time when the check started
        chk_count (int): The count of the check
        step_func (str): The name of the step function
       """
        self.build_expire_at = None
        self.classname = "CheckBuild"
        self.logger = IaCLogger(self.classname)
        PlatformReporter.__init__(self,**kwargs)

        session = boto3.Session()
        self.codebuild_client = session.client('codebuild')
        self.s3 = boto3.resource('s3')

        try:
            self.build_id = kwargs.get("build_id")
        except Exception:
            self.build_id=kwargs["inputargs"]["build_id"]

        self.phase = "check_build"
        self.build_status = kwargs.get("build_status")
        self.chk_t0 = kwargs.get("chk_t0")
        self.chk_count = kwargs.get("chk_count") or 0
        self.chk_count +=1

        if self.step_func:
            print("+"*32)
            print(f"checking codebuild count {self.chk_count}")
            print("+"*32)

        if not self.chk_t0:
            self.chk_t0 = int(time())

        self.build_id_suffix = None
        self.codebuild_log = None

        self.run_t0 = int(time())
        self.run_maxtime = 800  # lambda maximum is 900
        self.total_maxtime = 1800

    def _set_order(self):

        """
        Sets the order for the current process with a human-readable description and a specified role.

        The method constructs input arguments including a description of checking a codebuild
        and assigns the order using the new_order method.
        """
        
        inputargs = {
            "human_description": f'Check build_id: "{self.build_id}"',
            "role": "codebuild/build"
        }

        self.new_order(**inputargs)

    def _set_codebuild_params(self):

        """
        Retrieves the build status of a codebuild project using the provided build_id.

        Method takes no parameters, and retrieves the build status using the codebuild_client.
        It then checks the status and sets the results accordingly.

        If the build status is 'SUCCEEDED', 'FAILED', 'FAULT', or 'STOPPED', the method returns True.
        If the build status is 'TIMED_OUT', the method sets the results to "timed_out" and returns True.
        If the build status is 'IN_PROGRESS', the method does not return True.
       """
        if self.results.get("status"):
            return True

        build = self.codebuild_client.batch_get_builds(ids=[self.build_id])['builds'][0]
        build_status = build['buildStatus']
        codebuild_name = build['projectName']
        print(f"codebuild_name {codebuild_name}/codebuild status {build_status}")

        self.codebuild_log_bucket = build["logs"]["s3Logs"]["location"].split('/codebuild/logs')[0]
        self.logger.debug(f'codebuild s3 log bucket "{self.codebuild_log_bucket}"')

        self.results["build_status"] = build_status
        
        if build_status == 'SUCCEEDED': 
            self.results["status"] = "successful"
            return True

        if build_status == 'FAILED': 
            self.results["status"] = "failed"
            return True

        if build_status == 'FAULT': 
            self.results["status"] = "failed"
            return True

        if build_status == 'STOPPED': 
            self.results["status"] = "failed"
            return True

        if build_status == 'TIMED_OUT': 
            self.results["status"] = "timed_out"
            return True

        return

    def _chk_build(self):

        # see if build is done first
        """
        This method checks if a codebuild build is done.

        It will check the build status until it is done (SUCCEEDED, FAILED, FAULT, STOPPED, TIMED_OUT),
        or until the total max time is exceeded, or until the lambda function is about to expire.

        If the total max time is exceeded, it will set the results to "timed_out".
        If the lambda function is about to expire, it will break out of the loop and return.
        If the build is done, it will set the log using `_loop_set_log`.
       """
        build_done = self._set_codebuild_params()

        while not build_done:
            _t1 = int(time())
            _time_elapsed = _t1 - self.run_t0
            _total_time_elapsed = _t1 - self.chk_t0
        
            if _total_time_elapsed > self.total_maxtime:
                self.logger.error(f"total max time exceeded {self.total_maxtime}")
                self.results["status"] = "timed_out"
                break
        
            # check if lambda function is about to expire
            if _time_elapsed > self.run_maxtime:
                self.logger.warn(f"lambda run max time exceeded {self.run_maxtime}")
                break
        
            # check build exceeded total build time alloted
            if _t1 > self.build_expire_at:
                self.results["status"] = "timed_out"
                self.logger.error(f"build timed out: after {str(self.build_timeout)} seconds.")
                break
        
            sleep(5)
            build_done = self._set_codebuild_params()

        if self.results.get("status"):
            self._loop_set_log()

        return

    def _loop_set_log(self):

        """
        Loop until the log is retrieved from s3.

        The function loops for up to 30 seconds, sleeping for 2 seconds between each loop.
        If the log is retrieved, the function returns True.
        If the maximum time is exceeded, the function returns False.

        Returns:
        True if the log was retrieved, False otherwise
        """
        maxtime = 30
        t0 = int(time())

        _logname = f"codebuild/logs/{self.build_id_suffix}.gz"
        self.logger.debug(f"retrieving log: s3://{self.codebuild_log_bucket}/{_logname}")

        while True:

            _time_elapsed = int(time()) - t0

            if _time_elapsed > maxtime:
                self.logger.debug(f"time expired to retrieved log {str(_time_elapsed)} seconds")
                return False

            self._set_log(_logname)

            if self.codebuild_log: 
                break

            sleep(2)

    def _set_log(self,_logname):

        """
        Retrieves the codebuild log from s3.

        It will retrieve the log from the location specified in the codebuild project's
        configuration. If the log is retrieved, it will be stored in the object's
        attribute `codebuild_log`.

        If the log is not retrieved, it will return False.

        Returns:
        True if the log was retrieved, False otherwise
        """
        if self.codebuild_log:
            return True

        _dstfile = f'/tmp/{self.build_id_suffix}.gz'

        self.logger.debug(f'_set_log: s3 bucket - {self.codebuild_log_bucket}, s3 key - {_logname}')

        try:
            obj = self.s3.Object(self.codebuild_log_bucket,_logname)
            _read = obj.get()['Body'].read()
        except Exception:
            failed_message = f'_set_log: FAILED - s3 bucket - {self.codebuild_log_bucket}, s3 key - {_logname}\n {traceback.format_exc()}'
            self.logger.error(failed_message)
            return False

        gzipfile = BytesIO(_read)
        gzipfile = gzip.GzipFile(fileobj=gzipfile)
        log = gzipfile.read().decode('utf-8')

        self.logger.debug(f'_set_log: logged retrieved @ s3 bucket - {self.codebuild_log_bucket}, s3 key - {_logname}')

        self.codebuild_log = log

        return log

    def _save_run_info(self):
        """
        Save the run_info to the run_info table in DynamoDB.
        """
        self.run_info["build_status"] = self.results["status"]
        self.db.table_runs.insert(self.run_info)

        msg = f"trigger_id: {self.trigger_id} saved"
        self.add_log(msg)

    def _get_build_summary(self):
        """
        Generates a summary message based on the current build status.

        The method examines the `status` attribute of the `results` dictionary
        and the `build_id` attribute to determine the appropriate summary message.
        It updates the `status` to "failed" if the build was never triggered or
        if the build has failed. The summary message includes the trigger ID and
        build ID where applicable.

        Returns:
        str: A summary message detailing the build status.
        """
        if self.results["status"] == "successful":
            return f"# Successful \n# trigger_id {self.trigger_id} \n# build_id {self.build_id}"
        elif self.results["status"] == "timed_out":
            return f"# Timed out \n# trigger_id {self.trigger_id} \n# build_id {self.build_id}"
        elif self.build_id is False or not self.build_id:
            self.results["status"] = "failed"
            return f"# Never Triggered \n# trigger_id {self.trigger_id}"
        else:
            self.results["status"] = "failed"
            return f"# Failed \n# trigger_id {self.trigger_id} \n# build_id {self.build_id}"
    
    def _ci_links(self,base_comment):
        """
        Generates a markdown string containing a link to the CodeBuild console
        and a link to the CodeBuild execution details if available.

        :param base_comment: The markdown comment to which the links will be appended.
        :return: A markdown string with the links.
        """
        content = f'''\n##  Run(s) Info
{base_comment}
+ {self.webhook_info.get("commit_hash")}
'''
        if self.run_info.get("console_url"):

            content = f'{content}\n+ [ci pipeline]({self.run_info["console_url"]})'

        if self.run_info.get("build_url"):
            content = f'{content}\n+ [execution details]({self.run_info["build_url"]})'

        return content

    def finalize_pr(self):
        """
        Finalizes the PR by adding a comment to the PR with the CodeBuild console and execution details links.

        This method retrieves the necessary information from the `webhook_info` dictionary, sets the search tag,
        and creates a `GitHubRepo` instance to interact with the pull request. It then generates a markdown string
        with the links and adds the comment to the pull request. If an existing comment with the same search tag
        exists, it updates the comment. Otherwise, it adds a new comment.

        Finally, the method deletes any existing comment with the ID stored in the `status_comment_id` key of the
        `run_info` dictionary.

        Returns:
        dict: A dictionary with the comment ID and URL of the added comment.
        """
        repo_name = self.webhook_info["repo_name"]
        owner = self.webhook_info["owner"]
        pr_number = self.webhook_info["pr_number"]

        self.set_search_tag()

        github_repo = GitHubRepo(repo_name,
                                 pr_number,
                                 search_tag=self.search_tag,
                                 token=self.get_github_token(),
                                 owner=owner)

        base_comment = f'+ Executed By iac-ci\n    + owner: {owner}\n    + repo: {repo_name}\n    + pr_number: {pr_number}'
        ci_link_content = self._ci_links(base_comment)

        existing_comments = github_repo.get_pr_comments(use_default_search_tag=True)

        if existing_comments:
            comment_id = existing_comments[0]["id"]
            comment = existing_comments[0]["body"].replace(f'#{self.search_tag}',"").strip().rstrip('\n').rstrip('\r')
            comment = comment + "\n" + ci_link_content
            github_repo.delete_pr_comment(comment_id)
        else:
            comment = ci_link_content

        pr_info = github_repo.add_pr_comment(comment)

        self.clean_pr_comments()

        try:
            status_comment_id = self.run_info["status_comment_id"]
        except Exception:
            status_comment_id = self.run_info["status_comment_id"]

        if status_comment_id:
            github_repo.delete_pr_comment(status_comment_id)

        return pr_info

    def update_with_chks(self,results=None):
        """
        Updates a dictionary with the results of the checks.

        The dictionary should have at least the following keys:
            - chk_t0: the time when the first check was started
            - chk_count: the number of checks that were performed

        If the dictionary does not have the 'chk_t0' key, this method will add it with
        the current time.

        Parameters:
            results (dict): The dictionary to update with the results of the checks.

        Returns:
            dict: The updated dictionary with the results of the checks.
        """
        if not results:
            results = self.results

        if not results.get("chk_t0"):
            results["chk_t0"] = self.chk_t0

        results["chk_count"] = self.chk_count

        return results

    def execute(self):
        """
        Checks the status of the codebuild project with the given build_id.

        This method is the main entry point for the CheckBuild class. It checks the status
        of the codebuild project with the given build_id, and updates the results dictionary
        with the status of the build.

        If the build is successful, it will update the results with the status of "successful",
        and add a comment to the pull request with the results of the checks. If the build
        fails, it will update the results with the status of "failed", and add a comment to
        the pull request with the results of the checks. If the build times out, it will
        update the results with the status of "timed_out", and add a comment to the pull
        request with the results of the checks.

        If the build is not successful, it will not update the order, and the next step in
        the step function will be to call the _continue method. If the build is successful,
        it will update the order and the next step in the step function will be to call
        the _discontinue method.

        :return: A boolean indicating whether the build was successful.
        """
        self.build_id = self.run_info["build_id"]
        self.build_expire_at = int(self.run_info["build_expire_at"])
        self.build_id_suffix = self.build_id.split(":")[1]

        self._chk_build()
        self.update_with_chks()

        if self.results.get("step_func") and not self.results.get("status"):
            return "check_codebuild/_continue"

        if not self.codebuild_log:
            _log =f'failed to retrieved log \nbuild_id "{self.build_id}"'
        else:
            _log = self.codebuild_log

        self.add_log(_log)

        if self.results.get("step_func"):
            if self.results.get("status") != "successful":
                return "check_codebuild/_failed"
            else:
                return "check_codebuild/_discontinue"


        # the cloud watch and non step func
        # will handle wrapping things up

        # status should be set at this point
        self.results["continue"] = False
        self.results["close"] = True
        self.results["update"] = True

        # update_pr
        if self.results.get("status") == "successful":
            pr_info = self.finalize_pr()

            self.results["notify"] = {
                "links": [ {"github comment": pr_info["url"]} ]
            }

        # we only set order once we are completely done
        self._set_order()

        # at this point, the build finishes
        # either failed, timed_out, or successful
        summary_msg = self._get_build_summary()

        self.add_log("#"*32)
        self.add_log("# Summary")
        self.add_log(summary_msg)
        self.add_log("#"*32)

        self.results["msg"] = summary_msg

        if not self.results.get("notify"):
            self.results["notify"] = {
                "message": f"codebuild with build_id: {self.build_id}"
            }

        self.finalize_order()
        self._save_run_info()
        self.update_with_chks()

        return True