# AlertaUTEC – Plan de Trabajo

## 1. Contexto y objetivo
Diseñar una plataforma 100% serverless para reportar, monitorear y gestionar incidentes dentro del campus UTEC, asegurando comunicación en tiempo real entre estudiantes, personal administrativo y autoridades. El alcance incluye autenticación, reportería, panel de control, orquestación de flujos con Airflow y analítica opcional con SageMaker.

## 2. Metas específicas
- **Autenticación y roles:** registro/login con credenciales institucionales y control de roles (estudiante, administrativo, autoridad) mediante un microservicio serverless (API Gateway + Lambda + DynamoDB) que emite JWT firmados con una clave almacenada en Secrets Manager/KMS, evitando el uso de Amazon Cognito.
- **Gestión de incidentes:** API REST/WebSocket en AWS API Gateway + AWS Lambda que persiste incidentes en Amazon DynamoDB con IDs únicos.
- **Tiempo real y notificaciones:** WebSockets para actualizar estados (pendiente, en atención, resuelto) y SNS/SES/SMS para alertas asincrónicas.
- **Panel administrativo:** frontend en AWS Amplify Hosting que consume APIs y streams para monitorear y cerrar incidentes.
- **Orquestación con Airflow:** DAGs para clasificación automática, envíos a responsables y reportes recurrentes.
- **Historial y trazabilidad:** logging en DynamoDB Streams + AWS Lambda + Amazon S3/CloudWatch Logs.
- **Escalabilidad y resiliencia:** infraestructura serverless con IaC (AWS SAM o CDK).
- **Analítica opcional:** pipelines hacia AWS SageMaker para modelos predictivos y visualizaciones en QuickSight.

## 3. Arquitectura de alto nivel
```
Usuarios → AWS Amplify (UI)
        ↓ auth
      API Gateway (Auth REST) → Lambda Auth Service → DynamoDB (Users/Roles)
        ↓ JWT válidos
      API Gateway (REST + WebSocket)
        ↓ Lambda (Incidents, Notifications)
        ↳ DynamoDB (IncidentsTable)
        ↳ DynamoDB Streams → Lambda → S3 (historial)
        ↳ Amazon SNS/SES/SMS (alertas)
            ↓
         Apache Airflow (MWAA) → tareas de clasificación, reportes
            ↓
         Amazon SageMaker + QuickSight (analítica opcional)
```

## 4. Componentes clave
1. **Frontend (Amplify + React/Next):** formularios de incidentes, panel en vivo, dashboards.
2. **Auth custom (API Gateway + Lambda + DynamoDB):** registro/login con hashing de contraseñas (bcrypt/argon2), emisión de JWT firmados y almacenamiento de roles, con opción de federar a un IdP institucional mediante SAML/OIDC cuando esté disponible.
3. **APIs (API Gateway + Lambda):** endpoints REST (CRUD incidentes, usuarios) y WebSocket para eventos.
4. **Persistencia (DynamoDB + S3):** tabla `Incidents` y bucket para adjuntos/evidencia.
5. **Mensajería (SNS/SES/SMS, EventBridge):** disparo de notificaciones por estado.
6. **Orquestación (Airflow/MWAA):** DAGs para clasificación, reportes, entrenamiento de modelos.
7. **Observabilidad (CloudWatch, X-Ray, CloudTrail):** métricas, logs y auditoría.
8. **Analítica (SageMaker, QuickSight):** pipelines y dashboards predictivos.

## 5. Roadmap exprés (24 horas)
| Bloque | Horario sugerido | Objetivo | Resultado mínimo |
|--------|------------------|----------|------------------|
| **Kickoff & Setup** | 0h – 2h | Alinear requerimientos, definir alcance MVP, crear repositorios y tableros. | Backlog priorizado, repositorio con plantillas y IaC base. |
| **Auth + Modelo de datos** | 2h – 6h | Implementar servicio de autenticación custom (registro/login, roles) y esquema de DynamoDB. | Lambda Auth con hashing + emisión de JWT, tabla `Incidents`. |
| **CRUD + UI inicial** | 6h – 12h | Construir endpoints REST para incidentes y formularios básicos en Amplify. | `POST/GET/PATCH /incidents`, formulario funcional que guarda en DynamoDB. |
| **Tiempo real & Notificaciones** | 12h – 16h | Canal WebSocket + triggers de notificación y bitácora en S3. | Lambda WebSocket enviando eventos `incidentCreated/statusChanged`, integración con SNS/SES. |
| **Panel administrativo** | 16h – 20h | Vista con filtros, acciones de asignar/cerrar y métricas rápidas. | Panel React consumiendo WebSocket/REST, métricas básicas (contadores, SLA). |
| **Airflow + Demo** | 20h – 24h | Crear DAG mínimo (clasificación/notificación), script de demo y material de presentación. | DAG en MWAA o Airflow local, video corto/demo script, checklist de pruebas. |

## 6. Paso a paso detallado
1. **Kickoff & Research**
   - Definir KPIs (tiempo de respuesta, número de incidentes resueltos, etc.).
   - Identificar fuentes de credenciales institucionales para federación futura y, mientras tanto, establecer un directorio temporal en DynamoDB.
2. **Arquitectura & Infraestructura Base**
   - Diseñar IaC (SAM/CDK/Terraform) para Amplify, API Gateway (REST/WebSocket/Auth), Lambda, DynamoDB, SNS y buckets.
   - Configurar repositorio Git, ramas por squads y pipelines CI/CD (GitHub Actions + Amplify).
3. **Servicio de autenticación y roles**
   - Crear tabla `Users` con hash de contraseña + rol, y Lambda Auth (`/auth/register`, `/auth/login`).
   - Firmar JWT con clave almacenada en Secrets Manager/KMS y validar en API Gateway mediante Lambda Authorizer.
   - Implementar flujos de registro/login en frontend, guardias de ruta y refresco de tokens.
4. **API de Incident Management**
   - Diseñar modelo `Incident` (id, reporterId, tipo, ubicación, urgencia, attachments, estado, timestamps, assignedTo, history[]).
   - Implementar Lambdas para `POST /incidents`, `GET /incidents`, `PATCH /incidents/{id}` y `POST /attachments` (S3 pre-signed).
5. **Tiempo Real & Notificaciones**
   - Configurar API Gateway WebSocket + Lambda para eventos `incidentCreated`, `statusChanged`.
   - Integrar DynamoDB Streams → Lambda → SNS/SES/SMS para alertas y bitácora en S3.
6. **Panel Administrativo**
   - Construir UI con filtros, mapa/heatmap, acciones de asignar/cerrar.
   - Añadir métricas en vivo (incidentes por estado, SLA, ranking de zonas).
7. **Airflow DAGs**
   - Aprovisionar MWAA (o Airflow Docker en EC2/local si el ambiente de Academy lo requiere), crear DAG `classify_incidents` (usa modelo simple inicial).
   - DAG `notify_owners` (consulta incidentes críticos y dispara SNS/email).
   - DAG `weekly_reports` (agrupa estadísticas, envía a S3 + QuickSight dataset).
8. **Analítica Predictiva (Opcional)**
   - Exportar dataset histórico (DynamoDB → S3 via Glue/Athena).
   - Entrenar prototipo en SageMaker (XGBoost/AutoPilot) para predecir urgencia/probabilidad.
   - Conectar resultados a panel (mostrar zonas críticas y predicciones).
9. **Cierre y Demo**
   - Preparar script de demo (flujo de estudiante, operador, autoridad).
   - Recolectar métricas, capturas y video corto demostrativo.

## 7. Roles sugeridos en el equipo
- **Cloud Lead:** diseña IaC, despliegues y seguridad.
- **Backend/Realtime Lead:** APIs, WebSockets, DynamoDB.
- **Frontend Lead:** UX/UI en Amplify + React, panel en tiempo real.
- **Data/ML Lead:** Airflow, pipelines de datos y modelos en SageMaker.

## 8. Gestión de riesgos
| Riesgo | Mitigación |
|--------|------------|
| Integración con credenciales institucionales tarda | Mantener servicio Auth propio con usuarios mock y documentar la futura federación vía SAML/OIDC |
| Complejidad de Airflow | Comenzar con DAGs simples (lambdas invocadas) y escalar a MWAA si hay tiempo |
| WebSockets inestables | Fallback a polling + SNS hasta estabilizar infraestructura |
| Falta de datos para ML | Generar dataset sintético y documentar plan de entrenamiento real |

## 9. Métricas de éxito
- Tiempo promedio de respuesta por incidente.
- % de incidentes resueltos < SLA.
- Número de usuarios activos diarios.
- Latencia promedio de notificación (< 5 s interna, < 2 min externa).
- Cobertura de reportes (incidentes creados vs atendidos).

## 10. Entregables para la hackathon
1. Repositorio con frontend, backend (IaC) y DAGs.
2. README con instrucciones de despliegue y demo.
3. Video/slide deck mostrando flujo real.
4. Backlog priorizado y métricas iniciales.
5. (Opcional) Notebook de SageMaker + dashboard QuickSight.

## 11. Próximos pasos inmediatos
1. Confirmar integrantes y asignar roles.
2. Configurar repositorio y pipeline CI/CD.
3. Prototipo de auth + formulario de incidentes.
4. Integrar WebSocket + panel básico.
5. Orquestar DAG inicial y preparar demo.

## 12. Implementación actual del servicio de autenticación
- Código fuente en `services/auth/src/auth_service` con módulos separados (dominio, repositorios, utilidades y handlers Lambda).
- DynamoDB actúa como directorio de usuarios (`UsersTable`), con hash de contraseña `bcrypt` y emisión de JWT HS256 firmados con una clave almacenada en Secrets Manager o variable `JWT_SECRET_VALUE` para entornos locales.
- Endpoints disponibles en la Lambda HTTP:
   - `POST /auth/register`: valida emails `@utec.edu.pe`, persiste el usuario y retorna perfil.
   - `POST /auth/login`: verifica credenciales, emite tokens (`access`, `refresh`) e incluye campos de rol/estado.
- Authorizer Lambda (`authorizer_handler`) valida tokens en API Gateway y añade claims (`sub`, `role`) al contexto.

### Ejecutar pruebas unitarias
```powershell
cd services/auth
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
pip install -r tests\requirements-test.txt
.\.venv\Scripts\pytest
```

> Las pruebas (`tests/test_auth_service.py`) validan registro/login, hash seguro y firma de JWT sin depender de AWS gracias a un repositorio en memoria y fixtures que mockean secretos.

## 13. Sistema de Tiempo Real (WebSocket + Notificaciones) ✅ DESPLEGADO

### Arquitectura desplegada
```
Usuario crea incidente (DynamoDB)
        ↓
DynamoDB Streams detecta cambio
        ↓
    ┌───────────────────────┐
    ↓                       ↓
Broadcaster Lambda    Notifier Lambda
    ↓                       ↓
WebSocket API          SNS Topic
    ↓                       ↓
Clientes conectados   Email/SMS a autoridades
(Panel + App móvil)
```

### Componentes desplegados (Stack: `alerta-realtime`)

1. **WebSocket API Gateway**
   - Rutas: `$connect`, `$disconnect`
   - Gestión de conexiones en DynamoDB (`ConnectionsTable`)
   - Endpoints autenticados vía query params (`?sub=user&role=student`)

2. **DynamoDB Tables**
   - `AlertaUTEC-Incidents`: tabla principal con DynamoDB Streams habilitado
   - `alerta-realtime-Connections`: tracking de conexiones WebSocket activas

3. **Lambda Functions**
   - `ConnectFunction`: persiste conexiones WebSocket con contexto de usuario
   - `DisconnectFunction`: limpia conexiones cerradas
   - `BroadcasterFunction`: lee Streams y envía eventos a todos los clientes conectados
   - `NotifierFunction`: publica alertas a SNS cuando urgencia es alta/crítica

4. **SNS Topic** (`IncidentAlerts`)
   - Envía notificaciones automáticas por email/SMS
   - Se dispara cuando `urgencia in ["alta", "crítica"]` o `status in ["in_progress", "escalated"]`

### Cliente de Demostración
- Ubicación: `services/realtime/demo-client.html`
- Características:
  - Conexión WebSocket con visualización de estado
  - Display de eventos en tiempo real (`IncidentCreated`, `IncidentStatusChanged`)
  - Log interactivo con timestamps y formato JSON
  - Soporte para múltiples conexiones simultáneas

### Eventos soportados
```json
// IncidentCreated
{
  "type": "IncidentCreated",
  "id": "inc-001",
  "status": "pending",
  "urgencia": "alta",
  "ubicacion": "Lab B201",
  "titulo": "Fuga de gas detectada"
}

// IncidentStatusChanged
{
  "type": "IncidentStatusChanged",
  "id": "inc-001",
  "status": "in_progress",
  "urgencia": "alta"
}
```

### Despliegue (AWS Academy)
```bash
cd services/realtime
sam build --template template-academy.yaml --use-container
sam deploy \
  --template-file .aws-sam/build/template.yaml \
  --stack-name alerta-realtime \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides \
    LabRoleArn=arn:aws:iam::527785891672:role/LabRole \
    IncidentsStreamArn="<STREAM_ARN>" \
  --resolve-s3 \
  --region us-east-1
```

### Prueba rápida
```bash
# 1. Obtener WebSocket URL
aws cloudformation describe-stacks \
  --stack-name alerta-realtime \
  --query 'Stacks[0].Outputs[?OutputKey==`WebSocketWssEndpoint`].OutputValue' \
  --output text

# 2. Abrir cliente demo
cd services/realtime
python3 -m http.server 8080
# Navegar a http://<EC2_IP>:8080/demo-client.html

# 3. Insertar incidente de prueba
aws dynamodb put-item --table-name AlertaUTEC-Incidents --item '{
  "id": {"S": "test-001"},
  "status": {"S": "pending"},
  "urgencia": {"S": "alta"},
  "ubicacion": {"S": "Biblioteca Central"},
  "titulo": {"S": "Incidente de prueba"}
}'

# 4. Observar evento en tiempo real en el cliente
```

### Suscribir notificaciones SNS
```bash
# Obtener ARN del topic
TOPIC_ARN=$(aws cloudformation describe-stacks \
  --stack-name alerta-realtime \
  --query 'Stacks[0].Outputs[?OutputKey==`IncidentAlertsTopicArn`].OutputValue' \
  --output text)

# Suscribir email
aws sns subscribe \
  --topic-arn $TOPIC_ARN \
  --protocol email \
  --notification-endpoint tu-email@utec.edu.pe

# Confirmar desde tu correo
```

### Documentación técnica completa
- Workflow detallado: `docs/realtime-workflow.md`
- Diagramas de secuencia (Mermaid) para crear/actualizar incidentes
- Snippets de código Python para cada Lambda
- Contrato de eventos y esquema DynamoDB

### Estado del proyecto
- ✅ WebSocket API desplegado y funcional
- ✅ DynamoDB Streams conectado a Lambdas
- ✅ Broadcaster enviando eventos en tiempo real
- ✅ SNS notificando a autoridades por email/SMS
- ✅ Cliente HTML demo funcionando
- ✅ Backend de incidentes (CRUD REST API)
- 🔄 Pendiente: frontend React/Next con autenticación JWT

## 14. Backend de Gestión de Incidentes ✅ IMPLEMENTADO

API REST completa para crear, actualizar y consultar incidentes del campus.

### Endpoints disponibles

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| POST | `/incidents` | Crear nuevo incidente | JWT requerido |
| PATCH | `/incidents/{id}` | Actualizar estado/urgencia | JWT requerido |
| GET | `/incidents` | Listar incidentes (filtrable) | JWT requerido |

### Estructura del servicio
- **Código**: `services/incidents/src/handlers.py`
- **Authorizer**: `services/incidents/src/authorizer.py` (valida JWT)
- **Tests**: `services/incidents/tests/test_handlers.py`
- **Template SAM**: `services/incidents/template.yaml`

### Características implementadas
- ✅ Validación JWT con Lambda Authorizer
- ✅ Validaciones de entrada (titulo y ubicacion requeridos)
- ✅ Extracción automática de reporterId y email del JWT
- ✅ Manejo robusto de errores con códigos HTTP apropiados
- ✅ Headers CORS para integración con frontend
- ✅ Ordenamiento de incidentes por fecha de creación
- ✅ Filtrado por status en GET /incidents
- ✅ Campo `updatedAt` automático en actualizaciones
- ✅ Suite de tests unitarios (pytest)

### Modelo de datos (incidente)
```json
{
  "id": "uuid",
  "titulo": "string (requerido)",
  "ubicacion": "string (requerido)",
  "urgencia": "baja|media|alta|crítica",
  "status": "pending|in_progress|resolved",
  "descripcion": "string (opcional)",
  "reporterId": "string (del JWT)",
  "reporterEmail": "string (del JWT)",
  "assignedTo": "string (opcional)",
  "createdAt": "timestamp",
  "updatedAt": "timestamp"
}
```

### Despliegue
```bash
cd services/incidents
sam build --use-container
sam deploy \
  --template-file .aws-sam/build/template.yaml \
  --stack-name alerta-incidents \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides \
    LabRoleArn=arn:aws:iam::527785891672:role/LabRole \
    IncidentsTableName=AlertaUTEC-Incidents \
  --resolve-s3 \
  --region us-east-1
```

### Ejemplo de uso
```bash
# 1. Obtener JWT (del servicio de auth)
TOKEN=$(curl -X POST $API_AUTH/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@utec.edu.pe","password":"pass123"}' \
  | jq -r '.accessToken')

# 2. Crear incidente
curl -X POST $API_INCIDENTS/incidents \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "titulo": "Fuga de gas",
    "ubicacion": "Lab B201",
    "urgencia": "alta",
    "descripcion": "Requiere atención inmediata"
  }'

# 3. Listar incidentes pendientes
curl -X GET "$API_INCIDENTS/incidents?status=pending" \
  -H "Authorization: Bearer $TOKEN"

# 4. Actualizar estado
curl -X PATCH $API_INCIDENTS/incidents/{id} \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "in_progress", "assignedTo": "admin@utec.edu.pe"}'
```

### Integración con tiempo real
Una vez desplegado, cada operación CREATE/UPDATE en DynamoDB dispara automáticamente:
1. **Lambda Broadcaster** → envía evento WebSocket a clientes conectados
2. **Lambda Notifier** → publica a SNS si urgencia es alta/crítica

Ver documentación completa en `services/incidents/README.md`
