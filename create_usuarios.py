import boto3
import hashlib
import os
import json
import logging
from boto3.dynamodb.conditions import Attr

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
USERS_TABLE = os.environ['USERS_TABLE']
TIENDAS_TABLE = os.environ['TIENDAS_TABLE']
table = dynamodb.Table(USERS_TABLE)
tiendas_table = dynamodb.Table(TIENDAS_TABLE)

# Hash password function
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def lambda_handler(event, context):
    try:
        # Log the received event
        logger.info("Received event: %s", json.dumps(event))

        # Parse the event body
        body = json.loads(event['body'])
        tenant_id = body.get('tenantID')
        email = body.get('email')
        nombre = body.get('nombre')
        password = body.get('password')

        # Validate required fields
        if not tenant_id or not email or not nombre or not password:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing tenantID, email, nombre, or password'})
            }

        # Verificar si ya existe una tienda para este tenantID
        response = tiendas_table.scan(
            FilterExpression=Attr('tenantID').eq(tenant_id)
        )
        if not response['Items']:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'No existe una tienda para este tenantID'})
            }

        # Verificar si el usuario ya existe
        response = table.scan(
            FilterExpression=Attr('tenantID').eq(tenant_id) & Attr('email').eq(email)
        )
        if response['Items']:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Email already exists for this tenant'})
            }

        # Hash the password
        password_hash = hash_password(password)

        # Generate user ID and creation date
        year_prefix = datetime.datetime.utcnow().strftime('%Y')
        user_id = f"{year_prefix}-{str(uuid.uuid4())}"
        fecha_creacion = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')

        # Create user item
        usuario = {
            'tenantID': tenant_id,
            'userID': user_id,
            'fechaCreacion': fecha_creacion,
            'nombre': nombre,
            'email': email,
            'passwordHash': password_hash,
            'ultimoAcceso': fecha_creacion
        }

        # Store user in DynamoDB
        table.put_item(Item=usuario)

        # Return success response
        return {
            'statusCode': 201,
            'body': json.dumps({
                'message': 'Usuario creado',
                'tenantID': tenant_id,
                'userID': user_id,
                'fechaCreacion': fecha_creacion
            })
        }
    except Exception as e:
        logger.error("Error creating user: %s", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
