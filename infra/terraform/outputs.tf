output "api_endpoint" {
  description = "API Gateway endpoint for the SentinelAI AWS Agent service."
  value       = module.api_gateway.invoke_url
}

output "lambda_function_name" {
  description = "Lambda function hosting the agent runtime."
  value       = module.lambda.function_name
}

output "knowledge_bucket_name" {
  description = "S3 bucket for knowledge base documents."
  value       = module.s3.bucket_id
}

output "knowledge_base_id" {
  description = "Bedrock knowledge base ID."
  value       = aws_bedrockagent_knowledge_base.this.id
}

output "incident_table_name" {
  description = "DynamoDB table used for agent memory."
  value       = module.dynamodb.table_name
}
