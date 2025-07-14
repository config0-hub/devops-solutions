# Infrastructure as Code (IaC) CI/CD Pipeline Manager

## Description

This stack registers a GitOps repository for the developer solutions "iac-ci"

## Variables

### Required

| Name | Description | Default |
|------|-------------|---------|
| app_name_iac | Configuration for Infrastructure as Code CI application name | iac-ci |
| iac_ci_repo | GitHub repository for the developer solution "iac-ci" | &nbsp; |
| iac_ci_github_token | GitHub token for accessing the IaC CI repository | &nbsp; |

### Optional

| Name | Description | Default |
|------|-------------|---------|
| github_token | GitHub token for creating SSH deploy keys | &nbsp; |
| GITHUB_TOKEN | Alternative GitHub token for creating SSH deploy keys | &nbsp; |
| github_token_hash | Base64 encoded GitHub token | &nbsp; |
| slack_webhook_b64 | Base64 encoded Slack webhook URL | &nbsp; |
| slack_webhook_hash | Base64 encoded Slack webhook URL | &nbsp; |
| infracost_api_key_hash | Base64 encoded Infracost API key | &nbsp; |
| infracost_api_key | Infracost API key for cost estimation | &nbsp; |
| project_id | config0 builtin - id of a Config0 project | &nbsp; |
| schedule_id | config0 builtin - id of schedule associated with a stack/workflow | &nbsp; |
| job_instance_id | config0 builtin - id of a job instance of a job in a schedule | &nbsp; |
| run_id | config0 builtin - id of a run for the instance of a stack/workflow | &nbsp; |

## Dependencies

### Substacks

- [config0-publish:::github_webhook](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/github_webhook)
- [config0-publish:::aws_dynamodb_item](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/aws_dynamodb_item)
- [config0-publish:::aws_ssm_param](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/aws_ssm_param)
- [config0-publish:::new_github_ssh_key](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/new_github_ssh_key)

## License
<pre>
Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.
</pre>