import boto3
import json

def lambda_handler(event, context):
    try:
        print("\nReceived event:")
        print(event)
        print("\nExtracted Values:")
        print("Source:" + event['source'])
        print("Event Name:" + event['detail']['eventName'])
        print("Account Id:" + event['detail']['requestParameters']['accountId'])
        print("Destination OU Id:" + event['detail']['requestParameters']['destinationParentId'])
        print("Source OU Id:" + event['detail']['requestParameters']['sourceParentId'])
        print("Destination OU Id:" + event['detail']['requestParameters']['destinationParentId'] + "\n")
    except:
        raise

if __name__ == '__main__':
       lambda_handler()
