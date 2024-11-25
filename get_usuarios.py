import boto3
import os
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb')
USERS_TABLE = os.environ['USERS_TABLE']
table = dynamodb.Table(USERS_TABLE)

def lambda_handler(event, context):
    tenant_id = event.get('queryStringParameters', {}).get('tenantID')
    user_id = event.get('queryStringParameters', {}).get('userID')
    email = event.get('queryStringParameters', {}).get('email')

    if tenant_id and user_id:
        response = table.get_item(Key={'tenantID': tenant_id, 'userID': user_id})
    elif tenant_id and email:
        response = table.scan(
            FilterExpression=Attr('tenantID').eq(tenant_id) & Attr('email').eq(email)
        )
    else:
        return {'statusCode': 400, 'body': 'Debe proporcionar tenantID y userID o tenantID y email'}

    item = response.get('Item') if 'Item' in response else response.get('Items', [None])[0]

    if not item:
        return {'statusCode': 404, 'body': 'Usuario no encontrado'}

    item.pop('passwordHash', None)
    return {
        'statusCode': 200,
        'body': item
    }