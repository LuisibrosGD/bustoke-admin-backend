# Prompt Maestro 3: Configuración del Pipeline CI/CD (Unidad III)

## Archivo de configuración: `.github/workflows/test-automation.yml`

```yaml
name: Test Automation Pipeline

on:
  push:
    branches: [main, master]
  pull_request:
    branches: [main, master]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python 3.11
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-asyncio httpx

      - name: Configure environment variables
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
          SECRET_KEY: ${{ secrets.SECRET_KEY }}
          ALGORITHM: HS256
          ACCESS_TOKEN_EXPIRE_MINUTES: 60
          REFRESH_TOKEN_EXPIRE_DAYS: 7
          CORS_ORIGINS: http://localhost:3000
          PORT: 5000
        run: |
          echo "DATABASE_URL=$DATABASE_URL" >> $GITHUB_ENV
          echo "SECRET_KEY=$SECRET_KEY" >> $GITHUB_ENV
          echo "ALGORITHM=$ALGORITHM" >> $GITHUB_ENV
          echo "ACCESS_TOKEN_EXPIRE_MINUTES=$ACCESS_TOKEN_EXPIRE_MINUTES" >> $GITHUB_ENV
          echo "REFRESH_TOKEN_EXPIRE_DAYS=$REFRESH_TOKEN_EXPIRE_DAYS" >> $GITHUB_ENV
          echo "CORS_ORIGINS=$CORS_ORIGINS" >> $GITHUB_ENV
          echo "PORT=$PORT" >> $GITHUB_ENV

      - name: Run database migrations
        run: alembic upgrade head
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}

      - name: Start application in background
        run: |
          uvicorn app.main:app --host 0.0.0.0 --port 5000 &
          sleep 5

      - name: Run test suite
        run: |
          pytest tests/ -v --tb=short --junitxml=test-results.xml
        continue-on-error: true

      - name: Generate test report
        if: always()
        run: |
          python -m pytest tests/ -v --html=report.html --self-contained-html
        continue-on-error: true

      - name: Upload test results
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: test-results
          path: |
            test-results.xml
            report.html
          retention-days: 30

      - name: Upload coverage report
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: coverage-report
          path: coverage/
          retention-days: 30
```

## Explicación del Pipeline

### 1. Levantar el entorno necesario
- **Python 3.11**: Se configura la versión específica de Python requerida por el proyecto
- **Neon PostgreSQL 18**: Se conecta directamente a la base de datos en Neon usando `secrets.DATABASE_URL`
- **Dependencias**: Se instalan las dependencias de requirements.txt y herramientas de prueba

> **Nota**: Debes configurar los secrets en GitHub: Settings → Secrets and variables → Actions → New repository secret
> - `DATABASE_URL`: `postgresql+asyncpg://usuario:password@ep-xxxx.us-east-x.aws.neon.tech/neondb`
> - `SECRET_KEY`: Tu clave secreta para JWT

### 2. Levantar la aplicación en background
- **Uvicorn**: Se ejecuta la aplicación FastAPI en segundo plano
- **Espera**: Se añade una pausa de 5 segundos para asegurar que la aplicación esté lista

### 3. Ejecutar la suite de pruebas
- **Pytest**: Se ejecutan las pruebas con pytest generando reportes XML y HTML
- **Continuar si falla**: Se usa `continue-on-error: true` para que el pipeline continúe incluso si hay fallos

### 4. Exportar reportes como artefactos
- **Test Results**: Se suben los reportes de resultados (XML y HTML)
- **Coverage Report**: Se sube el reporte de cobertura de código
- **Retención**: Los artefactos se mantienen por 30 días

---

# Prompt Maestro 4: Análisis Inicial de Seguridad (Unidad IV)

## Reporte de Análisis de Seguridad - OWASP Top 10

### 1. Riesgos Potenciales Identificados

#### A. Inyección SQL (OWASP A03:2021)
**Ubicación**: `app/modules/reportes/service.py:64-151`

**Descripción del Riesgo**: 
Se están construyendo consultas SQL de forma dinámica usando f-strings con parámetros nombrados. Aunque se utilizan parámetros para los valores, la estructura de la consulta se modifica dinámicamente, lo que podría permitir inyección SQL si los parámetros no se sanitizan adecuadamente.

**Código vulnerable**:
```python
sql = text(f"""
    SELECT ... 
    FROM boletos b
    JOIN viajes v ON b.id_viaje = v.id_viaje
    ...
    WHERE {where_clause}
""")
```

**Explicación**: 
El parámetro `where_clause` se construye dinámicamente a partir de filtros que incluyen valores del usuario. Si bien se usan parámetros nombrados (`:param`), la construcción de la consulta podría ser manipulada si los filtros no se validan correctamente.

#### B. Broken Authentication (OWASP A07:2021)
**Ubicación**: `app/core/security.py` y `app/dependencies.py`

**Descripción del Riesgo**: 
1. **Falta de validación de alcance del token**: Los tokens JWT no validan el alcance (scope) o audiencia (audience)
2. **Tokens de refresco sin invalidación**: No hay mecanismo para invalidar tokens de refresco
3. **Falta de rate limiting**: No hay límite de intentos de autenticación

**Código vulnerable**:
```python
def decode_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError as e:
        raise ValueError(f"Token inválido: {e}")
```

**Explicación**: 
La función `decode_token` no valida claimers como `aud` (audiencia) o `iss` (emisor), lo que podría permitir que tokens generados para otros fines sean aceptados.

#### C. Exposición de Datos Sensibles (OWASP A02:2021)
**Ubicación**: `app/core/security.py:18-24`

**Descripción del Riesgo**: 
Se están registrando mensajes de error que contienen información sensible sobre hashes de contraseñas en los logs.

**Código vulnerable**:
```python
def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        if not hashed_password or len(hashed_password) < 50:
            print(f"[ERROR] Hash inválido - longitud: {len(hashed_password)}")
            return False
        if not hashed_password.startswith(("$2a$", "$2b$", "$2y$")):
            print(f"[ERROR] Hash no es bcrypt válido: {hashed_password[:20]}")
            return False
```

**Explicación**: 
Los primeros 20 caracteres del hash se registran en los logs, lo que podría facilitar ataques de fuerza bruta si los logs son comprometidos.

### 2. Recomendaciones de Corrección

#### A. Para Inyección SQL
```python
# En lugar de construir WHERE dinámicamente, usar parámetros seguros
async def get_reportes_seguro(db: AsyncSession, filtros: dict):
    query = select(Boleto).join(Viaje).join(Ruta)
    
    if 'fecha_inicio' in filtros:
        query = query.where(Viaje.fecha_hora_salida >= filtros['fecha_inicio'])
    if 'fecha_fin' in filtros:
        query = query.where(Viaje.fecha_hora_salida <= filtros['fecha_fin'])
    
    result = await db.execute(query)
    return result.scalars().all()
```

#### B. Para Broken Authentication
```python
# En security.py - Agregar validaciones adicionales
def decode_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM],
            audience="bustoke-admin",  # Validar audiencia
            issuer="bustoke-api"       # Validar emisor
        )
        return payload
    except JWTError as e:
        raise ValueError(f"Token inválido: {e}")

# En dependencies.py - Agregar rate limiting
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/login")
@limiter.limit("5/minute")  # Máximo 5 intentos por minuto
async def login(request: Request, credentials: LoginSchema):
    # ... lógica de login
```

#### C. Para Exposición de Datos Sensibles
```python
# En security.py - Eliminar logs sensibles
def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        if not hashed_password or len(hashed_password) < 50:
            # No registrar información sobre el hash
            return False
        if not hashed_password.startswith(("$2a$", "$2b$", "$2y$")):
            # No registrar fragmentos del hash
            return False
        
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except (ValueError, TypeError):
        # Registrar error genérico sin información sensible
        return False
```

### 3. Configuración Recomendada

#### Variables de Entorno para Seguridad
```bash
# .env - Configuración de seguridad mejorada
SECRET_KEY=tu-clave-secreta-super-segura-aqui-cambiar-en-produccion
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30  # Reducir tiempo de expiración
REFRESH_TOKEN_EXPIRE_DAYS=1     # Reducir tiempo de refresh

# Rate limiting
RATE_LIMIT_LOGIN=5/minute
RATE_LIMIT_API=100/minute

# CORS más restrictivo
CORS_ORIGINS=https://admin.bustoke.pe
```

#### Configuración de Headers de Seguridad
```python
# En main.py - Agregar headers de seguridad
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["admin.bustoke.pe", "*.bustoke.pe"]
)

# Headers de seguridad adicionales
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response
```

### 4. Próximos Pasos Recomendados

1. **Implementar rate limiting** en todos los endpoints de autenticación
2. **Agregar validación de audiencia y emisor** en tokens JWT
3. **Revisar y sanitizar** todas las construcciones de queries dinámicas
4. **Implementar logging seguro** que no exponga información sensible
5. **Configurar CORS más restrictivo** para producción
6. **Agregar headers de seguridad** HTTP
7. **Implementar escaneo de dependencias** con herramientas como Safety o Snyk
8. **Realizar auditoría de código** enfocada en seguridad

### 5. Herramientas Recomendadas

- **SAST**: Bandit para análisis estático de código Python
- **DAS**: Safety para escaneo de dependencias
- **DAST**: OWASP ZAP para pruebas de seguridad dinámicas
- **Secret Scanning**: GitLeaks para detectar secretos en el repositorio
- **Rate Limiting**: slowapi o fastapi-limiter