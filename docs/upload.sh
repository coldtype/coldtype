aws s3 --region us-east-1 sync --cache-control no-cache --exclude "*" --include "*.html" _build/html s3://coldtype.goodhertz.co
aws s3 --region us-east-1 sync _build/html s3://coldtype.goodhertz.co