import os
import time
import json
import boto3

_table = boto3.resource('dynamodb').Table(os.environ['CONNECTIONS_TABLE'])


def _get_claims(event):
    # Works with Lambda Authorizer that injects jwt.claims or simple query params fallback
    claims = event.get('requestContext', {}).get('authorizer', {}).get('jwt', {}).get('claims', {})
    if not claims:
        qs = event.get('queryStringParameters') or {}
        if qs:
            claims = {
                'sub': qs.get('sub') or 'anon',
                'role': qs.get('role') or 'student',
            }
    return claims or {'sub': 'anon', 'role': 'student'}


def on_connect(event, _context):
    request_ctx = event['requestContext']
    connection_id = request_ctx['connectionId']
    claims = _get_claims(event)
    item = {
        'pk': f'CONN#{connection_id}',
        'sk': 'META#',
        'userId': claims.get('sub', 'anon'),
        'role': claims.get('role', 'student'),
        'connectedAt': int(time.time())
    }
    _table.put_item(Item=item)
    return {"statusCode": 200, "body": json.dumps({"ok": True})}


def on_disconnect(event, _context):
    connection_id = event['requestContext']['connectionId']
    _table.delete_item(Key={'pk': f'CONN#{connection_id}', 'sk': 'META#'})
    return {"statusCode": 200, "body": json.dumps({"ok": True})}
