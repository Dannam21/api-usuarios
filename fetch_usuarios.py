import boto3
import os

dynamodb = boto3.resource('dynamodb')
USERS_TABLE = os.environ['USERS_TABLE']
table = dynamodb.Table(USERS_TABLE)

def lambda_handler(event, context):
    last_evaluated_key = event.get('queryStringParameters', {}).get('lastEvaluatedKey')
    limit = int(event.get('queryStringParameters', {}).get('limit', 10))
    scan_params = {
        'Limit': limit,
    }

    if last_evaluated_key:
        scan_params['ExclusiveStartKey'] = last_evaluated_key

    response = table.scan(**scan_params)

    items = response.get('Items', [])
    last_evaluated_key = response.get('LastEvaluatedKey', None)

    return {
        'statusCode': 200,
        'body': {
            'usuarios': items,
            'lastEvaluatedKey': last_evaluated_key
        }
    }