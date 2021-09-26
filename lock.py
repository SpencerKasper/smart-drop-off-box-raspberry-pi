from flask import Flask, render_template, request, redirect, url_for, make_response
import RPi.GPIO as GPIO
import boto3
import json
from time import sleep

relay = 18
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(relay, GPIO.OUT)
GPIO.output(relay, 0)
app = Flask(__name__)

region_name = 'us-east-1'
queue_name = 'smart_drop_off_box_queue.fifo'
max_queue_messages = 10
global message_bodies
message_bodies = []
aws_access_key_id = 'AKIA3HGQ5F2HIRBKUY6Z'
aws_secret_access_key = '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'
sqs = boto3.resource('sqs', region_name=region_name,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key)
queue = sqs.get_queue_by_name(QueueName=queue_name)
number_of_misses = 0


def poll_for_messages():
    print('Begin polling...')
    global message_bodies
    messages_to_delete = []
    for message in queue.receive_messages(
            MaxNumberOfMessages=max_queue_messages, WaitTimeSeconds=20):
        print('Message being processed...')
        # process message body
        body = json.loads(message.body)
        message_bodies.append(body)
        # add message to delete
        print(message.message_id)
        messages_to_delete.append({
            'Id': message.message_id,
            'ReceiptHandle': message.receipt_handle
        })

    if len(messages_to_delete) != 0:
        print('Messages to delete!')
        delete_response = queue.delete_messages(Entries=messages_to_delete)
    else:
        print('No messages to delete.')
    process_messages()        

def process_messages():
    global message_bodies
    global number_of_misses
    print(message_bodies)
    if(len(message_bodies) > 0):
        number_of_misses = 0
        for item in message_bodies:
            command_object = json.loads(item['Message'])
            command_type = command_object['commandType']
            if command_type == 'on':
                print('ON')
                GPIO.output(relay, 1)
            else:
                print('OFF')
                GPIO.output(relay, 0)
        poll_for_messages()
    else:
        number_of_misses = number_of_misses + 1
        delay = number_of_misses * 2
        print(f'No Message. Waiting for {delay} seconds...')
        sleep(delay)
        poll_for_messages()
        
        
poll_for_messages()