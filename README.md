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
