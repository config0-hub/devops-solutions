output "role_arn" {
  description = "ARN of the IAM role used by the Step Function state machine"
  value       = aws_sfn_state_machine.sfn_state_machine.role_arn
}

output "arn" {
  description = "ARN of the Step Function state machine"
  value       = aws_sfn_state_machine.sfn_state_machine.arn
}