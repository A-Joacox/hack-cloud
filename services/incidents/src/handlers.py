def dummy_authorizer(event, context):
    # Permite todo (solo para pruebas, reemplaza por tu validador JWT real)
    return {
        "principalId": "user|anon",
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": "Allow",
                    "Resource": event["methodArn"]
                }
            ]
        },
        "context": {
            "sub": "anon",
            "role": "student"
        }
    }
import os
import json
import boto3
import uuid
import time
from boto3.dynamodb.conditions import Key

ddb = boto3.resource('dynamodb')
TABLE = os.environ.get('INCIDENTS_TABLE', 'AlertaUTEC-Incidents')
table = ddb.Table(TABLE)

# Utilidad para extraer claims del contexto de API Gateway

def get_claims(event):
    """Extrae claims del authorizer (Lambda Token Authorizer)"""
    ctx = event.get('requestContext', {})
    # Para Lambda Token Authorizer, los claims están en authorizer directamente
    authorizer = ctx.get('authorizer', {})
    if authorizer:
        return {
            'sub': authorizer.get('sub'),
            'role': authorizer.get('role'),
            'email': authorizer.get('email')
        }
    return {}

# Crear incidente

def create_incident(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        claims = get_claims(event)
        
        # Validaciones básicas
        if not body.get('titulo'):
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'titulo es requerido'})
            }
        if not body.get('ubicacion'):
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'ubicacion es requerida'})
            }
        
        incident_id = body.get('id') or str(uuid.uuid4())
        now = int(time.time())
        
        item = {
            'id': incident_id,
            'status': body.get('status', 'pending'),
            'urgencia': body.get('urgencia', 'baja'),
            'ubicacion': body.get('ubicacion'),
            'titulo': body.get('titulo'),
            'descripcion': body.get('descripcion', ''),
            'reporterId': claims.get('sub', body.get('reporterId', 'anon')),
            'reporterEmail': claims.get('email', ''),
            'createdAt': now,
            'updatedAt': now
        }
        
        table.put_item(Item=item)
        
        return {
            'statusCode': 201,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(item)
        }
    except Exception as e:
        print(f'Error creating incident: {e}')
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Internal server error'})
        }

# Actualizar incidente (solo status y urgencia)

def update_incident(event, context):
    try:
        incident_id = event['pathParameters']['id']
        body = json.loads(event.get('body', '{}'))
        claims = get_claims(event)
        
        update_expr = []
        expr_attr = {}
        expr_attr_names = {}
        
        if 'status' in body:
            update_expr.append('#s = :status')
            expr_attr[':status'] = body['status']
            expr_attr_names['#s'] = 'status'
            
        if 'urgencia' in body:
            update_expr.append('urgencia = :urgencia')
            expr_attr[':urgencia'] = body['urgencia']
            
        if 'assignedTo' in body:
            update_expr.append('assignedTo = :assignedTo')
            expr_attr[':assignedTo'] = body['assignedTo']
            
        if not update_expr:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'No fields to update'})
            }
        
        # Agregar updatedAt automáticamente
        update_expr.append('updatedAt = :updatedAt')
        expr_attr[':updatedAt'] = int(time.time())
        
        update_kwargs = {
            'Key': {'id': incident_id},
            'UpdateExpression': 'SET ' + ', '.join(update_expr),
            'ExpressionAttributeValues': expr_attr,
            'ReturnValues': 'ALL_NEW'
        }
        
        if expr_attr_names:
            update_kwargs['ExpressionAttributeNames'] = expr_attr_names
        
        resp = table.update_item(**update_kwargs)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(resp['Attributes'])
        }
    except KeyError:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Missing incident id'})
        }
    except Exception as e:
        print(f'Error updating incident: {e}')
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Internal server error'})
        }

# Consultar incidentes (todos o por status)

def list_incidents(event, context):
    try:
        params = event.get('queryStringParameters') or {}
        status = params.get('status')
        
        scan_kwargs = {}
        if status:
            scan_kwargs['FilterExpression'] = Key('status').eq(status)
        
        resp = table.scan(**scan_kwargs)
        items = resp.get('Items', [])
        
        # Ordenar por createdAt descendente
        items.sort(key=lambda x: x.get('createdAt', 0), reverse=True)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'incidents': items,
                'count': len(items)
            })
        }
    except Exception as e:
        print(f'Error listing incidents: {e}')
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Internal server error'})
        }
