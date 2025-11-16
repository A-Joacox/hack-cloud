# Servicio de Autenticación y Modelo de Datos

## 1. Endpoints mínimos (API Gateway HTTP)
| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| POST | /auth/register | Crea un usuario institucional (estudiante, administrativo, autoridad). | Público (token institucional opcional) |
| POST | /auth/login | Valida credenciales, emite JWT y refresh token firmado. | Público |
| POST | /auth/refresh | Intercambia refresh token por nuevo access token. | Público (requiere refresh token válido) |
| GET | /auth/me | Devuelve perfil usando JWT (claims + datos en DynamoDB). | Protegido |

### Reglas clave
- Hash de contraseña con `bcrypt` (cost configurable) y sal aleatoria.
- JWT firmado con HS256 usando `JWT_SIGNING_KEY` almacenado en Secrets Manager/KMS.
- Expiraciones: access token 15 min, refresh token 12 h.
- Roles posibles: `student`, `staff`, `authority`. Claim `role` se usa para Guardias en frontend/API.

## 2. Tablas DynamoDB

### Tabla `Users`
| Atributo | Tipo | Descripción |
|----------|------|-------------|
| `pk` | String | `USER#{email}` (Partition key) |
| `sk` | String | Constante `PROFILE` |
| `email` | String | Email institucional (único) |
| `fullName` | String | Nombre completo |
| `role` | String | `student|staff|authority` |
| `passwordHash` | String | Hash bcrypt (salt embebido) |
| `status` | String | `active|disabled` |
| `createdAt` | String (ISO) | Timestamp creación |
| `updatedAt` | String (ISO) | Timestamp última actualización |
| `lastLoginAt` | String (ISO) | Último login (opcional) |

_Índice secundario opcional:_ `role-index` (PK: `role`, SK: `email`) para panel administrativo.

### Tabla `Incidents`
| Atributo | Tipo | Descripción |
|----------|------|-------------|
| `pk` | String | `INCIDENT#{incidentId}` (Partition key) |
| `sk` | String | Constante `METADATA` |
| `incidentId` | String (ULID) |
| `reporterId` | String | email/id del reportante |
| `type` | String | categoría (infraestructura, seguridad, etc.) |
| `location` | Map | `{campusZone, geo:{lat,lng}}` |
| `urgency` | String | `low|medium|high|critical` |
| `status` | String | `pending|in_progress|resolved` |
| `assignedTo` | String | responsable actual |
| `description` | String | detalle del incidente |
| `attachments` | List | URLs S3 |
| `history` | List | eventos `{timestamp, action, actor, notes}` |
| `createdAt` | String | timestamp creación |
| `updatedAt` | String | timestamp último cambio |

_Índices sugeridos:_
- `status-updatedAt-index` (PK: `status`, SK: `updatedAt`) para panel en tiempo real.
- `reporter-index` (PK: `reporterId`, SK: `createdAt`) para historial del usuario.

## 3. Dependencias y configuraciones
- **Librerías:** `boto3`, `botocore`, `bcrypt`, `pyjwt`, `pydantic` (validaciones), `python-ulid` (IDs), `aws-lambda-powertools` (logging).
- **Variables de entorno:**
  - `USERS_TABLE_NAME`
  - `INCIDENTS_TABLE_NAME`
  - `JWT_SIGNING_SECRET_ARN` (ARN Secrets Manager)
  - `ACCESS_TOKEN_TTL` (segundos)
  - `REFRESH_TOKEN_TTL`
- **Seguridad:** Lambda Authorizer que valida JWT y adjunta claims a `event.requestContext.authorizer`.
- **Flujo de registro:** puede requerir código de verificación enviado por correo (SES) o validación manual por autoridad.

## 4. Secuencia típica
1. Usuario se registra → Lambda valida dominio `@utec.edu.pe`, guarda hash + rol.
2. Login → compara hash, emite JWT + refresh, actualiza `lastLoginAt`.
3. Frontend usa JWT para llamar `POST /incidents` (Lambda Authorizer valida rol y permisos).
4. Cambios en incidentes se persisten y stream se usa para notificaciones y Airflow.

## 5. Próximos pasos
- Implementar módulo de hashing/JWT reutilizable.
- Crear repositorio DynamoDB con interfaz para facilitar pruebas unitarias y reemplazos (por ejemplo, en memoria).
- Estandarizar payloads de eventos (Pydantic models) para minimizar errores en Lambdas.
