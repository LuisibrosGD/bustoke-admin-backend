# Bustoke Admin Backend

Backend de administración para **Bustoke** — plataforma de venta de pasajes interprovinciales. Construido con **FastAPI + SQLAlchemy 2.x async**.

## Stack tecnológico

| Capa | Tecnología |
|------|-----------|
| Framework | FastAPI 0.111 |
| ORM | SQLAlchemy 2.x async (asyncpg) |
| Validación | Pydantic v2 |
| Autenticación | JWT (python-jose) + bcrypt (passlib) |
| BD | PostgreSQL 15+ |
| Migraciones | Alembic |
| Excel | openpyxl |
| Servidor | Uvicorn (puerto 5000) |

## Estructura del proyecto

```
bustoke-admin-backend/
├── .env                        # Variables de entorno
├── .env.example
├── requirements.txt
├── alembic.ini
├── Dockerfile
├── fix-pass.py                 # Script para hashear contraseñas
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/               # Migraciones generadas
└── app/
    ├── main.py                 # Punto de entrada FastAPI
    ├── config.py               # Settings con pydantic-settings
    ├── database.py             # Engine async + Base ORM
    ├── dependencies.py         # Dependencias: auth, roles, API Key
    ├── core/
    │   ├── security.py         # JWT create/decode, bcrypt hash/verify
    │   └── exceptions.py       # Excepciones HTTP personalizadas
    └── modules/
        ├── auth/               # Login, refresh, forgot/reset password + usuarios
        ├── agencias/           # CRUD agencias
        ├── agencias_terminales/# Pivot agencia-terminal
        ├── flota/              # CRUD buses + asientos
        ├── rutas/              # CRUD rutas + tarifas_ruta
        ├── viajes/             # CRUD viajes + boletos + pasajeros
        ├── terminales/         # CRUD terminales
        ├── choferes/           # CRUD choferes
        ├── boletos/            # CRUD boletos (global)
        ├── pasajeros/          # CRUD pasajeros (global)
        ├── suscripciones/      # CRUD planes + suscripciones
        ├── soporte/            # CRUD tickets de soporte + historial
        ├── reclamos/           # CRUD reclamos + mensajes
        ├── finanzas/           # CRUD liquidaciones + api_keys
        ├── reportes/           # Reportes SQL + exportación Excel
        ├── manifiestos/        # Manifiestos SUTRAN
        ├── ubigeo/             # Departamentos, provincias, distritos
        ├── dashboard/          # Resumen de dashboard
        ├── notificaciones/     # Notificaciones push/leídas
        └── public/             # Endpoints públicos con API Key auth
```

## Instalación

### 1. Crear entorno virtual

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

```bash
copy .env.example .env
```

Variables principales:

```env
DATABASE_URL=postgresql+asyncpg://postgres:mondongo@localhost:5432/bustoke_db
SECRET_KEY=supersecretkey-bustoke-admin-2024-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7
CORS_ORIGINS=http://localhost:3000
PORT=5000
```

### 4. Ejecutar servidor

```bash
uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload
```

### 5. Docker

```bash
docker build -t bustoke-admin-backend .
docker run -p 5000:5000 --env-file .env bustoke-admin-backend
```

## Endpoints

### Auth (`/admin/auth`)

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| POST | `/admin/auth/login` | Autenticación (email + password) | — |
| POST | `/admin/auth/refresh` | Renovar access token vía refresh token | — |
| POST | `/admin/auth/logout` | Cerrar sesión (stateless) | Bearer |
| POST | `/admin/auth/logout-session` | Cerrar todas las sesiones (informativo) | Bearer |
| POST | `/admin/auth/forgot-password` | Solicitar recuperación de contraseña | — |
| POST | `/admin/auth/reset-password` | Restablecer contraseña con token | — |
| POST | `/admin/auth/recover-email` | Recuperar email de cuenta | — |
| GET | `/admin/auth/usuarios/{id}` | Obtener datos de un usuario por ID | AdminOrSuper |

### Dashboard (`/admin/dashboard`)

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/admin/dashboard/` | Resumen de dashboard (filtrado por agencia si admin_agencia) | AdminOrSuper |

### Agencias (`/admin/agencias`)

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/admin/agencias/` | Listar agencias (paginado; admin_agencia ve solo la suya) | AdminOrSuper |
| GET | `/admin/agencias/{id}` | Obtener agencia por ID | AdminOrSuper |
| POST | `/admin/agencias/` | Crear agencia | SuperAdmin |
| PUT | `/admin/agencias/{id}` | Actualizar agencia | SuperAdmin |
| DELETE | `/admin/agencias/{id}` | Eliminar agencia | SuperAdmin |

### Agencias-Terminales (`/admin/agencias-terminales`)

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/admin/agencias-terminales/` | Listar relaciones (filtrable por `id_agencia`) | AdminOrSuper |
| GET | `/admin/agencias-terminales/{id}` | Obtener relación por ID | AdminOrSuper |
| POST | `/admin/agencias-terminales/` | Crear relación | SuperAdmin |
| DELETE | `/admin/agencias-terminales/{id}` | Eliminar relación | SuperAdmin |

### Flota — Buses (`/admin/flota/buses`)

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/admin/flota/buses` | Listar buses (paginado, filtrable por `id_agencia`) | AdminOrSuper |
| GET | `/admin/flota/buses/{id}` | Obtener bus por ID | AdminOrSuper |
| POST | `/admin/flota/buses` | Crear bus | AdminOrSuper |
| PUT | `/admin/flota/buses/{id}` | Actualizar bus | AdminOrSuper |
| DELETE | `/admin/flota/buses/{id}` | Eliminar bus | AdminOrSuper |

### Flota — Asientos (`/admin/flota/asientos`)

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/admin/flota/buses/{id}/asientos` | Listar asientos de un bus | AdminOrSuper |
| GET | `/admin/flota/asientos/{id}` | Obtener asiento por ID | AdminOrSuper |
| POST | `/admin/flota/asientos` | Crear asiento | AdminOrSuper |
| PUT | `/admin/flota/asientos/{id}` | Actualizar asiento | AdminOrSuper |
| DELETE | `/admin/flota/asientos/{id}` | Eliminar asiento | AdminOrSuper |

### Rutas (`/admin/rutas`)

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/admin/rutas/` | Listar rutas (filtrable por `id_agencia`) | AdminOrSuper |
| GET | `/admin/rutas/{id}` | Obtener ruta por ID | AdminOrSuper |
| POST | `/admin/rutas/` | Crear ruta | AdminOrSuper |
| PUT | `/admin/rutas/{id}` | Actualizar ruta | AdminOrSuper |
| DELETE | `/admin/rutas/{id}` | Eliminar ruta | AdminOrSuper |
| GET | `/admin/rutas/{id}/tarifas` | Listar tarifas de una ruta | AdminOrSuper |
| GET | `/admin/rutas/tarifas/{id}` | Obtener tarifa por ID | AdminOrSuper |
| POST | `/admin/rutas/tarifas` | Crear tarifa | AdminOrSuper |
| PUT | `/admin/rutas/tarifas/{id}` | Actualizar tarifa | AdminOrSuper |
| DELETE | `/admin/rutas/tarifas/{id}` | Eliminar tarifa | AdminOrSuper |

### Viajes (`/admin/viajes`)

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/admin/viajes/` | Listar viajes (filtrable por `id_agencia`, `id_bus`) | AdminOrSuper |
| GET | `/admin/viajes/{id}` | Obtener viaje por ID | AdminOrSuper |
| POST | `/admin/viajes/` | Crear viaje | AdminOrSuper |
| PUT | `/admin/viajes/{id}` | Actualizar viaje | AdminOrSuper |
| DELETE | `/admin/viajes/{id}` | Eliminar viaje | AdminOrSuper |

### Viajes — Boletos (`/admin/viajes/boletos`)

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/admin/viajes/{id}/boletos` | Listar boletos de un viaje | AdminOrSuper |
| GET | `/admin/viajes/boletos/all` | Listar todos los boletos (global) | AdminOrSuper |
| GET | `/admin/viajes/boletos/{id}` | Obtener boleto por ID | AdminOrSuper |
| POST | `/admin/viajes/boletos` | Crear boleto | AdminOrSuper |
| PUT | `/admin/viajes/boletos/{id}` | Actualizar boleto | AdminOrSuper |
| DELETE | `/admin/viajes/boletos/{id}` | Eliminar boleto | AdminOrSuper |

### Viajes — Pasajeros (`/admin/viajes/pasajeros`)

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/admin/viajes/{id}/pasajeros` | Listar pasajeros de un viaje | AdminOrSuper |
| GET | `/admin/viajes/pasajeros/all` | Listar todos los pasajeros (global) | AdminOrSuper |
| GET | `/admin/viajes/pasajeros/{id}` | Obtener pasajero por ID | AdminOrSuper |
| POST | `/admin/viajes/pasajeros` | Crear pasajero | AdminOrSuper |
| PUT | `/admin/viajes/pasajeros/{id}` | Actualizar pasajero | AdminOrSuper |
| DELETE | `/admin/viajes/pasajeros/{id}` | Eliminar pasajero | AdminOrSuper |

### Terminales (`/admin/terminales`)

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/admin/terminales/` | Listar terminales (admin_agencia ve solo asociados) | AdminOrSuper |
| GET | `/admin/terminales/{id}` | Obtener terminal por ID | AdminOrSuper |
| POST | `/admin/terminales/` | Crear terminal (auto-asigna agencia si admin_agencia) | AdminOrSuper |
| PUT | `/admin/terminales/{id}` | Actualizar terminal | AdminOrSuper |
| DELETE | `/admin/terminales/{id}` | Eliminar terminal | AdminOrSuper |

### Choferes (`/admin/choferes`)

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/admin/choferes/` | Listar choferes (filtrable por `id_agencia`) | AdminOrSuper |
| GET | `/admin/choferes/{id}` | Obtener chofer por ID | AdminOrSuper |
| POST | `/admin/choferes/` | Crear chofer | AdminOrSuper |
| PUT | `/admin/choferes/{id}` | Actualizar chofer | AdminOrSuper |
| DELETE | `/admin/choferes/{id}` | Eliminar chofer | AdminOrSuper |

### Suscripciones — Planes (`/admin/planes`)

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/admin/planes/` | Listar planes | AdminOrSuper |
| GET | `/admin/planes/{id}` | Obtener plan por ID | AdminOrSuper |
| POST | `/admin/planes/` | Crear plan | SuperAdmin |
| PUT | `/admin/planes/{id}` | Actualizar plan | SuperAdmin |
| DELETE | `/admin/planes/{id}` | Eliminar plan | SuperAdmin |

### Suscripciones (`/admin/suscripciones`)

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/admin/suscripciones/` | Listar suscripciones (filtrable por `id_agencia`) | AdminOrSuper |
| GET | `/admin/suscripciones/{id}` | Obtener suscripción por ID | AdminOrSuper |
| POST | `/admin/suscripciones/` | Crear suscripción | AdminOrSuper |
| PUT | `/admin/suscripciones/{id}` | Actualizar suscripción | AdminOrSuper |
| DELETE | `/admin/suscripciones/{id}` | Eliminar suscripción | AdminOrSuper |

### Boletos (`/admin/boletos`)

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/admin/boletos/` | Listar boletos (filtrable por `id_agencia`) | AdminOrSuper |
| GET | `/admin/boletos/{id}` | Obtener boleto por ID | AdminOrSuper |
| POST | `/admin/boletos/` | Crear boleto | AdminOrSuper |
| PUT | `/admin/boletos/{id}` | Actualizar boleto | AdminOrSuper |
| DELETE | `/admin/boletos/{id}` | Eliminar boleto | AdminOrSuper |

### Pasajeros (`/admin/pasajeros`)

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/admin/pasajeros/` | Listar pasajeros (filtrable por `id_agencia`) | AdminOrSuper |
| GET | `/admin/pasajeros/{id}` | Obtener pasajero por ID | AdminOrSuper |
| POST | `/admin/pasajeros/` | Crear pasajero | AdminOrSuper |
| PUT | `/admin/pasajeros/{id}` | Actualizar pasajero | AdminOrSuper |
| DELETE | `/admin/pasajeros/{id}` | Eliminar pasajero | AdminOrSuper |

### Soporte (`/admin/soporte`)

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/admin/soporte/` | Listar tickets (filtrable por `id_agencia`) | AdminOrSuper |
| GET | `/admin/soporte/{id}` | Obtener ticket por ID | AdminOrSuper |
| GET | `/admin/soporte/{id}/historial` | Historial de cambios del ticket | AdminOrSuper |
| POST | `/admin/soporte/` | Crear ticket | AdminOrSuper |
| PUT | `/admin/soporte/{id}` | Actualizar ticket (registra cambio en historial) | AdminOrSuper |
| DELETE | `/admin/soporte/{id}` | Eliminar ticket | AdminOrSuper |

### Reclamos (`/admin/reclamos`)

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/admin/reclamos/` | Listar reclamos (filtrable por `id_agencia`) | AdminOrSuper |
| GET | `/admin/reclamos/{id}` | Obtener reclamo por ID | AdminOrSuper |
| POST | `/admin/reclamos/` | Crear reclamo | AdminOrSuper |
| PUT | `/admin/reclamos/{id}` | Actualizar reclamo | AdminOrSuper |
| DELETE | `/admin/reclamos/{id}` | Eliminar reclamo | AdminOrSuper |
| GET | `/admin/reclamos/{id}/mensajes` | Listar mensajes de un reclamo | AdminOrSuper |
| POST | `/admin/reclamos/{id}/mensajes` | Enviar mensaje en un reclamo | AdminOrSuper |

### Finanzas — Liquidaciones (`/admin/liquidaciones`)

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/admin/liquidaciones` | Listar liquidaciones (filtrable por `id_agencia`) | AdminOrSuper |
| GET | `/admin/liquidaciones/{id}` | Obtener liquidación por ID | AdminOrSuper |
| POST | `/admin/liquidaciones` | Crear liquidación | AdminOrSuper |
| PUT | `/admin/liquidaciones/{id}` | Actualizar liquidación | AdminOrSuper |
| DELETE | `/admin/liquidaciones/{id}` | Eliminar liquidación | AdminOrSuper |

### Finanzas — API Keys (`/admin/api-keys`)

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/admin/api-keys` | Listar API keys (filtrable por `id_agencia`) | AdminOrSuper |
| GET | `/admin/api-keys/{id}` | Obtener API key por ID | AdminOrSuper |
| POST | `/admin/api-keys` | Crear API key (auto-genera token si se omite) | AdminOrSuper |
| PUT | `/admin/api-keys/{id}` | Actualizar API key | AdminOrSuper |
| DELETE | `/admin/api-keys/{id}` | Eliminar API key | AdminOrSuper |

### Reportes (`/reports`)

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/reports/{slug}` | Datos del reporte (`ventas`, `viajes`, `manifiesto-sutran`) | AdminOrSuper |
| GET | `/reports/{slug}/export/excel` | Exportar reporte a Excel | AdminOrSuper |

### Manifiestos (`/admin/manifiestos`)

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/admin/manifiestos/` | Listar manifiestos SUTRAN (paginado) | AdminOrSuper |

### Notificaciones (`/admin/notificaciones`)

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/admin/notificaciones/` | Listar notificaciones (filtrable: solo no leídas) | Bearer |
| GET | `/admin/notificaciones/contar` | Contar notificaciones no leídas | Bearer |
| PUT | `/admin/notificaciones/{id}` | Marcar una notificación como leída | Bearer |
| PUT | `/admin/notificaciones/leer-todas` | Marcar todas como leídas | Bearer |

### Ubigeo (`/admin/ubigeo`)

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/admin/ubigeo/departamentos` | Listar departamentos | AdminOrSuper |
| GET | `/admin/ubigeo/provincias` | Provincias (filtrable por `id_departamento`) | AdminOrSuper |
| GET | `/admin/ubigeo/distritos` | Distritos (filtrable por `id_provincia`) | AdminOrSuper |

### Endpoints Públicos (`/api/v1`)

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/api/v1/viajes/{id}/asientos` | Asientos disponibles de un viaje | API Key |
| POST | `/api/v1/boletos` | Crear boleto desde integración externa | API Key |

## Roles y permisos

| Rol | Acceso |
|-----|--------|
| `superadmin` | Todos los endpoints admin. Crear/editar/eliminar agencias, planes, API keys. |
| `admin_agencia` | CRUD de su propia agencia (buses, rutas, viajes, etc.). Solo lectura de su agencia. |
| `cliente` | No tiene acceso a endpoints admin. |

Las dependencias de autorización se definen en `app/dependencies.py`:

- `Bearer` — Token JWT válido
- `AdminOrSuper` — Requiere rol `admin_agencia` o `superadmin`
- `SuperAdmin` — Requiere rol `superadmin`
- `ApiKeyAuth` — Autenticación vía header `x-api-key`

## Autenticación

1. **Login**: `POST /admin/auth/login` → devuelve `accessToken`, `refreshToken`, `rol`, `idUsuario`, `idAgencia`
2. **Uso**: Enviar `Authorization: Bearer <accessToken>` en cada request
3. **Refresh**: `POST /admin/auth/refresh` con `refreshToken` en el body
4. **Logout**: Cliente elimina el token localmente

El JWT contiene: `sub` (id_usuario), `email`, `rol`, `id_agencia`.

## API Key (para endpoints públicos)

Los endpoints públicos usan autenticación via header `x-api-key`. Las API keys se gestionan desde `/admin/api-keys`.

## Schemas camelCase

Todos los schemas de respuesta y request usan alias **camelCase** para compatibilidad con el frontend TypeScript:

```json
{
  "id": 1,
  "razonSocial": "TransportesSur S.A.C.",
  "estado": "activa",
  "bancoNombre": null,
  "numeroCuenta": null,
  "cuentaCci": null
}
```

## Documentación interactiva

- **Swagger UI**: http://localhost:5000/docs
- **ReDoc**: http://localhost:5000/redoc

## Migraciones con Alembic

```bash
# Generar migración automática
alembic revision --autogenerate -m "descripcion_del_cambio"

# Aplicar migraciones pendientes
alembic upgrade head

# Ver historial
alembic history

# Revertir última migración
alembic downgrade -1
```
