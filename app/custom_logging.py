import boto3
import os
import time


# Initialize the CloudWatch client
client = boto3.client('logs', region_name='us-west-2', aws_access_key_id=os.environ.get("ACCESS_KEY"),
                      aws_secret_access_key=os.environ.get("ACCESS_SECRET"))

def send_log(log_message):
    response = client.put_log_events(
        logGroupName="LLM_Logger",
        logStreamName="stattest",
        logEvents=[
            {
                'timestamp': int(time.time() * 1000),
                'message': log_message
            }
        ]
    )