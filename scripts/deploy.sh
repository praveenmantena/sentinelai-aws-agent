#!/usr/bin/env bash
set -euo pipefail

ENVIRONMENT="${1:-hackathon}"
AWS_REGION="${2:-us-east-1}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST_DIR="${ROOT_DIR}/dist"
PACKAGE_PATH="${DIST_DIR}/sentinelai_aws_agent.zip"

mkdir -p "${DIST_DIR}"
rm -f "${PACKAGE_PATH}"

pushd "${ROOT_DIR}" >/dev/null
zip -r "${PACKAGE_PATH}" src requirements.txt >/dev/null
popd >/dev/null

pushd "${ROOT_DIR}/infra/terraform" >/dev/null
terraform init
terraform apply \
  -var="environment=${ENVIRONMENT}" \
  -var="aws_region=${AWS_REGION}" \
  -var="lambda_package_path=${PACKAGE_PATH}" \
  -auto-approve
popd >/dev/null

echo "Deployment completed for environment ${ENVIRONMENT} in ${AWS_REGION}."
