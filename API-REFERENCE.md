# 📚 API Reference - AlertaUTEC

Documentación completa de todos los endpoints y servicios desplegados.

---

## 🔐 **Authentication Service**

**Base URL:** `https://rgs5nn9vgf.execute-api.us-east-1.amazonaws.com/dev`

### **POST /auth/register**
Registrar un nuevo usuario en el sistema.

**Request:**
```json
{
  "email": "usuario@utec.edu.pe",
  "password": "password123",
  "nombre": "Juan Pérez"
}
```

**Response (201 Created):**
```json
{
  "user": {
    "userId": "01JCZX...",
    "email": "usuario@utec.edu.pe",
    "nombre": "Juan Pérez",
    "role": "student"
  },
  "accessToken": "eyJhbGc...",
  "refreshToken": "eyJhbGc...",
  "tokenType": "Bearer",
  "expiresIn": 3600
}
```

**Ejemplo curl:**
```bash
curl -X POST https://rgs5nn9vgf.execute-api.us-east-1.amazonaws.com/dev/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@utec.edu.pe",
    "password": "test123",
    "nombre": "Test User"
  }'
```

---

### **POST /auth/login**
Iniciar sesión y obtener tokens JWT.

**Request:**
```json
{
  "email": "usuario@utec.edu.pe",
  "password": "password123"
}
```

**Response (200 OK):**
```json
{
  "user": {
    "userId": "01JCZX...",
    "email": "usuario@utec.edu.pe",
    "nombre": "Juan Pérez",
    "role": "student"
  },
  "accessToken": "eyJhbGc...",
  "refreshToken": "eyJhbGc...",
  "tokenType": "Bearer",
  "expiresIn": 3600
}
```

**Ejemplo curl:**
```bash
curl -X POST https://rgs5nn9vgf.execute-api.us-east-1.amazonaws.com/dev/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@utec.edu.pe",
    "password": "test123"
  }'
```

---

## 🚨 **Incidents Service**

**Base URL:** `https://wkcu4ednm9.execute-api.us-east-1.amazonaws.com/prod`

### **POST /incidents**
Crear un nuevo incidente.

**Request:**
```json
{
  "titulo": "Incendio en cafetería",
  "descripcion": "Humo saliendo de la cocina principal",
  "ubicacion": "Cafetería Central - Piso 1",
  "urgencia": "alta"
}
```

**Campos:**
- `titulo` (string, required): Título breve del incidente
- `descripcion` (string, required): Descripción detallada
- `ubicacion` (string, required): Ubicación exacta del incidente
- `urgencia` (string, optional): `baja`, `media`, `alta` (default: `media`)

**Response (201 Created):**
```json
{
  "incidentId": "inc_8c2f606e",
  "status": "open",
  "urgencia": "alta",
  "ubicacion": "Cafetería Central - Piso 1",
  "titulo": "Incendio en cafetería",
  "descripcion": "Humo saliendo de la cocina principal",
  "reporterId": "anon",
  "reporterEmail": "",
  "createdAt": 1763285042,
  "updatedAt": 1763285042
}
```

**Ejemplo curl:**
```bash
curl -X POST https://wkcu4ednm9.execute-api.us-east-1.amazonaws.com/prod/incidents \
  -H "Content-Type: application/json" \
  -d '{
    "titulo": "Robo en biblioteca",
    "descripcion": "Persona sospechosa robando laptops",
    "ubicacion": "Biblioteca, 3er piso",
    "urgencia": "alta"
  }'
```

---

### **GET /incidents**
Listar todos los incidentes (con filtros opcionales).

**Query Parameters:**
- `status` (optional): Filtrar por estado (`open`, `in_progress`, `resolved`)

**Response (200 OK):**
```json
{
  "incidents": [
    {
      "incidentId": "inc_8c2f606e",
      "status": "open",
      "urgencia": "alta",
      "ubicacion": "Cafetería Central",
      "titulo": "Incendio en cafetería",
      "createdAt": 1763285042
    }
  ],
  "count": 1
}
```

**Ejemplo curl:**
```bash
# Listar todos los incidentes
curl https://wkcu4ednm9.execute-api.us-east-1.amazonaws.com/prod/incidents

# Filtrar solo incidentes abiertos
curl "https://wkcu4ednm9.execute-api.us-east-1.amazonaws.com/prod/incidents?status=open"
```

---

### **GET /incidents/{incidentId}**
Obtener detalles de un incidente específico.

**Response (200 OK):**
```json
{
  "incidentId": "inc_8c2f606e",
  "status": "open",
  "urgencia": "alta",
  "ubicacion": "Cafetería Central",
  "titulo": "Incendio en cafetería",
  "descripcion": "Humo saliendo de la cocina",
  "reporterId": "anon",
  "createdAt": 1763285042,
  "updatedAt": 1763285042
}
```

**Ejemplo curl:**
```bash
curl https://wkcu4ednm9.execute-api.us-east-1.amazonaws.com/prod/incidents/inc_8c2f606e
```

---

### **PUT /incidents/{incidentId}**
Actualizar un incidente existente.

**Request (actualizar cualquier campo):**
```json
{
  "status": "in_progress",
  "urgencia": "media",
  "assignedTo": "authority_user_123"
}
```

**Campos actualizables:**
- `status`: `open`, `in_progress`, `resolved`
- `urgencia`: `baja`, `media`, `alta`
- `assignedTo`: ID del usuario asignado
- `titulo`: Actualizar título
- `descripcion`: Actualizar descripción
- `ubicacion`: Actualizar ubicación

**Response (200 OK):**
```json
{
  "incidentId": "inc_8c2f606e",
  "status": "in_progress",
  "urgencia": "media",
  "assignedTo": "authority_user_123",
  "updatedAt": 1763285142
}
```

**Ejemplo curl:**
```bash
curl -X PUT https://wkcu4ednm9.execute-api.us-east-1.amazonaws.com/prod/incidents/inc_8c2f606e \
  -H "Content-Type: application/json" \
  -d '{
    "status": "resolved",
    "urgencia": "baja"
  }'
```

---

### **POST /incidents/{incidentId}/comments**
Agregar un comentario a un incidente.

**Request:**
```json
{
  "comment": "El incendio fue controlado, todo está seguro ahora",
  "userId": "user_123",
  "userName": "Juan Pérez"
}
```

**Campos:**
- `comment` (string, required): Texto del comentario (máx 1000 caracteres)
- `userId` (string, optional): ID del usuario que comenta (default: "anon")
- `userName` (string, optional): Nombre del usuario (default: "Anónimo")

**Response (201 Created):**
```json
{
  "commentId": "comment_01jd...",
  "incidentId": "inc_8c2f606e",
  "userId": "user_123",
  "userName": "Juan Pérez",
  "comment": "El incendio fue controlado, todo está seguro ahora",
  "createdAt": 1763285500
}
```

**Ejemplo curl:**
```bash
curl -X POST https://wkcu4ednm9.execute-api.us-east-1.amazonaws.com/prod/incidents/inc_8c2f606e/comments \
  -H "Content-Type: application/json" \
  -d '{
    "comment": "Situación controlada",
    "userId": "authority_01",
    "userName": "Oficial de Seguridad"
  }'
```

---

### **GET /incidents/{incidentId}/comments**
Obtener todos los comentarios de un incidente.

**Response (200 OK):**
```json
{
  "incidentId": "inc_8c2f606e",
  "comments": [
    {
      "commentId": "comment_01jd...",
      "userId": "authority_01",
      "userName": "Oficial de Seguridad",
      "comment": "Situación controlada",
      "createdAt": 1763285500
    },
    {
      "commentId": "comment_01jc...",
      "userId": "user_123",
      "userName": "Juan Pérez",
      "comment": "Gracias por la rápida respuesta",
      "createdAt": 1763285350
    }
  ],
  "count": 2
}
```

**Ejemplo curl:**
```bash
curl https://wkcu4ednm9.execute-api.us-east-1.amazonaws.com/prod/incidents/inc_8c2f606e/comments
```

---

### **DELETE /incidents/{incidentId}/comments/{commentId}**
Eliminar un comentario específico.

**Response (200 OK):**
```json
{
  "message": "Comentario eliminado exitosamente"
}
```

**Ejemplo curl:**
```bash
curl -X DELETE https://wkcu4ednm9.execute-api.us-east-1.amazonaws.com/prod/incidents/inc_8c2f606e/comments/comment_01jd...
```

---

## 🔌 **WebSocket Service (Real-time)**

**WebSocket URL:** `wss://b9ius2s0e1.execute-api.us-east-1.amazonaws.com/prod`

### **Conectar al WebSocket**

**Connection URL con query params:**
```
wss://b9ius2s0e1.execute-api.us-east-1.amazonaws.com/prod?sub=user123&role=student
```

**Query Parameters:**
- `sub` (optional): User ID del cliente conectado
- `role` (optional): Rol del usuario (`student`, `admin`, `authority`)

### **Eventos que recibes automáticamente:**

Cuando se crea o actualiza un incidente, todos los clientes conectados reciben:

**Evento: INCIDENT_CREATED**
```json
{
  "eventName": "INSERT",
  "incidentId": "inc_8c2f606e",
  "titulo": "Incendio en cafetería",
  "urgencia": "alta",
  "ubicacion": "Cafetería Central",
  "status": "open",
  "createdAt": 1763285042
}
```

**Evento: INCIDENT_UPDATED**
```json
{
  "eventName": "MODIFY",
  "incidentId": "inc_8c2f606e",
  "status": "in_progress",
  "urgencia": "media",
  "updatedAt": 1763285142
}
```

### **Ejemplo JavaScript:**
```javascript
const ws = new WebSocket('wss://b9ius2s0e1.execute-api.us-east-1.amazonaws.com/prod?sub=demo-user&role=student');

ws.onopen = () => {
  console.log('✅ Conectado al WebSocket');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('📡 Evento recibido:', data);
};

ws.onerror = (error) => {
  console.error('❌ Error:', error);
};

ws.onclose = () => {
  console.log('🔌 Desconectado');
};
```

### **Probar con wscat (CLI):**
```bash
# Instalar wscat
npm install -g wscat

# Conectar
wscat -c "wss://b9ius2s0e1.execute-api.us-east-1.amazonaws.com/prod?sub=test&role=student"
```

### **Demo Client HTML:**
Abre `services/realtime/demo-client.html` en tu navegador para una interfaz visual de prueba.

```bash
cd services/realtime
python3 -m http.server 8080
# Abre: http://localhost:8080/demo-client.html
```

---

## 🚀 **Deployment con SAM**

### **1. Auth Service**

```bash
cd services/auth

# Build
sam build --use-container --template template.yaml

# Deploy
sam deploy \
  --stack-name alerta-auth \
  --template-file .aws-sam/build/template.yaml \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides LabRoleArn=arn:aws:iam::527785891672:role/LabRole \
  --resolve-s3 \
  --region us-east-1

# Ver outputs (API URL, etc)
aws cloudformation describe-stacks \
  --stack-name alerta-auth \
  --region us-east-1 \
  --query "Stacks[0].Outputs" \
  --output table
```

---

### **2. Incidents Service**

```bash
cd services/incidents

# Build
sam build --use-container --template template.yaml

# Deploy
sam deploy \
  --stack-name alerta-incidents \
  --template-file .aws-sam/build/template.yaml \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides LabRoleArn=arn:aws:iam::527785891672:role/LabRole \
  --resolve-s3 \
  --region us-east-1

# Ver outputs (API URL, Stream ARN)
aws cloudformation describe-stacks \
  --stack-name alerta-incidents \
  --region us-east-1 \
  --query "Stacks[0].Outputs" \
  --output table
```

---

### **3. Realtime Service (WebSocket)**

```bash
cd services/realtime

# Build
sam build --use-container --template template-academy.yaml

# Obtener el Stream ARN de Incidents
STREAM_ARN=$(aws cloudformation describe-stacks \
  --stack-name alerta-incidents \
  --region us-east-1 \
  --query "Stacks[0].Outputs[?OutputKey=='IncidentsTableStreamArn'].OutputValue" \
  --output text)

# Deploy
sam deploy \
  --stack-name alerta-realtime \
  --template-file .aws-sam/build/template.yaml \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides \
    LabRoleArn=arn:aws:iam::527785891672:role/LabRole \
    IncidentsStreamArn=$STREAM_ARN \
  --resolve-s3 \
  --region us-east-1

# Ver outputs (WebSocket URL)
aws cloudformation describe-stacks \
  --stack-name alerta-realtime \
  --region us-east-1 \
  --query "Stacks[0].Outputs" \
  --output table
```

---

## 🧪 **Testing End-to-End**

### **Flujo completo de prueba:**

```bash
# 1. Registrar usuario
curl -X POST https://rgs5nn9vgf.execute-api.us-east-1.amazonaws.com/dev/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@utec.edu.pe","password":"test123","nombre":"Test User"}'

# 2. Conectar WebSocket (en el navegador con demo-client.html)
# URL: wss://b9ius2s0e1.execute-api.us-east-1.amazonaws.com/prod

# 3. Crear incidente (esto dispara evento en WebSocket)
curl -X POST https://wkcu4ednm9.execute-api.us-east-1.amazonaws.com/prod/incidents \
  -H "Content-Type: application/json" \
  -d '{
    "titulo": "Prueba tiempo real",
    "descripcion": "Testing WebSocket",
    "ubicacion": "Lab A",
    "urgencia": "alta"
  }'

# 4. Ver el evento aparecer automáticamente en demo-client.html ✨
```

---

## 📊 **Stack Outputs**

### **Obtener todos los endpoints:**

```bash
# Auth API
aws cloudformation describe-stacks \
  --stack-name alerta-auth \
  --region us-east-1 \
  --query "Stacks[0].Outputs[?OutputKey=='AuthApiUrl'].OutputValue" \
  --output text

# Incidents API
aws cloudformation describe-stacks \
  --stack-name alerta-incidents \
  --region us-east-1 \
  --query "Stacks[0].Outputs[?OutputKey=='IncidentsApiUrl'].OutputValue" \
  --output text

# WebSocket URL
aws cloudformation describe-stacks \
  --stack-name alerta-realtime \
  --region us-east-1 \
  --query "Stacks[0].Outputs[?OutputKey=='WebSocketWssEndpoint'].OutputValue" \
  --output text
```

---

## 🔥 **Eliminar todos los stacks**

```bash
# Eliminar en orden inverso (realtime depende de incidents)
aws cloudformation delete-stack --stack-name alerta-realtime --region us-east-1
aws cloudformation delete-stack --stack-name alerta-incidents --region us-east-1
aws cloudformation delete-stack --stack-name alerta-auth --region us-east-1

# Esperar a que se eliminen
aws cloudformation wait stack-delete-complete --stack-name alerta-realtime --region us-east-1
aws cloudformation wait stack-delete-complete --stack-name alerta-incidents --region us-east-1
aws cloudformation wait stack-delete-complete --stack-name alerta-auth --region us-east-1
```

---

## 📝 **Notas importantes**

- **JWT Tokens:** El auth service devuelve tokens JWT válidos por 1 hora
- **WebSocket:** La conexión se mantiene activa hasta que el cliente se desconecte
- **DynamoDB Streams:** Los eventos fluyen automáticamente desde Incidents → Broadcaster → WebSocket
- **SNS Notifications:** Los incidentes de urgencia `alta` también publican en un topic SNS
- **CORS:** Todas las APIs tienen CORS habilitado para desarrollo
- **Región:** Todo está desplegado en `us-east-1`

---

## 🎯 **Próximos pasos**

- [ ] Implementar autenticación JWT en endpoints de incidents
- [ ] Agregar paginación a GET /incidents
- [ ] Implementar filtros avanzados (por urgencia, fecha, ubicación)
- [ ] Agregar subida de imágenes a S3
- [ ] Dashboard de analytics con métricas de incidentes
- [ ] Frontend React/Next.js
