variable "aws_default_region" {
  description = "AWS region where resources will be deployed"
  type        = string
  default     = "eu-west-1"
}

variable "ci_environment" {
  description = "CI environment"
  type        = string
}

variable "step_function_name" {
  description = "Name of the AWS Step Function state machine"
  type        = string
  default     = "apigw-codebuild-ci"
}

variable "process_webhook" {
  description = "Name of the Lambda function that processes webhooks"
  type        = string
  default     = "process-webhook"
}

variable "pkgcode_to_s3" {
  description = "Name of the Lambda function that packages code to S3"
  type        = string
  default     = "pkgcode-to-s3"
}

variable "check_codebuild" {
  description = "Name of the Lambda function that checks CodeBuild status"
  type        = string
  default     = "check-codebuild"
}

variable "trigger_codebuild" {
  description = "Name of the Lambda function that triggers CodeBuild"
  type        = string
  default     = "trigger-codebuild"
}

variable "cloud_tags" {
  description = "Additional tags as a map to apply to all resources"
  type        = map(string)
  default     = {}
}

