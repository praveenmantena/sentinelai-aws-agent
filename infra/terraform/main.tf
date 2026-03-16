terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.50"
    }
    archive = {
      source  = "hashicorp/archive"
      version = ">= 2.4"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

locals {
  name_prefix = "${var.project_name}-${var.environment}"
}

module "s3" {
  source      = "./modules/s3"
  bucket_name = "${local.name_prefix}-knowledge-${data.aws_caller_identity.current.account_id}"
  tags        = var.tags
}

module "dynamodb" {
  source     = "./modules/dynamodb"
  table_name = "${local.name_prefix}-incidents"
  tags       = var.tags
}

module "iam" {
  source                         = "./modules/iam"
  name_prefix                    = local.name_prefix
  knowledge_bucket_arn           = module.s3.bucket_arn
  incidents_table_arn            = module.dynamodb.table_arn
  bedrock_model_id               = var.bedrock_model_id
  knowledge_base_collection_arn  = aws_opensearchserverless_collection.kb.arn
  tags                           = var.tags
}

module "lambda" {
  source              = "./modules/lambda"
  function_name       = "${local.name_prefix}-agents"
  lambda_role_arn     = module.iam.lambda_role_arn
  package_path        = var.lambda_package_path
  source_code_hash    = filebase64sha256(var.lambda_package_path)
  log_retention_days  = var.log_retention_days
  environment_variables = {
    AWS_REGION                = var.aws_region
    APP_ENV                   = var.environment
    BEDROCK_MODEL_ID          = var.bedrock_model_id
    BEDROCK_KNOWLEDGE_BASE_ID = aws_bedrockagent_knowledge_base.this.id
    KNOWLEDGE_BUCKET          = module.s3.bucket_id
    INCIDENTS_TABLE           = module.dynamodb.table_name
    LOG_GROUP_NAME            = "/aws/lambda/${local.name_prefix}-agents"
  }
  tags = var.tags
}

module "api_gateway" {
  source               = "./modules/api_gateway"
  api_name             = "${local.name_prefix}-api"
  lambda_invoke_arn    = module.lambda.invoke_arn
  lambda_function_name = module.lambda.function_name
  tags                 = var.tags
}

data "aws_caller_identity" "current" {}

data "aws_iam_policy_document" "aoss_encryption" {
  statement {
    effect = "Allow"
    principals {
      type        = "AWS"
      identifiers = ["*"]
    }
    actions   = ["aoss:CreateCollectionItems", "aoss:UpdateCollectionItems", "aoss:DescribeCollectionItems"]
    resources = ["collection/${local.name_prefix}-kb"]
  }
}

resource "aws_opensearchserverless_security_policy" "encryption" {
  name        = "${local.name_prefix}-kb-encryption"
  type        = "encryption"
  description = "Encryption policy for Bedrock knowledge base collection"
  policy = jsonencode({
    Rules = [
      {
        Resource = ["collection/${local.name_prefix}-kb"]
        ResourceType = "collection"
      }
    ]
    AWSOwnedKey = true
  })
}

resource "aws_opensearchserverless_security_policy" "network" {
  name        = "${local.name_prefix}-kb-network"
  type        = "network"
  description = "Network policy for Bedrock knowledge base collection"
  policy = jsonencode([
    {
      Rules = [
        {
          Resource = ["collection/${local.name_prefix}-kb"]
          ResourceType = "collection"
        },
        {
          Resource = ["dashboard/${local.name_prefix}-kb"]
          ResourceType = "dashboard"
        }
      ]
      AllowFromPublic = true
    }
  ])
}

resource "aws_opensearchserverless_access_policy" "data" {
  name        = "${local.name_prefix}-kb-data"
  type        = "data"
  description = "Data access policy for Bedrock knowledge base collection"
  policy = jsonencode([
    {
      Rules = [
        {
          ResourceType = "index"
          Resource     = ["index/${local.name_prefix}-kb/*"]
          Permission   = ["aoss:CreateIndex", "aoss:DeleteIndex", "aoss:UpdateIndex", "aoss:DescribeIndex", "aoss:ReadDocument", "aoss:WriteDocument"]
        },
        {
          ResourceType = "collection"
          Resource     = ["collection/${local.name_prefix}-kb"]
          Permission   = ["aoss:CreateCollectionItems", "aoss:DeleteCollectionItems", "aoss:UpdateCollectionItems", "aoss:DescribeCollectionItems"]
        }
      ]
      Principal = [module.iam.knowledge_base_role_arn]
    }
  ])
}

resource "aws_opensearchserverless_collection" "kb" {
  name       = "${local.name_prefix}-kb"
  type       = "VECTORSEARCH"
  depends_on = [aws_opensearchserverless_security_policy.encryption, aws_opensearchserverless_security_policy.network]
}

resource "aws_bedrockagent_knowledge_base" "this" {
  name     = "${local.name_prefix}-kb"
  role_arn = module.iam.knowledge_base_role_arn
  knowledge_base_configuration {
    type = "VECTOR"
    vector_knowledge_base_configuration {
      embedding_model_arn = var.kb_embedding_model_arn
    }
  }
  storage_configuration {
    type = "OPENSEARCH_SERVERLESS"
    opensearch_serverless_configuration {
      collection_arn    = aws_opensearchserverless_collection.kb.arn
      vector_index_name = "incident-runbooks"
      field_mapping {
        vector_field   = "vector"
        text_field     = "text"
        metadata_field = "metadata"
      }
    }
  }
}

resource "aws_bedrockagent_data_source" "s3" {
  knowledge_base_id = aws_bedrockagent_knowledge_base.this.id
  name              = "${local.name_prefix}-kb-documents"
  data_source_configuration {
    type = "S3"
    s3_configuration {
      bucket_arn = module.s3.bucket_arn
    }
  }
}

resource "aws_cloudwatch_event_rule" "incident_alarm" {
  name        = "${local.name_prefix}-incident-events"
  description = "Routes CloudWatch alarm state changes to the AI agent Lambda"
  event_pattern = jsonencode({
    source      = ["aws.cloudwatch"]
    detail-type = ["CloudWatch Alarm State Change"]
  })
}

resource "aws_cloudwatch_event_target" "lambda" {
  rule      = aws_cloudwatch_event_rule.incident_alarm.name
  target_id = "CloudOpsAICopilotLambda"
  arn       = module.lambda.function_arn
}

resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = module.lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.incident_alarm.arn
}
