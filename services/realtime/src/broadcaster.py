import os
import json
import boto3
from boto3.dynamodb.types import TypeDeserializer

_des = TypeDeserializer()
_apigw = boto3.client('apigatewaymanagementapi', endpoint_url=os.environ['WS_CALLBACK_URL'])
_table = boto3.resource('dynamodb').Table(os.environ['CONNECTIONS_TABLE'])


def _ddeserialize(dynamo_image):
    if not dynamo_image:
        return {}
    return {k: _des.deserialize(v) for k, v in dynamo_image.items()}


def build_payload(event_type, new_img, old_img):
    if event_type == 'INSERT':
        inc = _ddeserialize(new_img)
        return {
            'type': 'IncidentCreated',
            'incidentId': inc.get('incidentId'),
            'status': inc.get('status'),
            'urgencia': inc.get('urgencia'),
            'ubicacion': inc.get('ubicacion'),
            'titulo': inc.get('titulo'),
            'descripcion': inc.get('descripcion'),
            'createdAt': inc.get('createdAt'),
        }
    if event_type == 'MODIFY':
        new = _ddeserialize(new_img)
        old = _ddeserialize(old_img)
        if new.get('status') == old.get('status') and new.get('urgencia') == old.get('urgencia'):
            return None
        return {
            'type': 'IncidentStatusChanged',
            'incidentId': new.get('incidentId'),
            'status': new.get('status'),
            'urgencia': new.get('urgencia'),
            'updatedAt': new.get('updatedAt'),
        }
    return None


def handler(event, _context):
    # Fan-out simple: enviar a todas las conexiones registradas
    # Para segmentación por rol o scope, añadir filtros/índices
    items = _table.scan(ProjectionExpression='pk').get('Items', [])
    connection_ids = [it['pk'].split('#', 1)[1] for it in items]

    for rec in event.get('Records', []):
        et = rec.get('eventName')
        if et not in ('INSERT', 'MODIFY'):
            continue
        payload = build_payload(et, rec['dynamodb'].get('NewImage'), rec['dynamodb'].get('OldImage'))
        if not payload:
            continue
        data = json.dumps(payload).encode('utf-8')
        for cid in connection_ids:
            try:
                _apigw.post_to_connection(ConnectionId=cid, Data=data)
            except _apigw.exceptions.GoneException:
                # limpiar conexiones caídas
                _table.delete_item(Key={'pk': f'CONN#{cid}', 'sk': 'META#'})
