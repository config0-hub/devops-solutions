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
        Resource = "arn:aws:lambda:${var.aws_default_region}:${data.aws_caller_identity.current.account_id}:function:${var.app_name}-${var.process_webhook}"
        Next     = "ChkProcessWebhook"
      }
      ChkProcessWebhook = {
        Type = "Choice"
        Choices = [
          {
            And = [
              {
                Variable      = "$.apply"
                BooleanEquals = true
              },
              {
                Variable      = "$.continue"
                BooleanEquals = true
              }
            ]
            Next = "TriggerCodebuild"
          },
          {
            And = [
              {
                Variable      = "$.destroy"
                BooleanEquals = true
              },
              {
                Variable      = "$.continue"
                BooleanEquals = true
              }
            ]
            Next = "TriggerCodebuild"
          },
          {
            And = [
              {
                Variable      = "$.check"
                BooleanEquals = true
              },
              {
                Variable      = "$.continue"
                BooleanEquals = true
              }
            ]
            Next = "PkgCodeToS3"
          }
        ]
        Default = "Done"
      }
      PkgCodeToS3 = {
        Type      = "Task"
        Resource  = "arn:aws:lambda:${var.aws_default_region}:${data.aws_caller_identity.current.account_id}:function:${var.app_name}-${var.pkgcode_to_s3}"
        Next      = "ChkPkgCodeToS3"
        InputPath = "$.body"
      }
      ChkPkgCodeToS3 = {
        Type = "Choice"
        Choices = [
          {
            Variable      = "$.continue"
            BooleanEquals = true
            Next          = "TriggerLambda"
          }
        ]
        Default = "Done"
      }
      TriggerLambda = {
        Type      = "Task"
        Resource  = "arn:aws:lambda:${var.aws_default_region}:${data.aws_caller_identity.current.account_id}:function:${var.app_name}-${var.trigger_lambda}"
        Next      = "ChkTriggerLambda"
        InputPath = "$.body"
      }
      ChkTriggerLambda = {
        Type = "Choice"
        Choices = [
          {
            Variable      = "$.continue"
            BooleanEquals = true
            Next          = "EvaluatePr"
          }
        ]
        Default = "Done"
      }
      EvaluatePr = {
        Type      = "Task"
        Resource  = "arn:aws:lambda:${var.aws_default_region}:${data.aws_caller_identity.current.account_id}:function:${var.app_name}-${var.update_pr}"
        InputPath = "$.body"
        End       = true
      }
      TriggerCodebuild = {
        Type      = "Task"
        Resource  = "arn:aws:lambda:${var.aws_default_region}:${data.aws_caller_identity.current.account_id}:function:${var.app_name}-${var.trigger_codebuild}"
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
        Resource  = "arn:aws:lambda:${var.aws_default_region}:${data.aws_caller_identity.current.account_id}:function:${var.app_name}-${var.check_codebuild}"
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

