#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: ./scripts/seed_kb.sh <knowledge-bucket-name> [prefix]"
  exit 1
fi

BUCKET_NAME="$1"
PREFIX="${2:-runbooks}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

aws s3 sync "${ROOT_DIR}/docs/knowledge-base" "s3://${BUCKET_NAME}/${PREFIX}" --delete

echo "Uploaded knowledge documents to s3://${BUCKET_NAME}/${PREFIX}"
