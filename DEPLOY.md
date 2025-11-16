# 🚀 Guía de Despliegue - AWS Academy

## Opción Recomendada: Serverless Framework

### Pre-requisitos

1. **Node.js** instalado (v14+)
2. **Python 3.12** instalado
3. **AWS Academy** sesión activa
4. **Git** (ya lo tienes)

### Paso 1: Instalar Serverless Framework

```powershell
# Instalar globalmente
npm install -g serverless

# Verificar instalación
serverless --version
```

### Paso 2: Instalar Dependencias del Proyecto

```powershell
cd C:\Users\joacm\Desktop\hack-cloud\hack-ai

# Instalar dependencias Node.js
npm install
```

### Paso 3: Configurar Credenciales AWS Academy

**MUY IMPORTANTE**: Las credenciales de AWS Academy expiran cada pocas horas.

1. Ve a tu curso en **AWS Academy**
2. Click en **"Learner Lab"**
3. Click en **"AWS Details"** (esquina superior derecha)
4. Click en **"AWS CLI: Show"**
5. Copia todo el bloque de credenciales (se ve así):

```ini
[default]
aws_access_key_id=ASIA...
aws_secret_access_key=...
aws_session_token=IQoJb3JpZ2luX2VjE...
```

6. Pega ese contenido en: `C:\Users\joacm\.aws\credentials`

**Tip**: Cada vez que reinicies AWS Academy, tendrás que repetir este paso.

### Paso 4: Desplegar Todo el Stack

```powershell
# Desde la raíz del proyecto
serverless deploy

# Si tienes problemas con el perfil, usa:
serverless deploy --aws-profile default
```

**Esto desplegará**:
- ✅ 8 funciones Lambda
- ✅ API Gateway REST para incidents
- ✅ API Gateway WebSocket para real-time
- ✅ 3 tablas DynamoDB (Users, Incidents, Connections)
- ✅ DynamoDB Streams conectados
- ✅ Secret Manager para JWT
- ✅ SNS Topic para notificaciones

**Tiempo estimado**: 5-7 minutos ⏱️

### Paso 5: Obtener URLs

Al finalizar el despliegue verás:

```
✔ Service deployed to stack alerta-utec-dev

endpoints:
  POST - https://xxx.execute-api.us-east-1.amazonaws.com/dev/auth/register
  POST - https://xxx.execute-api.us-east-1.amazonaws.com/dev/auth/login
  POST - https://xxx.execute-api.us-east-1.amazonaws.com/dev/incidents
  PATCH - https://xxx.execute-api.us-east-1.amazonaws.com/dev/incidents/{id}
  GET - https://xxx.execute-api.us-east-1.amazonaws.com/dev/incidents
  
websocket: wss://yyy.execute-api.us-east-1.amazonaws.com/dev
```

**Guarda estas URLs**, las necesitarás para el frontend.

---

## Testing Rápido

### 1. Test de Autenticación

```powershell
# Registrar usuario (cambia la URL por la tuya)
$API_URL = "https://xxx.execute-api.us-east-1.amazonaws.com/dev"

curl -X POST "$API_URL/auth/register" `
  -H "Content-Type: application/json" `
  -d '{\"email\":\"joaquin@utec.edu.pe\",\"password\":\"Hack2024!\",\"nombre\":\"Joaquin\"}'

# Login (guarda el token que te devuelve)
curl -X POST "$API_URL/auth/login" `
  -H "Content-Type: application/json" `
  -d '{\"email\":\"joaquin@utec.edu.pe\",\"password\":\"Hack2024!\"}'
```

Respuesta esperada del login:
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "userId": "usr_..."
}
```

### 2. Test de Crear Incidente

```powershell
# Cambia TOKEN por el access_token del paso anterior
$TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -X POST "$API_URL/incidents" `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer $TOKEN" `
  -d '{\"titulo\":\"Robo en biblioteca\",\"descripcion\":\"Laptop robada\",\"ubicacion\":\"Biblioteca UTEC\",\"urgencia\":\"high\"}'
```

### 3. Test de WebSocket

1. Abre el archivo `services/realtime/demo-client.html` en un navegador
2. Cambia la URL WebSocket por la tuya (wss://yyy...)
3. Click en **"Connect"**
4. En otra terminal, crea un incidente (paso 2)
5. ¡Deberías ver el evento en tiempo real! 🎉

---

## Comandos Útiles

```powershell
# Ver logs en tiempo real
serverless logs -f createIncident --tail

# Ver logs de WebSocket
serverless logs -f wsConnect --tail

# Desplegar solo una función (si haces cambios)
serverless deploy function -f createIncident

# Ver info del stack
serverless info

# Ver recursos creados en AWS
serverless info --verbose

# Eliminar TODO (cuidado!)
serverless remove
```

---

## Troubleshooting

### ❌ Error: "Credentials expired"

**Solución**: Actualiza las credenciales desde AWS Academy (Paso 3).

### ❌ Error: "The role defined for the function cannot be assumed"

**Solución**: Verifica que el ARN del LabRole sea correcto en `serverless.yml`:
```yaml
iam:
  role: arn:aws:iam::527785891672:role/LabRole
```

### ❌ Error: "Rate exceeded"

**Solución**: AWS Academy tiene límites. Espera 2-3 minutos y reintenta.

### ❌ Error: Python dependencies

**Solución**: Asegúrate de tener **Docker Desktop** instalado y corriendo.

Si no tienes Docker:
```powershell
# Deshabilitar dockerizePip temporalmente
# En serverless.yml, cambia:
# dockerizePip: false
```

---

## Arquitectura Desplegada

```
┌─────────────────────────────────────────────────┐
│          API Gateway REST                       │
│  /auth/register  /auth/login                    │
│  /incidents [POST, GET, PATCH]                  │
└─────────────────┬───────────────────────────────┘
                  │
        ┌─────────▼─────────┐
        │  Lambda Functions │
        │  - authHandler    │
        │  - createIncident │
        │  - updateIncident │
        │  - listIncidents  │
        └─────────┬─────────┘
                  │
        ┌─────────▼─────────┐
        │  DynamoDB Tables  │
        │  - Users          │
        │  - Incidents      │◄─── Streams ───┐
        └───────────────────┘                 │
                                              │
        ┌─────────────────────────┐           │
        │  API Gateway WebSocket  │           │
        │  $connect  $disconnect  │           │
        └─────────┬───────────────┘           │
                  │                           │
        ┌─────────▼─────────┐    ┌───────────▼────────┐
        │  Lambda WS        │    │  Lambda Streams    │
        │  - wsConnect      │    │  - broadcaster     │
        │  - wsDisconnect   │    │  - notifier        │
        └───────────────────┘    └────────┬───────────┘
                                           │
                                  ┌────────▼────────┐
                                  │   SNS Topic     │
                                  │  (Email/SMS)    │
                                  └─────────────────┘
```

---

## Próximos Pasos

1. ✅ Backend desplegado y funcionando
2. 🔄 **Siguiente**: Crear el frontend en React/Next.js
3. 🔄 Conectar el frontend con estas APIs
4. 🔄 (Opcional) Agregar Apache Airflow para análisis de datos

**¡Ya tienes todo el backend en la nube!** 🚀
