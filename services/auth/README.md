# Servicio de Autenticación (AWS Lambda)

## Funcionalidad
- Registro de usuarios institucionales (`POST /auth/register`).
- Inicio de sesión (`POST /auth/login`).
- Emisión de JWT (access + refresh) con roles incluidos.
- Utiliza DynamoDB como directorio de usuarios y Secrets Manager/KMS para la clave de firmado.

## Estructura
```
services/auth
├─ requirements.txt
├─ src/auth_service/
│  ├─ __init__.py
│  ├─ app.py              # Handler principal (register/login)
│  ├─ config.py           # Variables de entorno y constantes
│  ├─ domain/
│  │  ├─ models.py        # Modelos de dominio (User)
│  │  ├─ schemas.py       # Pydantic para requests/responses
│  │  └─ auth_service.py  # Lógica de registro/login
│  ├─ repositories/
│  │  ├─ base.py          # Interface de repositorio
│  │  └─ dynamo.py        # Implementación DynamoDB
│  └─ utils/
│     ├─ jwt_utils.py     # Firma y validación de tokens
│     └─ password_utils.py# Hash/validación de contraseñas
└─ tests/
   └─ test_auth_service.py
```

## Variables de entorno clave
- `USERS_TABLE_NAME`
- `JWT_SECRET_VALUE` (usado solo para pruebas locales; en producción se obtiene de Secrets Manager)
- `ACCESS_TOKEN_TTL` (segundos, default 900)
- `REFRESH_TOKEN_TTL` (segundos, default 43200)

## Ejecutar pruebas unitarias
```powershell
cd services/auth
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
pip install -r tests\requirements-test.txt
pytest
```

Para despliegue en Lambda vía SAM/CDK, empaqueta `services/auth/src` como artefacto e inyecta las variables de entorno necesarias.
