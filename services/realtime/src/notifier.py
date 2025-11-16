import os
import json
import boto3
from boto3.dynamodb.types import TypeDeserializer

_des = TypeDeserializer()
_sns = boto3.client('sns')
TOPIC_ARN = os.environ['SNS_TOPIC_ARN']


def _ddeserialize(dynamo_image):
    if not dynamo_image:
        return {}
    return {k: _des.deserialize(v) for k, v in dynamo_image.items()}


def handler(event, _context):
    for rec in event.get('Records', []):
        et = rec.get('eventName')
        if et not in ('INSERT', 'MODIFY'):
            continue
        new = _ddeserialize(rec['dynamodb'].get('NewImage'))
        urg = (new.get('urgencia') or '').lower()
        status = (new.get('status') or '').lower()

        should_notify = urg in ('alta', 'crítica', 'critica') or status in ('in_progress', 'escalated')
        if not should_notify:
            continue

        msg = {
            'id': new.get('id'),
            'status': status,
            'urgencia': urg,
            'titulo': new.get('titulo'),
            'ubicacion': new.get('ubicacion'),
        }
        _sns.publish(TopicArn=TOPIC_ARN, Subject='AlertaUTEC Incidente', Message=json.dumps(msg))
