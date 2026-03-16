resource "aws_cloudwatch_log_group" "this" {
  name              = "/aws/lambda/${var.function_name}"
  retention_in_days = var.log_retention_days
  tags              = var.tags
}

resource "aws_lambda_function" "this" {
  function_name    = var.function_name
  role             = var.lambda_role_arn
  runtime          = "python3.12"
  handler          = "src.api.handler.lambda_handler"
  filename         = var.package_path
  source_code_hash = var.source_code_hash
  timeout          = 90
  memory_size      = 1024

  environment {
    variables = var.environment_variables
  }

  depends_on = [aws_cloudwatch_log_group.this]
  tags       = var.tags
}
