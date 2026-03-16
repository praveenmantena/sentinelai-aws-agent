param(
    [Parameter(Mandatory = $true)]
    [string]$BucketName,

    [Parameter(Mandatory = $true)]
    [string]$ApiBaseUrl,

    [string]$Region = "us-east-1",
    [switch]$PublicRead
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$WebappDir = Join-Path $Root "webapp"
$DistDir = Join-Path $Root "dist\webapp"

if (-not (Test-Path $WebappDir)) {
    throw "webapp directory not found at $WebappDir"
}

New-Item -ItemType Directory -Path $DistDir -Force | Out-Null
Copy-Item -Path (Join-Path $WebappDir "*") -Destination $DistDir -Recurse -Force

$configContent = @"
window.APP_CONFIG = {
  API_BASE_URL: "$ApiBaseUrl"
};
"@
Set-Content -Path (Join-Path $DistDir "config.js") -Value $configContent -Encoding UTF8

aws s3api head-bucket --bucket $BucketName 2>$null
if ($LASTEXITCODE -ne 0) {
    if ($Region -eq "us-east-1") {
        aws s3api create-bucket --bucket $BucketName --region $Region | Out-Null
    } else {
        aws s3api create-bucket --bucket $BucketName --region $Region --create-bucket-configuration LocationConstraint=$Region | Out-Null
    }
}

aws s3 sync $DistDir "s3://$BucketName" --delete
aws s3api put-bucket-website --bucket $BucketName --website-configuration '{"IndexDocument":{"Suffix":"index.html"},"ErrorDocument":{"Key":"index.html"}}'

if ($PublicRead) {
    aws s3api put-public-access-block --bucket $BucketName --public-access-block-configuration BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false

    $policy = @{
        Version = "2012-10-17"
        Statement = @(
            @{
                Sid = "PublicReadGetObject"
                Effect = "Allow"
                Principal = "*"
                Action = "s3:GetObject"
                Resource = "arn:aws:s3:::$BucketName/*"
            }
        )
    } | ConvertTo-Json -Depth 8 -Compress

    aws s3api put-bucket-policy --bucket $BucketName --policy $policy
}

Write-Host "Webapp deployed to s3://$BucketName"
Write-Host "Website URL: http://$BucketName.s3-website-$Region.amazonaws.com"
