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

