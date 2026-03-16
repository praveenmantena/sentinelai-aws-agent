# Deployment

## Prerequisites

- AWS CLI configured with credentials that can create Bedrock, IAM, Lambda, API Gateway, DynamoDB, S3, EventBridge, and OpenSearch Serverless resources.
- Terraform 1.6 or later.
- A shell environment that can run the scripts in the scripts directory.
- Bedrock model access enabled in the target region.

## Deployment flow

1. Package the Lambda source.
2. Provision infrastructure with Terraform.
3. Upload runbooks to the knowledge bucket.
4. Sync the Bedrock Knowledge Base data source.
5. Invoke the API or trigger a CloudWatch alarm to validate the end-to-end path.

## Commands

```bash
cd infra/terraform
terraform init
terraform apply -var="environment=hackathon"
```

```bash
./scripts/seed_kb.sh <knowledge-bucket-name>
./scripts/deploy.sh hackathon us-east-1
```

## Cleanup

```bash
cd infra/terraform
terraform destroy -var="environment=hackathon"
```

## Notes

The Bedrock Knowledge Base in Terraform uses OpenSearch Serverless as the vector store. In production, tighten the network policy and replace public access with private VPC access where appropriate.
