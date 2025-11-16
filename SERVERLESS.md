# Serverless Framework - AlertaUTEC

## Requisitos

```bash
# Instalar Serverless Framework
npm install -g serverless

# Instalar plugin para Python
npm install --save-dev serverless-python-requirements
```

## Desplegar TODO de una vez

```bash
# Deploy completo (auth + incidents + realtime)
serverless deploy

# O con stage específico
serverless deploy --stage prod
```

## Deploy selectivo

```bash
# Solo una función
serverless deploy function -f createIncident

# Remover todo
serverless remove
```

## Obtener info después de deploy

```bash
# Ver outputs (URLs, ARNs)
serverless info

# Ver logs en tiempo real
serverless logs -f createIncident -t
serverless logs -f broadcaster -t
```

## Variables de entorno

Todas se configuran automáticamente:
- `USERS_TABLE` → alerta-utec-users-dev
- `INCIDENTS_TABLE` → alerta-utec-incidents-dev
- `CONNECTIONS_TABLE` → alerta-utec-connections-dev
- `JWT_SECRET_ARN` → arn del secret generado
- `SNS_TOPIC_ARN` → arn del topic SNS
- `WS_CALLBACK_URL` → URL del WebSocket API

## Testing local

```bash
# Invocar función localmente
serverless invoke local -f createIncident -d '{
  "body": "{\"titulo\":\"Test\",\"ubicacion\":\"Lab A\"}",
  "requestContext": {
    "authorizer": {"sub": "user123", "email": "test@utec.edu.pe"}
  }
}'
```

## Ventajas vs SAM

- ✅ Un solo archivo para todo
- ✅ Deploy más rápido
- ✅ Sintaxis más simple
- ✅ Plugins (Python requirements, warmup, etc)
- ✅ Multi-provider (AWS, Azure, GCP)
