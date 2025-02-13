# Project Summary

## Overview of Languages, Frameworks, and Main Libraries Used
The project primarily utilizes Python as its programming language. It appears to be structured around AWS services, leveraging libraries such as Boto3 for AWS interactions. The project likely incorporates various frameworks and tools for CI/CD processes, including Terraform for infrastructure as code (IAC) and potentially GitHub Actions or similar for handling pull requests and notifications.

## Purpose of the Project
The project seems to focus on automating AWS-related tasks, including managing AWS resources, handling pull requests, and integrating with CI/CD pipelines. The presence of files related to code builds, Lambda functions, and Slack notifications suggests that the project aims to streamline deployment processes and improve collaboration through automated notifications and reporting.

## List of Build/Configuration/Project Files
- `/app_check_build.py`
- `/app_codebuild.py`
- `/app_lambda.py`
- `/app_pr.py`
- `/app_s3.py`
- `/app_webhook.py`
- `/iac_ci/common/boto3_bucket.py`
- `/iac_ci/common/boto3_common.py`
- `/iac_ci/common/boto3_dynamo.py`
- `/iac_ci/common/boto3_file.py`
- `/iac_ci/common/boto3_lambda.py`
- `/iac_ci/common/common.py`
- `/iac_ci/common/github_pr.py`
- `/iac_ci/common/loggerly.py`
- `/iac_ci/common/notify_slack.py`
- `/iac_ci/common/run_helper.py`
- `/iac_ci/config0/reporter.py`
- `/iac_ci/helper/cloud/aws/codebuild.py`
- `/iac_ci/helper/cloud/aws/lambdabuild.py`
- `/iac_ci/helper/cloud/aws/lambda_helper.py`
- `/iac_ci/helper/resource/aws.py`
- `/iac_ci/helper/resource/codebuild.py`
- `/iac_ci/helper/resource/common.py`
- `/iac_ci/helper/resource/infracost.py`
- `/iac_ci/helper/resource/lambdabuild.py`
- `/iac_ci/helper/resource/opa.py`
- `/iac_ci/helper/resource/terraform.py`
- `/iac_ci/helper/resource/tfinstaller.py`
- `/iac_ci/helper/resource/tfsec.py`
- `/iac_ci/helper/resource/serialization.py`
- `/iac_ci/helper/resource/shellouts.py`
- `/iac_ci/helper/resource/utilities.py`
- `/iac_ci/helper/main_check_build.py`
- `/iac_ci/helper/main_codebuild.py`
- `/iac_ci/helper/main_lambda.py`
- `/iac_ci/helper/main_pr.py`
- `/iac_ci/helper/main_s3.py`
- `/iac_ci/helper/main_webhook.py`

## Directories to Find Source Files
- The primary source files can be found in the following directories:
  - `/`
  - `/iac_ci/common`
  - `/iac_ci/config0`
  - `/iac_ci/helper`
  - `/iac_ci/helper/cloud/aws`
  - `/iac_ci/helper/resource`

## Location of Documentation Files
- Documentation files are located in the following directory:
  - `/docs` 
    - `example-tf-pr-body-for-pull-request-2.md`
    - `example-tf-pr-body-for-pull-request.md`