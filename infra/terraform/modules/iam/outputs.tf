output "lambda_role_arn" {
  value = aws_iam_role.lambda.arn
}

output "knowledge_base_role_arn" {
  value = aws_iam_role.knowledge_base.arn
}
