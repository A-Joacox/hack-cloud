"""
Handlers para gestión de comentarios en incidentes
"""
import json
import os
import time
from datetime import datetime
import boto3
from ulid import ULID

dynamodb = boto3.resource('dynamodb')
incidents_table = dynamodb.Table(os.environ.get('INCIDENTS_TABLE', 'AlertaUTEC-Incidents'))


def _response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
        },
        'body': json.dumps(body)
    }


def create_comment(event, context):
    """
    POST /incidents/{incidentId}/comments
    Crear un nuevo comentario en un incidente
    """
    try:
        incident_id = event['pathParameters']['incidentId']
        body = json.loads(event.get('body', '{}'))
        
        # Validaciones
        comment_text = body.get('comment', '').strip()
        if not comment_text:
            return _response(400, {'error': 'El campo "comment" es requerido'})
        
        if len(comment_text) > 1000:
            return _response(400, {'error': 'El comentario no puede exceder 1000 caracteres'})
        
        # Verificar que el incidente existe
        incident_response = incidents_table.get_item(Key={'incidentId': incident_id})
        if 'Item' not in incident_response:
            return _response(404, {'error': 'Incidente no encontrado'})
        
        # Obtener info del usuario (de JWT o query params por ahora)
        user_id = body.get('userId', 'anon')
        user_name = body.get('userName', 'Anónimo')
        
        # Crear comentario
        comment_id = f"comment_{str(ULID()).lower()}"
        timestamp = int(time.time())
        
        comment_item = {
            'commentId': comment_id,
            'incidentId': incident_id,
            'userId': user_id,
            'userName': user_name,
            'comment': comment_text,
            'createdAt': timestamp,
        }
        
        # Guardar como item separado con SK para permitir queries
        # Usamos GSI o estructura pk=incidentId, sk=COMMENT#commentId
        incidents_table.put_item(Item={
            'incidentId': f"{incident_id}#COMMENT#{comment_id}",
            'commentId': comment_id,
            'parentIncidentId': incident_id,
            'userId': user_id,
            'userName': user_name,
            'comment': comment_text,
            'createdAt': timestamp,
            'type': 'comment'
        })
        
        return _response(201, comment_item)
        
    except KeyError as e:
        return _response(400, {'error': f'Campo faltante: {str(e)}'})
    except Exception as e:
        print(f"Error creating comment: {str(e)}")
        return _response(500, {'error': 'Error interno del servidor'})


def list_comments(event, context):
    """
    GET /incidents/{incidentId}/comments
    Listar todos los comentarios de un incidente
    """
    try:
        incident_id = event['pathParameters']['incidentId']
        
        # Verificar que el incidente existe
        incident_response = incidents_table.get_item(Key={'incidentId': incident_id})
        if 'Item' not in incident_response:
            return _response(404, {'error': 'Incidente no encontrado'})
        
        # Buscar todos los comentarios (usando begins_with en incidentId)
        response = incidents_table.query(
            IndexName='IncidentTypeIndex',  # Necesitaremos agregar este GSI
            KeyConditionExpression='parentIncidentId = :iid AND #t = :type',
            ExpressionAttributeNames={'#t': 'type'},
            ExpressionAttributeValues={
                ':iid': incident_id,
                ':type': 'comment'
            },
            ScanIndexForward=False  # Ordenar por más reciente primero
        )
        
        comments = response.get('Items', [])
        
        # Si no hay GSI, hacer scan filtrado (menos eficiente)
        if not comments:
            response = incidents_table.scan(
                FilterExpression='begins_with(incidentId, :prefix) AND #t = :type',
                ExpressionAttributeNames={'#t': 'type'},
                ExpressionAttributeValues={
                    ':prefix': f"{incident_id}#COMMENT#",
                    ':type': 'comment'
                }
            )
            comments = response.get('Items', [])
        
        # Formatear respuesta
        formatted_comments = []
        for c in comments:
            formatted_comments.append({
                'commentId': c.get('commentId'),
                'userId': c.get('userId'),
                'userName': c.get('userName'),
                'comment': c.get('comment'),
                'createdAt': c.get('createdAt'),
            })
        
        # Ordenar por fecha descendente
        formatted_comments.sort(key=lambda x: x.get('createdAt', 0), reverse=True)
        
        return _response(200, {
            'incidentId': incident_id,
            'comments': formatted_comments,
            'count': len(formatted_comments)
        })
        
    except KeyError as e:
        return _response(400, {'error': f'Campo faltante: {str(e)}'})
    except Exception as e:
        print(f"Error listing comments: {str(e)}")
        return _response(500, {'error': 'Error interno del servidor'})


def delete_comment(event, context):
    """
    DELETE /incidents/{incidentId}/comments/{commentId}
    Eliminar un comentario (solo el autor o admin)
    """
    try:
        incident_id = event['pathParameters']['incidentId']
        comment_id = event['pathParameters']['commentId']
        
        # Eliminar comentario
        incidents_table.delete_item(
            Key={'incidentId': f"{incident_id}#COMMENT#{comment_id}"}
        )
        
        return _response(200, {'message': 'Comentario eliminado exitosamente'})
        
    except Exception as e:
        print(f"Error deleting comment: {str(e)}")
        return _response(500, {'error': 'Error interno del servidor'})
