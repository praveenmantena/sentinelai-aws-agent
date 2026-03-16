data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "lambda" {
  name               = "${var.name_prefix}-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
  tags               = var.tags
}

data "aws_iam_policy_document" "lambda" {
  statement {
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
      "logs:FilterLogEvents"
    ]
    resources = ["*"]
  }

  statement {
    effect = "Allow"
    actions = [
      "bedrock:InvokeModel",
      "bedrock:InvokeModelWithResponseStream"
    ]
    resources = ["*"]
  }

  statement {
    effect = "Allow"
    actions = [
      "bedrock:Retrieve",
      "bedrock:RetrieveAndGenerate"
    ]
    resources = ["*"]
  }

  statement {
    effect = "Allow"
    actions = [
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:UpdateItem",
      "dynamodb:Query"
    ]
    resources = [var.incidents_table_arn]
  }

  statement {
    effect = "Allow"
    actions = [
      "s3:GetObject",
      "s3:ListBucket"
    ]
    resources = [var.knowledge_bucket_arn, "${var.knowledge_bucket_arn}/*"]
  }
}

resource "aws_iam_policy" "lambda" {
  name   = "${var.name_prefix}-lambda-policy"
  policy = data.aws_iam_policy_document.lambda.json
}

resource "aws_iam_role_policy_attachment" "lambda" {
  role       = aws_iam_role.lambda.name
  policy_arn = aws_iam_policy.lambda.arn
}

data "aws_iam_policy_document" "kb_assume_role" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["bedrock.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "knowledge_base" {
  name               = "${var.name_prefix}-kb-role"
  assume_role_policy = data.aws_iam_policy_document.kb_assume_role.json
  tags               = var.tags
}

data "aws_iam_policy_document" "knowledge_base" {
  statement {
    effect = "Allow"
    actions = [
      "bedrock:InvokeModel"
    ]
    resources = [var.embedding_model_arn]
  }

  statement {
    effect = "Allow"
    actions = [
      "aoss:APIAccessAll"
    ]
    resources = [var.knowledge_base_collection_arn]
  }

  statement {
    effect = "Allow"
    actions = [
      "s3:GetObject",
      "s3:ListBucket"
    ]
    resources = [var.knowledge_bucket_arn, "${var.knowledge_bucket_arn}/*"]
  }
}

resource "aws_iam_policy" "knowledge_base" {
  name   = "${var.name_prefix}-kb-policy"
  policy = data.aws_iam_policy_document.knowledge_base.json
}

resource "aws_iam_role_policy_attachment" "knowledge_base" {
  role       = aws_iam_role.knowledge_base.name
  policy_arn = aws_iam_policy.knowledge_base.arn
}
