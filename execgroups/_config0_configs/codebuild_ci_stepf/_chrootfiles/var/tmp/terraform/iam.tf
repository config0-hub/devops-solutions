resource "aws_iam_role" "default" {
  name = "${var.step_function_name}-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Principal = {
        Service = "states.amazonaws.com"
      }
      Effect = "Allow"
      Sid    = "StepFunctionAssumeRole"
    }]
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
          "arn:aws:lambda:${var.aws_default_region}:${data.aws_caller_identity.current.account_id}:function:${var.ci_environment}-${var.process_webhook}",
          "arn:aws:lambda:${var.aws_default_region}:${data.aws_caller_identity.current.account_id}:function:${var.ci_environment}-${var.pkgcode_to_s3}",
          "arn:aws:lambda:${var.aws_default_region}:${data.aws_caller_identity.current.account_id}:function:${var.ci_environment}-${var.trigger_codebuild}",
          "arn:aws:lambda:${var.aws_default_region}:${data.aws_caller_identity.current.account_id}:function:${var.ci_environment}-${var.check_codebuild}"
        ]
      }
    ]
  })
}

