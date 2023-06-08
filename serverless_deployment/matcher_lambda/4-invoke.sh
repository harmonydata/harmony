#!/bin/bash
set -eo pipefail
FUNCTION=$(aws cloudformation describe-stack-resource --stack-name harmony-matcher --logical-resource-id function --query 'StackResourceDetail.PhysicalResourceId' --output text)
aws lambda invoke --function-name $FUNCTION --payload file://example_to_match.json out.json
cat out.json
echo ""