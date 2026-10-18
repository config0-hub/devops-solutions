# AWS CI/CD Environment Stack

## Description
This stack sets up a complete CI/CD environment in AWS, including S3 buckets, DynamoDB tables, Lambda functions, Step Functions, API Gateway, and SNS subscriptions to create a serverless CI/CD pipeline.

## How a push becomes a build

The install (`setup_codebuild_ci`) is run once per `ci_environment`. `add_codebuild_ci` is
run once per repository. Nothing is hosted by the user: the chain below runs on API Gateway,
Lambda, Step Functions and CodeBuild inside the user's AWS account.

```text
GitHub repository (hooked by add_codebuild_ci: github_webhook, secret = settings row "secret")
└── push / pull_request webhook -> API Gateway `ci-shared-<ci_environment>` (apigw_lambda-integ)
    └── Lambda `<ci_environment>-lambda_trigger_stepf` (execgroup github::lambda_trigger_stepf, app.handler)
        │   reads the trigger_id from the URL path, reads the webhook secret from the
        │   DynamoDB table `ci-shared-settings` (row _id = trigger_id), checks the HMAC,
        │   starts the Step Functions state machine, records the execution in `ci-shared-runs`
        └── Step Functions `<ci_environment>-codebuild-stepf-ci` (codebuild_stepf_ci / execgroup codebuild_ci_stepf)
            ├── ProcessWebhook   Lambda `<ci_environment>-process-webhook`  (lambda_codebuild_ci, app_webhook.handler)
            │                    parses the GitHub/Bitbucket payload, checks the branch, writes the run row
            ├── PkgCodeToS3     Lambda `<ci_environment>-pkgcode-to-s3`    (lambda_codebuild_ci, app_s3.handler)
            │                    reads the deploy key from SSM (settings row "ssm_ssh_key"), clones the
            │                    commit over SSH, zips it to `ci-shared-<ci_environment>-<suffix>-tmp`
            ├── TriggerCodebuild Lambda `<ci_environment>-trigger-codebuild` (lambda_codebuild_ci, app_codebuild.handler)
            │                    start_build on the CodeBuild project `<codebuild_name>` (aws_codebuild /
            │                    execgroup aws::codebuild), no source, with COMMIT_HASH, S3_LOCATION (the
            │                    zip) and the registry variables as environment variables; the buildspec
            │                    is the project's inline one unless the repository ships its own buildspec.yml
            └── CheckCodebuild  Lambda `<ci_environment>-check-codebuild`  (lambda_codebuild_ci, app_check_build.handler)
                                 polls batch_get_builds, pulls the build log from the tmp bucket, closes the run row
EventBridge rule "CodeBuild Build State Change" -> SNS topic `<ci_environment>-codebuild-complete-trigger`
    (codebuild_complete_trigger / execgroup aws::codebuild_evntbrdg_sns_lambda)
    -> the same `<ci_environment>-check-codebuild` Lambda, so a finished build also reaches that Lambda by event.
```

The repository is reached two ways, both set up by the stacks (no GitHub OIDC trust on the
user's side): a per-repository deploy key, and a webhook whose shared secret sits in the
`ci-shared-settings` row. The CodeBuild project has `NO_SOURCE`, and TriggerCodebuild's
`start_build` passes no source either, so the zip PkgCodeToS3 put in the tmp bucket is not what
CodeBuild unpacks: every build starts in an empty workspace. With the project's inline buildspec
(the repository ships no `buildspec.yml`) the `pre_build` phase clones the commit itself, over
SSH with the deploy key pulled from `parameter-store` (`SSH_KEY`), and checks out `$COMMIT_HASH`;
that clone is why CodeBuild needs the deploy key at all. A repository that ships its own
`buildspec.yml` gets that file as the `buildspecOverride` (PkgCodeToS3 copies it to the tmp
bucket beside the zip), the empty workspace, and the environment variables `COMMIT_HASH`,
`S3_LOCATION` (the zip's `s3://` location), `S3_BUCKET_OUTPUT` and `AWS_DEFAULT_REGION` plus the
registry ones; fetching the code, from `$S3_LOCATION` or by cloning, is that buildspec's job.

The deploy key is an EC2 key pair made by `new_github_ssh_key` (execgroup `aws::ssh_key_pair`).
EC2 keeps the private half in SSM Parameter Store at `/ec2/keypair/<key_pair_id>` and deletes it
with the key pair; the `ssh_key_pair` row names that parameter in `private_key_ssm_path`.
`add_codebuild_ci` passes the name on, as the settings row's `ssm_ssh_key` (the pkgcode-to-s3
Lambda reads it with decryption) and as the buildspec's `parameter-store` entry `SSH_KEY`. Config0
never copies the private half anywhere.

A build's result stays in the user's account. The check-codebuild Lambda closes the run's row in the
DynamoDB table `ci-shared-runs` with the build's status and, when `add_codebuild_ci` was given a Slack
webhook, posts a Slack message (status, repository, commit hash, build id). The Lambdas do not post the
result to Config0 (decided 2026-10-18, CON-101); a dashboard view of these runs is a possible later
feature (CON-102).

## Variables

### Required Variables
| Name | Description | Default |
|------|-------------|---------|
| ci_environment | CI/CD environment name | config0-eval |

### Optional Variables
| Name | Description | Default |
|------|-------------|---------|
| suffix_id | Configuration for suffix id | &nbsp; |
| suffix_length | Configuration for suffix length | 4 |
| aws_default_region | Default AWS region | us-east-1 |
| cloud_tags_hash | Resource tags for cloud provider | &nbsp; |
| bucket_acl | S3 bucket access permissions | private |
| bucket_expire_days | Days until object expiration | 7 |
| runtime | Lambda runtime environment | python3.11 |
| lambda_layers | Lambda function layers | &nbsp; |

## Dependencies

### Substacks
- [config0-hub:::aws_storage::aws_s3_bucket](https://api-app.config0.com/web_api/v1.0/stacks/config0-hub/aws_s3_bucket)
- [config0-hub:::aws_storage::aws_dynamodb](https://api-app.config0.com/web_api/v1.0/stacks/config0-hub/aws_dynamodb)
- [config0-hub:::aws::aws-lambda-python-codebuild](https://api-app.config0.com/web_api/v1.0/stacks/config0-hub/aws-lambda-python-codebuild)
- [config0-hub:::aws_networking::apigw_lambda-integ](https://api-app.config0.com/web_api/v1.0/stacks/config0-hub/apigw_lambda-integ)
- [config0-hub:::devops-solutions::codebuild_stepf_ci](https://api-app.config0.com/web_api/v1.0/stacks/config0-hub/codebuild_stepf_ci)
- [config0-hub:::devops-solutions::codebuild_complete_trigger](https://api-app.config0.com/web_api/v1.0/stacks/config0-hub/codebuild_complete_trigger)

### Execgroups
- [config0-hub:::github::lambda_trigger_stepf](https://api-app.config0.com/web_api/v1.0/exec/groups/config0-hub/github/lambda_trigger_stepf)
- [config0-hub:::github::lambda_codebuild_ci](https://api-app.config0.com/web_api/v1.0/exec/groups/config0-hub/github/lambda_codebuild_ci)

### Scripts
None identified in the provided code.

## License
<pre>
Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
</pre>
