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
        nombre = body.get('nombre')
        email = body.get('email')

        update_expression = "set "
        expression_attribute_values = {}

        if nombre:
            update_expression += "nombre = :nombre, "
            expression_attribute_values[':nombre'] = nombre

        if email:
            update_expression += "email = :email, "
            expression_attribute_values[':email'] = email

        update_expression = update_expression.rstrip(', ')

        response = table.update_item(
            Key={'tenantID': tenant_id, 'userID': user_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues="UPDATED_NEW"
        )

        return {
            'statusCode': 200,
            'body': json.dumps(response['Attributes'])
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }