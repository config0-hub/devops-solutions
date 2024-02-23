data "aws_caller_identity" "current" {}

###############################################################
# Variables
###############################################################

variable "aws_default_region" {
  default = "eu-west-1"
}

variable "step_function_name" {
  default = "apigw-codebuild-ci"
}

variable "process_webhook" {
  default = "process-webhook"
}

variable "pkgcode_to_s3" {
  default = "pkgcode-to-s3"
}

variable "check_codebuild" {
  default = "check-codebuild"
}

variable "trigger_codebuild" {
  default = "trigger-codebuild"
}

variable "cloud_tags" {
  description = "additional tags as a map"
  type        = map(string)
  default     = {}
}

###############################################################
# Main
###############################################################

resource "aws_iam_role" "default" {
  name               = "${var.step_function_name}-role"
  assume_role_policy = <<-EOF
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Action": "sts:AssumeRole",
        "Principal": {
          "Service": "states.amazonaws.com"
        },
        "Effect": "Allow",
        "Sid": "StepFunctionAssumeRole"
      }
    ]
  }
  EOF
}


resource "aws_sfn_state_machine" "sfn_state_machine" {
  name     = var.step_function_name
  role_arn = aws_iam_role.default.arn

  definition = <<EOF
  {
    "Comment": "the state machine processes webhook from code repo, executes codebuild, and check results",
    "StartAt": "ProcessWebhook",
    "States": {
      "ProcessWebhook": {
        "Type": "Task",
        "Resource": "arn:aws:lambda:${var.aws_default_region}:${data.aws_caller_identity.current.account_id}:function:${var.process_webhook}",
        "Next": "ChkProcessWebhook"
      },
      "ChkProcessWebhook": {
        "Type": "Choice",
        "Choices": [
          {
            "Variable": "$.lambdaResult.continue",
            "BooleanEquals": true,
            "Next": "PkgCodeToS3"
          }
        ],
        "Default": "Done"
      },
      "PkgCodeToS3": {
        "Type": "Task",
        "Resource": "arn:aws:lambda:${var.aws_default_region}:${data.aws_caller_identity.current.account_id}:function:${var.pkgcode_to_s3}",
        "Next": "ChkPkgCodeToS3"
      },
      "ChkPkgCodeToS3": {
        "Type": "Choice",
        "Choices": [
          {
            "Variable": "$.lambdaResult.continue",
            "BooleanEquals": true,
            "Next": "TriggerCodebuild"
          }
        ],
        "Default": "Done"
      },
      "TriggerCodebuild": {
        "Type": "Task",
        "Resource": "arn:aws:lambda:${var.aws_default_region}:${data.aws_caller_identity.current.account_id}:function:${var.trigger_codebuild}",
        "Next": "ChkTriggerCodebuild"
      },
      "ChkTriggerCodebuild": {
        "Type": "Choice",
        "Choices": [
          {
            "Variable": "$.lambdaResult.continue",
            "BooleanEquals": true,
            "Next": "WaitCodebuildDone"
          }
        ],
        "Default": "Done"
      },
      "WaitCodebuildDone": {
        "Type": "Choice",
        "Choices": [
          {
            "Variable": "$.detail.build-status",
            "StringEquals": "TIMED_OUT",
            "Next": "CheckCodebuild"
          },
          {
            "Variable": "$.detail.build-status",
            "StringEquals": "CLIENT_ERROR",
            "Next": "CheckCodebuild"
          },
          {
            "Variable": "$.detail.build-status",
            "StringEquals": "FAULT",
            "Next": "CheckCodebuild"
          },
          {
            "Variable": "$.detail.build-status",
            "StringEquals": "STOPPED",
            "Next": "CheckCodebuild"
          },
          {
            "Variable": "$.detail.build-status",
            "StringEquals": "FAILED",
            "Next": "CheckCodebuild"
          },
          {
            "Variable": "$.detail.build-status",
            "StringEquals": "SUCCEEDED",
            "Next": "CheckCodebuild"
          }
        ],
        "Default": "Done"
      },
      "CheckCodebuild": {
        "Type": "Task",
        "Resource": "arn:aws:lambda:${var.aws_default_region}:${data.aws_caller_identity.current.account_id}:function:${var.check_codebuild}",
        "End": true
      },
      "Done": {
        "Type": "Pass",
        "End": true
      }
    }
  }
  EOF
}

resource "aws_iam_role_policy" "step_function_policy" {
  name    = "${var.step_function_name}-policy"
  role    = aws_iam_role.default.id

  policy  = <<-EOF
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Action": [
          "lambda:InvokeFunction"
        ],
        "Effect": "Allow",
        "Resource": [ "arn:aws:lambda:${var.aws_default_region}:${data.aws_caller_identity.current.account_id}:function:${var.process_webhook}",
                      "arn:aws:lambda:${var.aws_default_region}:${data.aws_caller_identity.current.account_id}:function:${var.pkgcode_to_s3}",
                      "arn:aws:lambda:${var.aws_default_region}:${data.aws_caller_identity.current.account_id}:function:${var.trigger_codebuild}",
                      "arn:aws:lambda:${var.aws_default_region}:${data.aws_caller_identity.current.account_id}:function:${var.check_codebuild}" ]
      }
    ]
  }
  EOF
}
