#!/bin/bash
set -eo pipefail
FUNCTION=$(aws cloudformation describe-stack-resource --stack-name harmony-tika --logical-resource-id function --query 'StackResourceDetail.PhysicalResourceId' --output text)
aws lambda invoke --function-name $FUNCTION --payload fileb://tiny_pdf.json out.json
cat out.json
echo ""