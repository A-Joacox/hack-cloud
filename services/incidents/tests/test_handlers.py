import sys
import os
import json
import pytest
from unittest.mock import MagicMock, patch
from decimal import Decimal

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from handlers import create_incident, update_incident, list_incidents, get_claims


@pytest.fixture
def mock_table():
    with patch('handlers.table') as mock:
        yield mock


@pytest.fixture
def event_with_claims():
    return {
        'requestContext': {
            'authorizer': {
                'sub': 'user123',
                'role': 'student',
                'email': 'test@utec.edu.pe'
            }
        },
        'body': json.dumps({
            'titulo': 'Test incident',
            'ubicacion': 'Lab A101',
            'urgencia': 'alta'
        })
    }


def test_get_claims_with_authorizer():
    event = {
        'requestContext': {
            'authorizer': {
                'sub': 'user123',
                'role': 'admin',
                'email': 'admin@utec.edu.pe'
            }
        }
    }
    claims = get_claims(event)
    assert claims['sub'] == 'user123'
    assert claims['role'] == 'admin'
    assert claims['email'] == 'admin@utec.edu.pe'


def test_get_claims_without_authorizer():
    event = {'requestContext': {}}
    claims = get_claims(event)
    assert claims == {}


def test_create_incident_success(mock_table, event_with_claims):
    mock_table.put_item.return_value = {}
    
    response = create_incident(event_with_claims, None)
    
    assert response['statusCode'] == 201
    body = json.loads(response['body'])
    assert body['titulo'] == 'Test incident'
    assert body['ubicacion'] == 'Lab A101'
    assert body['urgencia'] == 'alta'
    assert body['status'] == 'pending'
    assert body['reporterId'] == 'user123'
    assert 'id' in body
    assert 'createdAt' in body
    mock_table.put_item.assert_called_once()


def test_create_incident_missing_titulo(mock_table):
    event = {
        'requestContext': {'authorizer': {'sub': 'user123'}},
        'body': json.dumps({'ubicacion': 'Lab A101'})
    }
    
    response = create_incident(event, None)
    
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert 'titulo' in body['error']
    mock_table.put_item.assert_not_called()


def test_create_incident_missing_ubicacion(mock_table):
    event = {
        'requestContext': {'authorizer': {'sub': 'user123'}},
        'body': json.dumps({'titulo': 'Test'})
    }
    
    response = create_incident(event, None)
    
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert 'ubicacion' in body['error']
    mock_table.put_item.assert_not_called()


def test_update_incident_success(mock_table):
    event = {
        'pathParameters': {'id': 'inc-123'},
        'requestContext': {'authorizer': {'sub': 'admin'}},
        'body': json.dumps({'status': 'in_progress', 'urgencia': 'critica'})
    }
    mock_table.update_item.return_value = {
        'Attributes': {
            'id': 'inc-123',
            'status': 'in_progress',
            'urgencia': 'critica',
            'updatedAt': 1700000100
        }
    }
    
    response = update_incident(event, None)
    
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['status'] == 'in_progress'
    assert body['urgencia'] == 'critica'
    mock_table.update_item.assert_called_once()


def test_update_incident_no_fields(mock_table):
    event = {
        'pathParameters': {'id': 'inc-123'},
        'requestContext': {'authorizer': {'sub': 'admin'}},
        'body': json.dumps({})
    }
    
    response = update_incident(event, None)
    
    assert response['statusCode'] == 400
    mock_table.update_item.assert_not_called()


def test_list_incidents_all(mock_table):
    event = {'requestContext': {'authorizer': {'sub': 'user'}}}
    mock_table.scan.return_value = {
        'Items': [
            {'id': 'inc-1', 'titulo': 'Test 1', 'createdAt': 1700000000},
            {'id': 'inc-2', 'titulo': 'Test 2', 'createdAt': 1700000100}
        ]
    }
    
    response = list_incidents(event, None)
    
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['count'] == 2
    assert len(body['incidents']) == 2
    # Debe estar ordenado por createdAt descendente
    assert body['incidents'][0]['id'] == 'inc-2'
    assert body['incidents'][1]['id'] == 'inc-1'


def test_list_incidents_with_status_filter(mock_table):
    event = {
        'queryStringParameters': {'status': 'pending'},
        'requestContext': {'authorizer': {'sub': 'user'}}
    }
    mock_table.scan.return_value = {
        'Items': [{'id': 'inc-1', 'status': 'pending', 'createdAt': 1700000000}]
    }
    
    response = list_incidents(event, None)
    
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['count'] == 1
    mock_table.scan.assert_called_once()
    call_args = mock_table.scan.call_args
    assert 'FilterExpression' in call_args[1]
