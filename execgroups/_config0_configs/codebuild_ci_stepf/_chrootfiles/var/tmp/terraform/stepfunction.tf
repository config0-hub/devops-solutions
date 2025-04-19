resource "aws_sfn_state_machine" "sfn_state_machine" {
  name     = var.step_function_name
  role_arn = aws_iam_role.default.arn
  tags     = var.cloud_tags

  definition = jsonencode({
    Comment = "The state machine processes webhook from code repo, executes codebuild, and checks results"
    StartAt = "ProcessWebhook"
    States = {
      ProcessWebhook = {
        Type     = "Task"
        Resource = "arn:aws:lambda:${var.aws_default_region}:${data.aws_caller_identity.current.account_id}:function:${var.process_webhook}"
        Next     = "ChkProcessWebhook"
      }
      ChkProcessWebhook = {
        Type = "Choice"
        Choices = [
          {
            Variable      = "$.continue"
            BooleanEquals = true
            Next          = "PkgCodeToS3"
          }
        ]
        Default = "Done"
      }
      PkgCodeToS3 = {
        Type      = "Task"
        Resource  = "arn:aws:lambda:${var.aws_default_region}:${data.aws_caller_identity.current.account_id}:function:${var.pkgcode_to_s3}"
        Next      = "ChkPkgCodeToS3"
        InputPath = "$.body"
      }
      ChkPkgCodeToS3 = {
        Type = "Choice"
        Choices = [
          {
            Variable      = "$.continue"
            BooleanEquals = true
            Next          = "TriggerCodebuild"
          }
        ]
        Default = "Done"
      }
      TriggerCodebuild = {
        Type      = "Task"
        Resource  = "arn:aws:lambda:${var.aws_default_region}:${data.aws_caller_identity.current.account_id}:function:${var.trigger_codebuild}"
        Next      = "ChkTriggerCodebuild"
        InputPath = "$.body"
      }
      ChkTriggerCodebuild = {
        Type = "Choice"
        Choices = [
          {
            Variable      = "$.continue"
            BooleanEquals = true
            Next          = "WaitCodebuildCheck"
          }
        ]
        Default = "Done"
      }
      WaitCodebuildCheck = {
        Type    = "Wait"
        Seconds = 30
        Next    = "CheckCodebuild"
        Comment = "Wait to Check CodeBuild completion"
      }
      CheckCodebuild = {
        Type      = "Task"
        Resource  = "arn:aws:lambda:${var.aws_default_region}:${data.aws_caller_identity.current.account_id}:function:${var.check_codebuild}"
        Next      = "ChkCheckCodebuild"
        InputPath = "$.body"
      }
      ChkCheckCodebuild = {
        Type = "Choice"
        Choices = [
          {
            Variable      = "$.continue"
            BooleanEquals = true
            Next          = "CheckCodebuild"
          }
        ]
        Default = "Done"
      }
      Done = {
        Type = "Pass"
        End  = true
      }
    }
  })
}

