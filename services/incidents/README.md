# Servicio de Gestión de Incidentes

Backend REST API para crear, actualizar y consultar incidentes del campus UTEC.

## Arquitectura

```
Cliente (JWT) → API Gateway REST → Lambda Authorizer (valida JWT)
                                            ↓
                                    Lambda CRUD Handlers
                                            ↓
                                    DynamoDB (AlertaUTEC-Incidents)
                                            ↓
                                    DynamoDB Streams
                                            ↓
                        ┌───────────────────┴───────────────────┐
                        ↓                                       ↓
                Lambda Broadcaster                      Lambda Notifier
                (WebSocket)                             (SNS)
```

## Endpoints

### POST /incidents
Crear un nuevo incidente.

**Headers:**
```
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

**Body:**
```json
{
  "titulo": "Fuga de gas en laboratorio",
  "ubicacion": "Edificio B - Lab 201",
  "urgencia": "alta",
  "descripcion": "Se detectó olor a gas en el laboratorio de química"
}
```

**Response 201:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "titulo": "Fuga de gas en laboratorio",
  "ubicacion": "Edificio B - Lab 201",
  "urgencia": "alta",
  "descripcion": "Se detectó olor a gas en el laboratorio de química",
  "status": "pending",
  "reporterId": "user123",
  "reporterEmail": "estudiante@utec.edu.pe",
  "createdAt": 1700000000,
  "updatedAt": 1700000000
}
```

### PATCH /incidents/{id}
Actualizar el estado o urgencia de un incidente existente.

**Headers:**
```
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

**Body:**
```json
{
  "status": "in_progress",
  "assignedTo": "admin@utec.edu.pe"
}
```

**Response 200:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "in_progress",
  "urgencia": "alta",
  "assignedTo": "admin@utec.edu.pe",
  "updatedAt": 1700000100
}
```

### GET /incidents
Listar todos los incidentes, opcionalmente filtrados por estado.

**Headers:**
```
Authorization: Bearer <JWT_TOKEN>
```

**Query Parameters:**
- `status` (opcional): filtrar por estado (pending, in_progress, resolved)

**Ejemplos:**
- `/incidents` - todos los incidentes
- `/incidents?status=pending` - solo pendientes

**Response 200:**
```json
{
  "incidents": [
    {
      "id": "...",
      "titulo": "...",
      "status": "pending",
      "urgencia": "alta",
      "createdAt": 1700000000
    }
  ],
  "count": 1
}
```

## Despliegue (AWS Academy)

### Requisitos previos
- AWS SAM CLI instalado
- Docker (opcional, para `sam build --use-container`)
- Tabla DynamoDB `AlertaUTEC-Incidents` con Streams habilitado
- Secret en Secrets Manager con el JWT signing key

### Pasos

```bash
cd services/incidents

# Build
sam build --use-container

# Deploy
sam deploy \
  --template-file .aws-sam/build/template.yaml \
  --stack-name alerta-incidents \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides \
    LabRoleArn=arn:aws:iam::527785891672:role/LabRole \
    IncidentsTableName=AlertaUTEC-Incidents \
  --resolve-s3 \
  --region us-east-1

# Obtener URL de la API
aws cloudformation describe-stacks \
  --stack-name alerta-incidents \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
  --output text
```

## Pruebas con curl

### 1. Obtener JWT token (desde el servicio de auth)
```bash
API_AUTH="https://<AUTH_API_ID>.execute-api.us-east-1.amazonaws.com/prod"

# Login
TOKEN=$(curl -X POST $API_AUTH/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@utec.edu.pe",
    "password": "SecurePassword123!"
  }' | jq -r '.accessToken')

echo $TOKEN
```

### 2. Crear incidente
```bash
API_URL="https://<INCIDENTS_API_ID>.execute-api.us-east-1.amazonaws.com/prod"

curl -X POST $API_URL/incidents \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "titulo": "Incidente de prueba",
    "ubicacion": "Lab A101",
    "urgencia": "media",
    "descripcion": "Prueba del sistema"
  }'
```

### 3. Listar incidentes
```bash
curl -X GET $API_URL/incidents \
  -H "Authorization: Bearer $TOKEN"
```

### 4. Actualizar incidente
```bash
INCIDENT_ID="<ID_DEL_INCIDENTE>"

curl -X PATCH $API_URL/incidents/$INCIDENT_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "resolved"
  }'
```

## Variables de entorno

- `INCIDENTS_TABLE`: nombre de la tabla DynamoDB (default: AlertaUTEC-Incidents)
- `JWT_SECRET_ARN`: ARN del secret en Secrets Manager con el JWT signing key

## Integración con tiempo real

Cuando se crea o actualiza un incidente:
1. Se escribe en DynamoDB
2. DynamoDB Streams detecta el cambio
3. Lambda Broadcaster envía evento WebSocket a todos los clientes conectados
4. Lambda Notifier publica a SNS si urgencia es alta/crítica

## Estructura del proyecto

```
services/incidents/
├── src/
│   ├── handlers.py        # Handlers para crear, actualizar, listar incidentes
│   └── authorizer.py      # Lambda authorizer para validar JWT
├── template.yaml          # SAM template con API Gateway + Lambdas
├── requirements.txt       # Dependencias Python
└── README.md             # Este archivo
```

## Campos del incidente

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | string | UUID único del incidente |
| titulo | string | Título descriptivo (requerido) |
| ubicacion | string | Ubicación física del incidente (requerido) |
| urgencia | string | Nivel: baja, media, alta, crítica (default: baja) |
| status | string | Estado: pending, in_progress, resolved (default: pending) |
| descripcion | string | Descripción detallada (opcional) |
| reporterId | string | ID del usuario que reporta (extraído del JWT) |
| reporterEmail | string | Email del reporter (extraído del JWT) |
| assignedTo | string | Email del responsable asignado (opcional) |
| createdAt | number | Timestamp de creación (epoch seconds) |
| updatedAt | number | Timestamp de última actualización (epoch seconds) |

## Estado del proyecto

- ✅ CRUD completo (crear, actualizar, listar)
- ✅ Validación JWT con Lambda Authorizer
- ✅ Validaciones de entrada (titulo y ubicacion requeridos)
- ✅ Manejo de errores con status codes apropiados
- ✅ Headers CORS para frontend
- ✅ Integración con DynamoDB Streams (para tiempo real)
- 🔄 Pendiente: Tests unitarios
- 🔄 Pendiente: Upload de attachments a S3
