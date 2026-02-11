####FILE####:::step_function.tf
resource "aws_sfn_state_machine" "sfn_state_machine" {
  name       = var.step_function_name
  role_arn   = aws_iam_role.default.arn
  tags       = var.cloud_tags
  definition = <<EOF
{
  "Comment": "Processes webhook, executes CodeBuild, supports optional parallel folder builds when report && parallel_folder_builds. No parsing of $.body.",
  "StartAt": "ProcessWebhook",
  "States": {
    "ProcessWebhook": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:${var.aws_default_region}:${data.aws_caller_identity.current.account_id}:function:iac-ci-process-webhook",
      "Next": "ChkProcessWebhook"
    },
    "ChkProcessWebhook": {
      "Type": "Choice",
      "Choices": [
        {
          "And": [
            {
              "BooleanEquals": true,
              "Variable": "$.apply"
            },
            {
              "BooleanEquals": true,
              "Variable": "$.continue"
            }
          ],
          "Next": "TriggerCodebuild"
        },
        {
          "And": [
            {
              "BooleanEquals": true,
              "Variable": "$.destroy"
            },
            {
              "BooleanEquals": true,
              "Variable": "$.continue"
            }
          ],
          "Next": "TriggerCodebuild"
        },
        {
          "And": [
            {
              "BooleanEquals": true,
              "Variable": "$.continue"
            },
            {
              "BooleanEquals": true,
              "Variable": "$.report"
            },
            {
              "IsPresent": true,
              "Variable": "$.parallel_folder_builds"
            }
          ],
          "Next": "PrepareParallelBody"
        },
        {
          "And": [
            {
              "BooleanEquals": true,
              "Variable": "$.check"
            },
            {
              "BooleanEquals": true,
              "Variable": "$.continue"
            }
          ],
          "Next": "PkgCodeToS3"
        }
      ],
      "Default": "Done"
    },
    "PrepareParallelBody": {
      "Type": "Pass",
      "Parameters": {
        "parallelArray.$": "$.parallel_folder_builds",
        "original_body.$": "$.body"
      },
      "Next": "ParallelPkgCodeToS3"
    },
    "ParallelPkgCodeToS3": {
      "Type": "Map",
      "ItemsPath": "$.parallelArray",
      "ResultPath": "$.parallelResults",
      "MaxConcurrency": 0,
      "Parameters": {
        "iac_ci_folder.$": "$$.Map.Item.Value",
        "report": true,
        "body.$": "$.original_body",
        "_id.$": "$$.Map.Item.Value"
      },
      "Iterator": {
        "StartAt": "ChildPkgCodeToS3",
        "States": {
          "ChildPkgCodeToS3": {
            "Type": "Task",
            "Resource": "arn:aws:lambda:${var.aws_default_region}:${data.aws_caller_identity.current.account_id}:function:iac-ci-pkgcode-to-s3",
            "Next": "ChildChkPkgCodeToS3"
          },
          "ChildChkPkgCodeToS3": {
            "Type": "Choice",
            "Choices": [
              {
                "IsPresent": true,
                "Variable": "$.failure_s3_key",
                "Next": "Done_Child"
              },
              {
                "BooleanEquals": true,
                "Variable": "$.continue",
                "Next": "ChildTriggerLambda"
              }
            ],
            "Default": "Done_Child"
          },
          "ChildTriggerLambda": {
            "Type": "Task",
            "Resource": "arn:aws:lambda:${var.aws_default_region}:${data.aws_caller_identity.current.account_id}:function:iac-ci-trigger-lambda",
            "Next": "Done_Child"
          },
          "Done_Child": {
            "Type": "Pass",
            "End": true
          }
        }
      },
      "Next": "EvaluatePrParent"
    },
    "EvaluatePrParent": {
      "Type": "Task",
      "Comment": "Send final PR update using original string body; set continue=true inside your Lambda if needed.",
      "InputPath": "$.original_body",
      "Resource": "arn:aws:lambda:${var.aws_default_region}:${data.aws_caller_identity.current.account_id}:function:iac-ci-update-pr",
      "End": true
    },
    "PkgCodeToS3": {
      "Type": "Task",
      "InputPath": "$.body",
      "Resource": "arn:aws:lambda:${var.aws_default_region}:${data.aws_caller_identity.current.account_id}:function:iac-ci-pkgcode-to-s3",
      "Next": "ChkPkgCodeToS3"
    },
    "ChkPkgCodeToS3": {
      "Type": "Choice",
      "Choices": [
        {
          "IsPresent": true,
          "Variable": "$.failure_s3_key",
          "Next": "EvaluatePr"
        },
        {
          "BooleanEquals": true,
          "Variable": "$.continue",
          "Next": "TriggerLambda"
        }
      ],
      "Default": "Done"
    },
    "TriggerLambda": {
      "Type": "Task",
      "InputPath": "$.body",
      "Resource": "arn:aws:lambda:${var.aws_default_region}:${data.aws_caller_identity.current.account_id}:function:iac-ci-trigger-lambda",
      "Next": "ChkTriggerLambda"
    },
    "ChkTriggerLambda": {
      "Type": "Choice",
      "Choices": [
        {
          "BooleanEquals": true,
          "Variable": "$.continue",
          "Next": "EvaluatePr"
        }
      ],
      "Default": "Done"
    },
    "EvaluatePr": {
      "Type": "Task",
      "InputPath": "$.body",
      "Resource": "arn:aws:lambda:${var.aws_default_region}:${data.aws_caller_identity.current.account_id}:function:iac-ci-update-pr",
      "End": true
    },
    "TriggerCodebuild": {
      "Type": "Task",
      "InputPath": "$.body",
      "Resource": "arn:aws:lambda:${var.aws_default_region}:${data.aws_caller_identity.current.account_id}:function:iac-ci-trigger-codebuild",
      "Next": "ChkTriggerCodebuild"
    },
    "ChkTriggerCodebuild": {
      "Type": "Choice",
      "Choices": [
        {
          "BooleanEquals": true,
          "Variable": "$.continue",
          "Next": "WaitCodebuildCheck"
        }
      ],
      "Default": "Done"
    },
    "WaitCodebuildCheck": {
      "Type": "Wait",
      "Comment": "Wait to Check CodeBuild completion",
      "Seconds": 30,
      "Next": "CheckCodebuild"
    },
    "CheckCodebuild": {
      "Type": "Task",
      "InputPath": "$.body",
      "Resource": "arn:aws:lambda:${var.aws_default_region}:${data.aws_caller_identity.current.account_id}:function:iac-ci-check-codebuild",
      "Next": "ChkCheckCodebuild"
    },
    "ChkCheckCodebuild": {
      "Type": "Choice",
      "Choices": [
        {
          "BooleanEquals": true,
          "Variable": "$.continue",
          "Next": "CheckCodebuild"
        }
      ],
      "Default": "Done"
    },
    "Done": {
      "Type": "Pass",
      "End": true
    }
  }
}
EOF
}

####FILE####:::data.tf
data "aws_caller_identity" "current" {}

####FILE####:::outputs.tf
output "role_arn" {
  description = "ARN of the IAM role used by the Step Function state machine"
  value       = aws_sfn_state_machine.sfn_state_machine.role_arn
}

output "arn" {
  description = "ARN of the Step Function state machine"
  value       = aws_sfn_state_machine.sfn_state_machine.arn
}

####FILE####:::variables.tf
variable "aws_default_region" {
  description = "AWS region where resources will be deployed"
  type        = string
  default     = "eu-west-1"
}

variable "step_function_name" {
  description = "Name of the AWS Step Function state machine"
  type        = string
  default     = "apigw-codebuild-ci"
}

variable "app_name" {
  description = "Prefix for all Lambda functions and other resources"
  type        = string
  default     = "iac-ci"
}

variable "process_webhook" {
  description = "Name suffix for the Lambda function that processes webhooks"
  type        = string
  default     = "process-webhook"
}

variable "pkgcode_to_s3" {
  description = "Name suffix for the Lambda function that packages code to S3"
  type        = string
  default     = "pkgcode-to-s3"
}

variable "trigger_lambda" {
  description = "Name suffix for the Lambda function that triggers other Lambda functions"
  type        = string
  default     = "trigger-lambda"
}

variable "update_pr" {
  description = "Name suffix for the Lambda function that updates pull requests"
  type        = string
  default     = "update-pr"
}

variable "check_codebuild" {
  description = "Name suffix for the Lambda function that checks CodeBuild status"
  type        = string
  default     = "check-codebuild"
}

variable "trigger_codebuild" {
  description = "Name suffix for the Lambda function that triggers CodeBuild jobs"
  type        = string
  default     = "trigger-codebuild"
}

variable "cloud_tags" {
  description = "Additional tags to apply to all resources"
  type        = map(string)
  default     = {}
}

####FILE####:::provider.tf
# AWS Provider Configuration
# Configures the AWS provider with region and default tagging strategy

# Local block to sort tags for consistent ordering
locals {
  # Convert user-provided tags map to sorted list
  sorted_cloud_tags = [
    for k in sort(keys(var.cloud_tags)) : {
      key   = k
      value = var.cloud_tags[k]
    }
  ]

  # Create a sorted and consistent map of all tags
  all_tags = merge(
    # Convert sorted list back to map
    { for item in local.sorted_cloud_tags : item.key => item.value },
    {
      # Tag indicating resources are managed by config0
      orchestrated_by = "config0"
    }
  )
}

provider "aws" {
  # Region where AWS resources will be created
  region = var.aws_default_region

  # Default tags applied to all resources with consistent ordering
  default_tags {
    tags = local.all_tags
  }

  # Optional: Configure tags to be ignored by the provider
  ignore_tags {
    # Uncomment and customize if specific tags should be ignored
    # keys = ["TemporaryTag", "AutomationTag"]
  }
}

# Terraform Version Configuration
# Specifies the required Terraform and provider versions
terraform {
  # Minimum Terraform version required
  required_version = ">= 1.1.0"

  # Required providers with version constraints
  required_providers {
    aws = {
      source  = "hashicorp/aws" # AWS provider source
      version = "~> 5.0"        # Compatible with AWS provider v5.x
    }
  }
}

####FILE####:::iam.tf
resource "aws_iam_role" "default" {
  name = "${var.step_function_name}-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Principal = {
          Service = "states.amazonaws.com"
        }
        Effect = "Allow"
        Sid    = "StepFunctionAssumeRole"
      }
    ]
  })

  tags = var.cloud_tags
}

resource "aws_iam_role_policy" "step_function_policy" {
  name = "${var.step_function_name}-policy"
  role = aws_iam_role.default.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "lambda:InvokeFunction"
        ]
        Effect = "Allow"
        Resource = [
          "arn:aws:lambda:${var.aws_default_region}:${data.aws_caller_identity.current.account_id}:function:${var.app_name}-${var.process_webhook}",
          "arn:aws:lambda:${var.aws_default_region}:${data.aws_caller_identity.current.account_id}:function:${var.app_name}-${var.pkgcode_to_s3}",
          "arn:aws:lambda:${var.aws_default_region}:${data.aws_caller_identity.current.account_id}:function:${var.app_name}-${var.trigger_codebuild}",
          "arn:aws:lambda:${var.aws_default_region}:${data.aws_caller_identity.current.account_id}:function:${var.app_name}-${var.trigger_lambda}",
          "arn:aws:lambda:${var.aws_default_region}:${data.aws_caller_identity.current.account_id}:function:${var.app_name}-${var.update_pr}",
          "arn:aws:lambda:${var.aws_default_region}:${data.aws_caller_identity.current.account_id}:function:${var.app_name}-${var.check_codebuild}"
        ]
      }
    ]
  })
}

####FILE####:::cloudwatch.tf
# EventBridge rule to capture CodeBuild state changes
resource "aws_cloudwatch_event_rule" "codebuild_state_change" {
  name        = "${var.app_name}-codebuild-state-change"
  description = "Captures CodeBuild state changes and triggers Step Function"

  event_pattern = jsonencode({
    source      = ["aws.codebuild"]
    detail-type = ["CodeBuild Build State Change"]
    detail = {
      build-status = ["SUCCEEDED", "FAILED", "STOPPED", "TIMED_OUT"]
    }
  })
}

# EventBridge target to invoke Step Function
resource "aws_cloudwatch_event_target" "invoke_step_function" {
  rule     = aws_cloudwatch_event_rule.codebuild_state_change.name
  arn      = aws_sfn_state_machine.sfn_state_machine.arn
  role_arn = aws_iam_role.eventbridge_sfn_role.arn

  # Format the event data for the Step Function
  input_transformer {
    input_paths = {
      buildStatus = "$.detail.build-status",
      buildId     = "$.detail.build-id",
      projectName = "$.detail.project-name",
      region      = "$.region",
      account     = "$.account"
    }
    input_template = <<EOF
{
  "body": {
    "buildStatus": <buildStatus>,
    "buildId": <buildId>,
    "projectName": <projectName>,
    "region": <region>,
    "account": <account>,
    "source": "EventBridge",
    "continue": true
  }
}
EOF
  }
}

# IAM role for EventBridge to invoke Step Function
resource "aws_iam_role" "eventbridge_sfn_role" {
  name = "${var.app_name}-eventbridge-sfn-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "events.amazonaws.com"
        }
      }
    ]
  })

  tags = var.cloud_tags
}

# IAM policy to allow EventBridge to invoke Step Function
resource "aws_iam_role_policy" "eventbridge_sfn_policy" {
  name = "${var.app_name}-eventbridge-sfn-policy"
  role = aws_iam_role.eventbridge_sfn_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action   = "states:StartExecution"
        Effect   = "Allow"
        Resource = aws_sfn_state_machine.sfn_state_machine.arn
      }
    ]
  })
}
