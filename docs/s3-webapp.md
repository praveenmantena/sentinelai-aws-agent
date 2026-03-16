# S3 Lightweight Web UI

This project includes a static web UI in `webapp/` that can be hosted on Amazon S3 and used with the SentinelAI backend API.

## What it provides

- Incident JSON input and one-click investigation execution
- Response view with root cause, diagnosis, confidence, and raw JSON
- Remediation approval controls (approve, reject, pending)
- Local browser persistence of approvals using `localStorage`

## Prerequisites

- Existing backend API endpoint from Terraform output `api_endpoint`
- AWS CLI configured with permissions for S3 bucket operations

## Deploy to S3

From the repository root:

```powershell
./scripts/deploy_webapp_s3.ps1 -BucketName <your-ui-bucket> -ApiBaseUrl <api-endpoint> -Region us-east-1 -PublicRead
```

Example:

```powershell
./scripts/deploy_webapp_s3.ps1 -BucketName sentinelai-ui-demo-123456 -ApiBaseUrl https://abcde12345.execute-api.us-east-1.amazonaws.com -Region us-east-1 -PublicRead
```

## Security note

`-PublicRead` makes the bucket website publicly readable for hackathon demos. For production, front this with CloudFront and lock bucket access with Origin Access Control.

## Browser usage

1. Open the S3 website URL printed by the script.
2. Confirm API endpoint is auto-filled.
3. Paste or load incident JSON.
4. Click **Run Investigation**.
5. Review response and record remediation decisions.
