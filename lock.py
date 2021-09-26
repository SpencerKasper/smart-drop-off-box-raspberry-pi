from flask import Flask, render_template, request, redirect, url_for, make_response
import RPi.GPIO as GPIO
import boto3
import json

relay = 18
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(relay, GPIO.OUT)
GPIO.output(relay, 0)
app = Flask(__name__)

region_name = 'us-east-1'
queue_name = 'smart_drop_off_box_queue.fifo'
max_queue_messages = 10
message_bodies = []
aws_access_key_id = '<YOUR AWS ACCESS KEY ID>'
aws_secret_access_key = '<YOUR AWS SECRET ACCESS KEY>'
sqs = boto3.resource('sqs', region_name=region_name,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key)
queue = sqs.get_queue_by_name(QueueName=queue_name)
while True:
    messages_to_delete = []
    for message in queue.receive_messages(
            MaxNumberOfMessages=max_queue_messages):
        # process message body
        body = json.loads(message.body)
        message_bodies.append(body)
        # add message to delete
        messages_to_delete.append({
            'Id': message.message_id,
            'ReceiptHandle': message.receipt_handle
        })

    # if you don't receive any notifications the
    # messages_to_delete list will be empty
    if len(messages_to_delete) == 0:
        break
    # delete messages to remove them from SQS queue
    # handle any errors
    else:
        delete_response = queue.delete_messages(
                Entries=messages_to_delete)