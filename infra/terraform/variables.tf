variable "project_name" {
  description = "Project name used for resource naming."
  type        = string
  default     = "sentinelai-aws-agent"
}

variable "aws_region" {
  description = "AWS region for deployment."
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Deployment environment name."
  type        = string
  default     = "dev"
}

variable "lambda_package_path" {
  description = "Path to the Lambda deployment zip package."
  type        = string
  default     = "../../dist/sentinelai_aws_agent.zip"
}

variable "bedrock_model_id" {
  description = "Foundation model ID used for reasoning and log analysis."
  type        = string
  default     = "anthropic.claude-3-5-sonnet-20241022-v2:0"
}

variable "kb_embedding_model_arn" {
  description = "Embedding model ARN for the Bedrock knowledge base."
  type        = string
  default     = "arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v2:0"
}

variable "log_retention_days" {
  description = "Retention in days for CloudWatch logs."
  type        = number
  default     = 14
}

variable "tags" {
  description = "Common tags for AWS resources."
  type        = map(string)
  default = {
    project     = "sentinelai-aws-agent"
    managed_by  = "terraform"
    repository  = "sentinelai-aws-agent"
  }
}
