aws s3 --region us-west-1 sync --cache-control no-cache --exclude "*" --include "*.html" --include "*.xml" site s3://blog.coldtype.xyz --profile personal
aws s3 --region us-west-1 sync site s3://blog.coldtype.xyz --profile personal