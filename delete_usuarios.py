import boto3
import os
import json

dynamodb = boto3.resource('dynamodb')
USERS_TABLE = os.environ['USERS_TABLE']
table = dynamodb.Table(USERS_TABLE)

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        tenant_id = body['tenantID']
        user_id = body['userID']

        response = table.delete_item(Key={'tenantID': tenant_id, 'userID': user_id})

        return {
            'statusCode': 204,
            'body': 'Usuario eliminado'
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }