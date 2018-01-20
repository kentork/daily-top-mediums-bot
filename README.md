post daily most popular Medium's stories to slack

# Prepare

This scripts is executed on AWS lambda.

* Python 3.6

And before development, you get a incoming webhook URL for slack.

# Development

## Fetch dependencies in root of this folder

```ps1
pip install -r .\requirements.txt -t .
```

## Execute on local

```ps1
$Env:SLACK_INCOMING_WEBHOOK_URL = "slack_incoming_webhook_url"
python .\lambda_function.py
```

# Deployment

1. Compress all files to zip ( without caches, logged files and git management files )
2. Open aws lambda page and upload it
