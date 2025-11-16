import os
import json
import boto3
import jwt
from functools import lru_cache

@lru_cache(maxsize=1)
def _resolve_secret():
    secret_value = os.environ.get('JWT_SECRET_VALUE')
    if secret_value:
        return secret_value
    
    secret_arn = os.environ.get('JWT_SECRET_ARN')
    if secret_arn:
        client = boto3.client('secretsmanager')
        resp = client.get_secret_value(SecretId=secret_arn)
        secret_string = resp.get('SecretString')
        if secret_string:
            try:
                parsed = json.loads(secret_string)
                return parsed.get('JWT_SIGNING_KEY') or secret_string
            except json.JSONDecodeError:
                return secret_string
    
    raise RuntimeError('JWT signing secret not configured')

def verify_token(token):
    secret = _resolve_secret()
    return jwt.decode(token, secret, algorithms=['HS256'])

def authorizer_handler(event, context):
    """Lambda authorizer para validar JWT en API Gateway"""
    token = event.get('authorizationToken', '').replace('Bearer ', '')
    
    if not token:
        raise Exception('Unauthorized')
    
    try:
        claims = verify_token(token)
    except Exception as err:
        print(f'Invalid token: {err}')
        raise Exception('Unauthorized')
    
    # Formato para API Gateway Lambda Authorizer
    return {
        'principalId': claims['sub'],
        'policyDocument': {
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Action': 'execute-api:Invoke',
                    'Effect': 'Allow',
                    'Resource': event['methodArn']
                }
            ]
        },
        'context': {
            'sub': claims['sub'],
            'role': claims.get('role', 'student'),
            'email': claims.get('email', '')
        }
    }
