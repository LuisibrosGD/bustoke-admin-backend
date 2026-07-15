# Matriz de Casos de Prueba — Bustoke Admin Backend

> **Proyecto:** Bustoke Admin API (FastAPI + async SQLAlchemy 2.x + PostgreSQL 15)
> **Estándares:** ISTQB / ISO/IEC 29119
> **Enfoques:** Caja Negra (Partición de Equivalencia + VLC), Caja Blanca (Cobertura de Caminos), Basada en Riesgos
> **Credenciales de prueba:** `actividades/credenciales.md`

---

## 1. Pruebas de Caja Negra

### 1.1 Módulo Auth — Login (`POST /admin/auth/login`)

| ID | Componente/Módulo | Tipo de Prueba | Descripción del Caso | Precondiciones | Datos de Entrada | Pasos de Ejecución | Resultado Esperado |
|---|---|---|---|---|---|---|---|
| CN-01 | Auth | Caja Negra — PE | Login exitoso de **Superadmin** | Usuario existe en BD: `sebastian.admin@bustoke.pe`, rol `superadmin`, contraseña `TempPassword123!5`, `activo = true` | `{ "email": "sebastian.admin@bustoke.pe", "password": "TempPassword123!5" }` | 1. `POST /admin/auth/login` con body.\n2. Validar status code.\n3. Validar estructura de respuesta. | `200`. Retorna `accessToken`, `refreshToken`, `tokenType: "bearer"`, `rol: "superadmin"`, `idUsuario` numérico, `idAgencia: null`. |
| CN-02 | Auth | Caja Negra — PE | Login exitoso de **Admin de Agencia (Cruz del Sur)** | Usuario existe: `admin.cruz@cruzdelsur.com.pe`, rol `admin_agencia`, `id_agencia` vinculado a Cruz del Sur, contraseña `TempPassword123!1`, `activo = true` | `{ "email": "admin.cruz@cruzdelsur.com.pe", "password": "TempPassword123!1" }` | 1. `POST /admin/auth/login` con body.\n2. Validar estructura. | `200`. Campos esperados: `rol: "admin_agencia"`, `idAgencia` valor numérico (no null). |
| CN-03 | Auth | Caja Negra — PE | Login exitoso de **Admin de Agencia (Oltursa)** | Usuario existe: `admin.oltursa@oltursa.com.pe`, rol `admin_agencia`, `id_agencia` vinculado a Oltursa, contraseña `TempPassword123!2` | `{ "email": "admin.oltursa@oltursa.com.pe", "password": "TempPassword123!2" }` | 1. `POST /admin/auth/login` con body. | `200`. `rol: "admin_agencia"`, `idAgencia` ≠ null. |
| CN-04 | Auth | Caja Negra — PE | Login exitoso de **Admin de Agencia (Civa)** | Usuario existe: `admin.civa@civa.com.pe`, rol `admin_agencia`, contraseña `TempPassword123!3` | `{ "email": "admin.civa@civa.com.pe", "password": "TempPassword123!3" }` | 1. `POST /admin/auth/login` con body. | `200`. `rol: "admin_agencia"`. |
| CN-05 | Auth | Caja Negra — PE | Login exitoso de **Admin de Agencia (Movil Bus)** | Usuario existe: `admin.movil@movilbus.com.pe`, rol `admin_agencia`, contraseña `TempPassword123!4` | `{ "email": "admin.movil@movilbus.com.pe", "password": "TempPassword123!4" }` | 1. `POST /admin/auth/login` con body. | `200`. `rol: "admin_agencia"`. |
| CN-06 | Auth | Caja Negra — PE | Login con email no registrado | No existe usuario con ese email en tabla `usuarios` | `{ "email": "noexiste@test.com", "password": "Cualquier123!" }` | 1. `POST /admin/auth/login` con body. | `401 Unauthorized` con `{ "detail": "Credenciales incorrectas" }`. No revelar si el email existe o no. |
| CN-07 | Auth | Caja Negra — PE | Login con contraseña incorrecta (email real) | Usuario existe `sebastian.admin@bustoke.pe`, se envía password distinto | `{ "email": "sebastian.admin@bustoke.pe", "password": "WrongPass999!" }` | 1. `POST /admin/auth/login` con body. | `401 Unauthorized` con `{ "detail": "Credenciales incorrectas" }`. |
| CN-08 | Auth | Caja Negra — PE | Login de usuario inactivo | Usuario existe con email `cliente.user6@gmail.com` (o cualquier cliente), `activo = false` | `{ "email": "cliente.user6@gmail.com", "password": "password123" }` | 1. `POST /admin/auth/login` con body. | `401 Unauthorized` con `{ "detail": "Usuario inactivo" }`. |
| CN-09 | Auth | Caja Negra — VLC | Email con formato inválido (partición inválida) | — | `{ "email": "correo-invalido", "password": "Test123!" }` | 1. `POST /admin/auth/login` con body. | `422 Unprocessable Entity` — validación Pydantic `EmailStr` rechaza el formato. |
| CN-10 | Auth | Caja Negra — VLC | Password vacío (valor límite) | — | `{ "email": "sebastian.admin@bustoke.pe", "password": "" }` | 1. `POST /admin/auth/login` con body. | `422` si Pydantic tiene `min_length` (por defecto acepta string vacío → pasaría a `verify_password` y retornaría `401`). |

### 1.2 Módulo Auth — Refresh Token (`POST /admin/auth/refresh`)

| ID | Componente/Módulo | Tipo de Prueba | Descripción del Caso | Precondiciones | Datos de Entrada | Pasos de Ejecución | Resultado Esperado |
|---|---|---|---|---|---|---|---|
| CN-11 | Auth | Caja Negra — PE | Refresh exitoso con refresh token válido (Superadmin) | Login previo de `sebastian.admin@bustoke.pe` que devuelve `refreshToken` | `{ "refreshToken": "<refresh_token_jwt>" }` | 1. `POST /admin/auth/refresh` con body. | `200`. Retorna nuevos `accessToken` y `refreshToken` con mismo `rol: "superadmin"`, `idUsuario`, `idAgencia: null`. |
| CN-12 | Auth | Caja Negra — PE | Refresh exitoso con refresh token válido (Admin Agencia) | Login previo de `admin.cruz@cruzdelsur.com.pe` que devuelve `refreshToken` | `{ "refreshToken": "<refresh_token_jwt>" }` | 1. `POST /admin/auth/refresh` con body. | `200`. `rol: "admin_agencia"`, `idAgencia` corresponde a Cruz del Sur. |
| CN-13 | Auth | Caja Negra — PE | Refresh con token de tipo access (inválido) | Obtener un `accessToken` vía login con cualquier credencial | `{ "refreshToken": "<access_token_jwt>" }` | 1. `POST /admin/auth/refresh` con body. | `401 Unauthorized` con `{ "detail": "Token de tipo incorrecto" }`. |
| CN-14 | Auth | Caja Negra — VLC | Refresh con token expirado | Token refresh con `exp` en el pasado (modificar manualmente o esperar 7 días) | `{ "refreshToken": "<refresh_token_expirado>" }` | 1. `POST /admin/auth/refresh` con body. | `401 Unauthorized` con `{ "detail": "Refresh token inválido o expirado" }`. |
| CN-15 | Auth | Caja Negra — PE | Refresh con token malformado (string aleatorio) | — | `{ "refreshToken": "abc123.token.invalido" }` | 1. `POST /admin/auth/refresh` con body. | `401 Unauthorized` con `{ "detail": "Refresh token inválido o expirado" }`. |

### 1.3 Módulo Auth — Forgot / Reset Password

| ID | Componente/Módulo | Tipo de Prueba | Descripción del Caso | Precondiciones | Datos de Entrada | Pasos de Ejecución | Resultado Esperado |
|---|---|---|---|---|---|---|---|
| CN-16 | Auth | Caja Negra — PE | Solicitar restablecimiento para Superadmin existente | Usuario `sebastian.admin@bustoke.pe` existe en BD | `{ "email": "sebastian.admin@bustoke.pe" }` | 1. `POST /admin/auth/forgot-password` con body. | `200`. `{ "message": "Si el correo existe, recibirás instrucciones de recuperación" }`. Internamente genera token JWT de tipo `password_reset` con 1h de expiración. *Nota: No hay envío de email implementado (TODO en código).* |
| CN-17 | Auth | Caja Negra — PE | Solicitar restablecimiento para Admin de Agencia existente | Usuario `admin.civa@civa.com.pe` existe | `{ "email": "admin.civa@civa.com.pe" }` | 1. `POST /admin/auth/forgot-password` con body. | `200`. Mismo mensaje genérico (no revela si existe). |
| CN-18 | Auth | Caja Negra — PE | Solicitar restablecimiento para email no registrado | — | `{ "email": "nadie@bustoke.pe" }` | 1. `POST /admin/auth/forgot-password` con body. | `200`. Mismo mensaje. Seguridad: no diferenciar entre existente/inexistente. |
| CN-19 | Auth | Caja Negra — VLC | Reset password con token expirado | Token `password_reset` generado hace > 1 hora | `{ "token": "<reset_token_expirado>", "newPassword": "NuevaClave1" }` | 1. `POST /admin/auth/reset-password` con body. | `400 Bad Request` con `{ "detail": "Token de restablecimiento inválido o expirado" }`. |
| CN-20 | Auth | Caja Negra — PE | Reset password exitoso para Admin de Agencia | Token `password_reset` válido recién generado (vía forgot-password) para `admin.oltursa@oltursa.com.pe` | `{ "token": "<reset_token_valido>", "newPassword": "MiNuevaPass123!" }` | 1. `POST /admin/auth/reset-password`. 2. Intentar login con la nueva contraseña. | 1. `200`. 2. Login con `admin.oltursa@oltursa.com.pe` / `MiNuevaPass123!` → `200`. |

### 1.4 Módulo Viajes — CRUD (`/admin/viajes`)

| ID | Componente/Módulo | Tipo de Prueba | Descripción del Caso | Precondiciones | Datos de Entrada | Pasos de Ejecución | Resultado Esperado |
|---|---|---|---|---|---|---|---|
| CN-21 | Viajes | Caja Negra — VLC | Listar viajes con límite en borde inferior (limit=1) | Existen ≥ 2 viajes en BD. Token de Superadmin `sebastian.admin@bustoke.pe` | `GET /admin/viajes?skip=0&limit=1` con token Superadmin | 1. `GET /admin/viajes?skip=0&limit=1` con header `Authorization: Bearer <token>`. | `200`. Arreglo con exactamente 1 elemento. |
| CN-22 | Viajes | Caja Negra — VLC | Listar viajes con límite en borde superior (limit=500) | Existen ≥ 500 viajes en BD | `GET /admin/viajes?skip=0&limit=500` con token Superadmin | 1. `GET /admin/viajes?skip=0&limit=500`. | `200`. Máximo 500 elementos. |
| CN-23 | Viajes | Caja Negra — VLC | Listar viajes con límite sobre el máximo (limit=501) | — | `GET /admin/viajes?skip=0&limit=501` con token Superadmin | 1. Realizar request. | `422`. FastAPI rechaza por `Query(..., le=500)`. |
| CN-24 | Viajes | Caja Negra — VLC | Listar viajes con skip negativo (skip=-1) | — | `GET /admin/viajes?skip=-1&limit=10` con token Superadmin | 1. Realizar request. | `422`. FastAPI rechaza por `Query(..., ge=0)`. |
| CN-25 | Viajes | Caja Negra — PE | Listar viajes filtrados por agencia (Admin Cruz del Sur) | Token JWT de `admin.cruz@cruzdelsur.com.pe`. Existen viajes de Cruz del Sur y de Oltursa. | `GET /admin/viajes` con token de Cruz del Sur (sin query param `id_agencia`) | 1. Router: detecta `rol: admin_agencia`, fuerza `id_agencia` desde JWT. 2. Solo retorna viajes cuya ruta pertenece a la agencia del token. | `200`. Solo viajes de Cruz del Sur. **No deben aparecer** viajes de Oltursa, Civa ni Movil Bus. |
| CN-26 | Viajes | Caja Negra — PE | Listar viajes sin filtro (Superadmin ve todos) | Token JWT de `sebastian.admin@bustoke.pe` | `GET /admin/viajes` con token Superadmin | 1. Router: rol `superadmin` no fuerza filtro de agencia. | `200`. Todos los viajes de todas las agencias. |
| CN-27 | Viajes | Caja Negra — PE | Admin de agencia intenta filtrar viajes de otra agencia vía query param | Token de `admin.cruz@cruzdelsur.com.pe` (id_agencia=1). Se envía `?id_agencia=2` (Oltursa). | `GET /admin/viajes?id_agencia=2` con token de Cruz del Sur | 1. Router: `admin_agencia` → sobrescribe con id_agencia del JWT (ignora query param). | `200`. Solo viajes de Cruz del Sur (id_agencia=1). Query param es ignorado. |
| CN-28 | Viajes | Caja Negra — PE | Crear viaje exitoso (Superadmin) | Ruta con `id_ruta=1`, Bus con `id_bus=1`, Chofer con `id_chofer=1` existen. Token de `sebastian.admin@bustoke.pe`. | `{ "idRuta": 1, "idBus": 1, "idChofer": 1, "fechaHoraSalida": "2026-08-15T06:00:00", "fechaHoraLlegada": "2026-08-15T10:30:00", "estado": "programado", "rampaEmbarque": "Puerta 3" }` | 1. `POST /admin/viajes` con token Superadmin. 2. Validar status. 3. Validar respuesta. | `201 Created`. Retorna `ViajeOut` con `id` asignado y campos coincidentes. |
| CN-29 | Viajes | Caja Negra — PE | Crear viaje con estado inválido (partición inválida) | Token Superadmin | `{ "idRuta": 1, "idBus": 1, "fechaHoraSalida": "2026-08-15T06:00:00", "fechaHoraLlegada": "2026-08-15T10:30:00", "estado": "volando" }` | 1. `POST /admin/viajes`. | `422` o error BD. El ENUM `estado_viaje` solo acepta: `programado`, `en_curso`, `finalizado`, `cancelado`. |
| CN-30 | Viajes | Caja Negra — VLC | Crear viaje con `fechaHoraLlegada` anterior a `fechaHoraSalida` | Token Superadmin | `{ "idRuta": 1, "idBus": 1, "fechaHoraSalida": "2026-08-15T10:00:00", "fechaHoraLlegada": "2026-08-15T06:00:00", "estado": "programado" }` | 1. `POST /admin/viajes`. | `201`. **Defecto:** No hay validación backend que impida esto. El sistema lo crea con datos inconsistentes. |
| CN-31 | Viajes | Caja Negra — PE | Obtener viaje por ID inexistente | Token Superadmin. No existe viaje con `id_viaje=99999`. | `GET /admin/viajes/99999` | 1. `GET /admin/viajes/99999`. | `404 Not Found` con `{ "detail": "Viaje 99999 no encontrado" }`. |
| CN-32 | Viajes | Caja Negra — PE | Eliminar viaje existente (Superadmin) | Viaje `id=5` existe en BD | `DELETE /admin/viajes/5` con token Superadmin | 1. `DELETE /admin/viajes/5`. | `200`. `{ "message": "Viaje 5 eliminado" }`. Elemento eliminado de BD. |

### 1.5 Módulo Boletos — Creación (`POST /admin/viajes/boletos`)

| ID | Componente/Módulo | Tipo de Prueba | Descripción del Caso | Precondiciones | Datos de Entrada | Pasos de Ejecución | Resultado Esperado |
|---|---|---|---|---|---|---|---|
| CN-33 | Boletos | Caja Negra — PE | Crear boleto exitoso con todos los campos (Admin de Agencia) | Viaje `id_viaje=1` existe, Pasajero `id_pasajero=1` existe, Asiento `id_asiento=10` está libre. Token de `admin.movil@movilbus.com.pe`. | `{ "idViaje": 1, "idUsuario": null, "idPasajero": 1, "idAsiento": 10, "emailContacto": "r@bustoke.pe", "canal": "app_bustoke", "codigoQr": "BKT-20260815-1A-ABC123", "precioFinal": 45.50 }` | 1. `POST /admin/viajes/boletos` con token AdminOrSuper. | `201 Created`. Retorna `BoletoOut` con `estado: "activo"`, `usado: false`, `estadoCheckin: "pendiente"`, `fechaEmision` asignada automáticamente. |
| CN-34 | Boletos | Caja Negra — VLC | Precio final con valor límite mínimo (0.01) | Viaje y Pasajero existen. Token Superadmin. | `{ ... "precioFinal": 0.01, "canal": "app_bustoke", "codigoQr": "BKT-TEST-001" }` | 1. `POST /admin/viajes/boletos`. | `201`. Boleto creado con `precioFinal = 0.01`. |
| CN-35 | Boletos | Caja Negra — VLC | Precio final con valor cero (fuera de límite esperado) | Viaje y Pasajero existen. Token Superadmin. | `{ ... "precioFinal": 0.00, ... }` | 1. `POST /admin/viajes/boletos`. | `201`. Se crea con precio 0.00. **Defecto ausente:** No hay validación de precio > 0 en backend. |
| CN-36 | Boletos | Caja Negra — PE | Crear boleto con canal inválido | Token Superadmin | `{ ... "canal": "whatsapp", ... }` | 1. `POST /admin/viajes/boletos`. | Error BD. ENUM `canal_venta` solo acepta: `app_bustoke`, `ventanilla_fisica`, `api_externa`. |
| CN-37 | Boletos | Caja Negra — PE | Crear boleto con código QR duplicado | Ya existe boleto con `codigo_qr = "BKT-DUP-001"`. Token Superadmin. | `{ ... "codigoQr": "BKT-DUP-001", ... }` | 1. `POST /admin/viajes/boletos`. | Error BD (unique constraint violation). Sin manejo explícito → responde `500`. **Defecto:** debería ser `409 Conflict`. |

### 1.6 Módulo Boletos — Check-in y QR

| ID | Componente/Módulo | Tipo de Prueba | Descripción del Caso | Precondiciones | Datos de Entrada | Pasos de Ejecución | Resultado Esperado |
|---|---|---|---|---|---|---|---|
| CN-38 | Boletos | Caja Negra — PE | Check-in exitoso de boleto (cambiar estado) | Boleto `id=3` existe con `estado_checkin = "pendiente"`. Token AdminOrSuper. | `{ "estadoCheckin": "realizado" }` | 1. `PUT /admin/viajes/boletos/3/check-in` con body. | `200`. Boleto actualizado con `estadoCheckin: "realizado"`. |
| CN-39 | Boletos | Caja Negra — PE | Escanear QR válido para un viaje | Boleto con `codigo_qr = "BKT-SCAN-001"` existe para viaje `id=1`. Token AdminOrSuper. | `{ "codigoQr": "BKT-SCAN-001" }` | 1. `POST /admin/viajes/1/check-in/scan` con body. | `200`. Retorna `BoletoOut` del boleto encontrado. |
| CN-40 | Boletos | Caja Negra — PE | Escanear QR que no pertenece al viaje | Boleto con `codigo_qr = "BKT-OTRO"` pertenece a viaje `id=2`, no a viaje `id=1`. Token AdminOrSuper. | `{ "codigoQr": "BKT-OTRO" }` | 1. `POST /admin/viajes/1/check-in/scan` con body. | `404 Not Found` con `{ "detail": "No se encontró un boleto con ese código QR para el viaje 1" }`. |

### 1.7 Módulo Público — API Key (`/api/v1`)

| ID | Componente/Módulo | Tipo de Prueba | Descripción del Caso | Precondiciones | Datos de Entrada | Pasos de Ejecución | Resultado Esperado |
|---|---|---|---|---|---|---|---|
| CN-41 | Público | Caja Negra — PE | Consultar asientos disponibles con API Key válida | API Key activa existe en tabla `api_keys`, viaje `id_viaje=1` existe | `GET /api/v1/viajes/1/asientos` con header `x-api-key: <api_key_valida>` | 1. `GET /api/v1/viajes/1/asientos` con header. | `200`. Arreglo con todos los asientos del bus, cada uno con campos: `id`, `numeroAsiento`, `fila`, `piso`, `tipoServicio`, `ocupado`, `bloqueado`. |
| CN-42 | Público | Caja Negra — PE | Consultar asientos sin API Key | — | `GET /api/v1/viajes/1/asientos` sin header `x-api-key` | 1. Realizar request sin header. | `401 Unauthorized` con `{ "detail": "API Key requerida (header x-api-key)" }`. |
| CN-43 | Público | Caja Negra — PE | Consultar asientos con API Key inválida | — | `GET /api/v1/viajes/1/asientos` con header `x-api-key: clave-falsa` | 1. Realizar request con API Key falsa. | `401 Unauthorized` con `{ "detail": "API Key inválida o expirada" }`. |
| CN-44 | Público | Caja Negra — PE | Crear boleto externo con asiento ya ocupado | Viaje `id=1`, asiento `id=5` ya tiene un boleto activo. API Key válida. | `{ "idViaje": 1, "idAsiento": 5, "emailContacto": "c@x.com", "precioFinal": 30.00, "pasajero": { "idTipoDocumento": 1, "numeroDocumento": "12345678", "nombres": "Juan", "apellidoPaterno": "Perez", "apellidoMaterno": "Lopez" } }` | 1. `POST /api/v1/boletos` con API Key y body. | `400 Bad Request` con `{ "detail": "El asiento ya se encuentra ocupado" }`. |
| CN-45 | Público | Caja Negra — PE | Crear boleto externo exitoso con pasajero nuevo | Viaje `id=1`, asiento `id=20` libre. API Key válida. | Misma estructura que CN-44, con `idAsiento: 20`, `numeroDocumento: "87654321"`. | 1. `POST /api/v1/boletos`. | `201`. Retorna `BoletoExternoOut` con `codigoQr` generado automáticamente (formato `BKT-EXT-{viaje}-{asiento}-{hex}`). |

### 1.8 Módulo Dashboard y Reportes

| ID | Componente/Módulo | Tipo de Prueba | Descripción del Caso | Precondiciones | Datos de Entrada | Pasos de Ejecución | Resultado Esperado |
|---|---|---|---|---|---|---|---|
| CN-46 | Dashboard | Caja Negra — PE | Admin de agencia ve dashboard de su propia agencia | Token de `admin.cruz@cruzdelsur.com.pe`. Existen boletos/viajes de varias agencias. | `GET /admin/dashboard/` con token de Cruz del Sur | 1. Realizar request. | `200`. Datos resumidos solo de Cruz del Sur. |
| CN-47 | Dashboard | Caja Negra — PE | Superadmin ve dashboard global | Token de `sebastian.admin@bustoke.pe` | `GET /admin/dashboard/` | 1. Realizar request. | `200`. Datos consolidados de todas las agencias. |

---

## 2. Pruebas de Caja Blanca

**Componente crítico seleccionado:** Función `authenticate_user` en `app/modules/auth/service.py:17-26` y función `list_viajes` en `app/modules/viajes/router.py:24-44`.

### 2.1 Cobertura de Caminos — `authenticate_user`

4 decisiones secuenciales → 5 caminos factibles (3 cortocircuitos + 1 feliz + 1 hash inválido):

| ID | Componente/Módulo | Tipo de Prueba | Descripción del Caso | Precondiciones | Datos de Entrada | Pasos de Ejecución | Resultado Esperado |
|---|---|---|---|---|---|---|---|
| CB-01 | Auth — `authenticate_user` | Caja Blanca — Cobertura de Caminos | **Camino A:** usuario no existe (1ª decisión False) | No hay usuario con ese email | `{ "email": "ghost@test.com", "password": "x" }` | 1. `POST /admin/auth/login`. 2. `select(Usuario).where(email == "ghost@test.com")` → `scalar_one_or_none()` = `None`. | `401 Unauthorized` — cortocircuito en primera condición. |
| CB-02 | Auth — `authenticate_user` | Caja Blanca — Cobertura de Caminos | **Camino B:** usuario existe pero inactivo (2ª decisión False) | Usuario existente con `activo = false` | `{ "email": "cliente.user6@gmail.com", "password": "password123" }` (asumiendo cliente inactivo) | 1. Usuario encontrado. 2. `user.activo` = False. | `401 Unauthorized` — mensaje: `"Usuario inactivo"`. |
| CB-03 | Auth — `authenticate_user` | Caja Blanca — Cobertura de Caminos | **Camino C:** usuario activo pero password incorrecto (3ª decisión False) | Usuario activo existe, se envía password incorrecto | `{ "email": "sebastian.admin@bustoke.pe", "password": "ClaveErronea999" }` | 1. Usuario encontrado, activo. 2. `verify_password(password, user.password_hash)` = False (retorna False porque bcrypt.checkpw falla). | `401 Unauthorized` — mensaje: `"Credenciales incorrectas"`. |
| CB-04 | Auth — `authenticate_user` | Caja Blanca — Cobertura de Caminos | **Camino D:** hash bcrypt con prefijo inválido (path excepcional) | Hash en BD no comienza con `$2a$`, `$2b$` o `$2y$` (ej: hash corrupto de `fix-pass.py`) | `{ "email": "admin.cruz@cruzdelsur.com.pe", "password": "TempPassword123!1" }` | 1. `verify_password()`: `hashed_password.startswith(...)` = False. 2. Log de error y retorna False. | `401 Unauthorized`. Internamente: `[ERROR] Hash no es bcrypt válido`. |
| CB-05 | Auth — `authenticate_user` | Caja Blanca — Cobertura de Caminos | **Camino E:** todas las condiciones verdaderas (flujo feliz) | Usuario activo existe, password correcto | `{ "email": "sebastian.admin@bustoke.pe", "password": "TempPassword123!5" }` | 1. Usuario encontrado, activo. 2. `verify_password(..., user.password_hash)` = True. 3. `build_token_response(user)`. | `200` con `TokenResponse` completo. |

### 2.2 Cobertura de Decisiones — `list_viajes` (Router dispatch)

| ID | Componente/Módulo | Tipo de Prueba | Descripción del Caso | Precondiciones | Datos de Entrada | Pasos de Ejecución | Resultado Esperado |
|---|---|---|---|---|---|---|---|
| CB-06 | Viajes — Router `list_viajes` | Caja Blanca — Cobertura de Decisiones | **Rama `id_bus`:** filtrar por bus | Bus `id_bus=2` tiene viajes asignados. Token Superadmin. | `GET /admin/viajes?id_bus=2` | 1. Router evalúa primer `if id_bus is not None`. 2. Llama a `get_viajes_by_bus(db, 2, 0, 100)`. | `200`. Solo viajes cuyo `id_bus == 2`. |
| CB-07 | Viajes — Router `list_viajes` | Caja Blanca — Cobertura de Decisiones | **Rama `id_ruta`:** filtrar por ruta | Ruta `id_ruta=3` tiene viajes. Token Superadmin. | `GET /admin/viajes?id_ruta=3` | 1. `id_bus` es None, `id_ruta` no es None. 2. `get_viajes_by_ruta(db, 3, 0, 100)`. | `200`. Solo viajes con `id_ruta == 3`. |
| CB-08 | Viajes — Router `list_viajes` | Caja Blanca — Cobertura de Decisiones | **Rama `admin_agencia`:** fuerza `id_agencia` desde JWT | Token de `admin.cruz@cruzdelsur.com.pe` (rol: `admin_agencia`, `id_agencia: X`). Viajes de Cruz del Sur y Oltursa existen. | `GET /admin/viajes` sin query param `id_agencia` | 1. `id_bus` None, `id_ruta` None. 2. `user_rol == "admin_agencia"` → `id_agencia = X` (forzado). 3. `get_viajes_by_agencia(db, X, 0, 100)`. | `200`. Solo viajes de la agencia del token. |
| CB-09 | Viajes — Router `list_viajes` | Caja Blanca — Cobertura de Decisiones | **Rama filter fallback:** `id_agencia` explícito en query param (Superadmin) | Token Superadmin. `id_agencia=5` especificado. | `GET /admin/viajes?id_agencia=5` | 1. Todos los if previos falsos. 2. `id_agencia=5` (del query param). 3. `get_viajes_by_agencia(db, 5, 0, 100)`. | `200`. Solo viajes de agencia 5. |
| CB-10 | Viajes — Router `list_viajes` | Caja Blanca — Cobertura de Decisiones | **Rama default:** `get_all_viajes` (sin filtros) | Token Superadmin. Sin query params de filtro. | `GET /admin/viajes` | 1. Todos los condicionales falsos. 2. `get_all_viajes(db, 0, 100)`. | `200`. Todos los viajes (sin filtro). |

### 2.3 Cobertura de Decisiones — `verify_password`

| ID | Componente/Módulo | Tipo de Prueba | Descripción del Caso | Precondiciones | Datos de Entrada | Pasos de Ejecución | Resultado Esperado |
|---|---|---|---|---|---|---|---|
| CB-11 | Core — `verify_password` (`security.py:10-33`) | Caja Blanca — Cobertura de Decisiones | **Rama A:** hash_length < 50 | Hash corrupto guardado en BD | `{ "email": "admin.civa@civa.com.pe", "password": "TempPassword123!3" }` (con hash truncado en BD) | 1. `len(hashed_password) < 50` → `True`. 2. Log `[ERROR] Hash inválido`. 3. Retorna `False`. | `401`. |
| CB-12 | Core — `verify_password` | Caja Blanca — Cobertura de Decisiones | **Rama B:** hash no comienza con `$2` | Hash con formato incorrecto | `{ "email": "admin.civa@civa.com.pe", "password": "TempPassword123!3" }` (hash en BD: `$1$...` tipo MD5) | 1. Pasó length check. 2. `not hash.startswith(('$2a$','$2b$','$2y$'))` → `True`. 3. Log error, retorna `False`. | `401`. |
| CB-13 | Core — `verify_password` | Caja Blanca — Cobertura de Decisiones | **Rama C:** flujo feliz — bcrypt.checkpw pasa | Hash bcrypt válido en BD | `{ "email": "sebastian.admin@bustoke.pe", "password": "TempPassword123!5" }` | 1. Todos los guards pasan. 2. `bcrypt.checkpw()` retorna `True`. | `200`. |

---

## 3. Pruebas Basadas en Riesgos

### Riesgo Crítico 1: Doble venta del mismo asiento en un viaje

**Impacto:** Pérdida económica directa por overbooking, dos pasajeros con el mismo asiento, insatisfacción del cliente, penalidades por incumplimiento.

| ID | Componente/Módulo | Tipo de Prueba | Descripción del Caso | Precondiciones | Datos de Entrada | Pasos de Ejecución | Resultado Esperado |
|---|---|---|---|---|---|---|---|
| RB-01 | Boletos — `create_boleto` (admin) | Basada en Riesgo | Solicitud concurrente de 2 compras para el mismo asiento en el mismo viaje | Viaje `id=1` existe, Asiento `id=10` está libre. Se envían 2 requests `POST /admin/viajes/boletos` simultáneos (race condition). Token Superadmin. | Request A: `{ "idViaje": 1, "idPasajero": 1, "idAsiento": 10, "canal": "app_bustoke", "codigoQr": "BKT-RACE-A", "precioFinal": 50.00 }` Request B: `{ "idViaje": 1, "idPasajero": 2, "idAsiento": 10, "canal": "app_bustoke", "codigoQr": "BKT-RACE-B", "precioFinal": 50.00 }` | 1. Disparar 2 requests en paralelo. 2. Sin `FOR UPDATE` ambos pasan la validación de asiento libre. 3. Ambos insertan. | **Riesgo:** Ambos `201` — 2 boletos para el mismo asiento. **Mitigación requerida:** Índice único compuesto `(id_viaje, id_asiento)` donde `estado = 'activo'` o bloqueo pesimista `SELECT ... FOR UPDATE`. |
| RB-02 | Público — `create_boleto_externo` | Basada en Riesgo | Venta de asiento liberado tras cancelación funciona correctamente | Asiento `id=5` ocupado por boleto `estado: "cancelado"` (antes activo, cancelado). API Key válida. | `{ "idViaje": 1, "idAsiento": 5, "emailContacto": "c@x.com", "precioFinal": 30.00, "pasajero": { ... "numeroDocumento": "99999999", ... } }` | 1. Cancelar boleto existente (estado → `cancelado`). 2. `POST /api/v1/boletos` para el mismo asiento. | `201`. **Válido.** La validación en `create_boleto_externo` (líneas 51-58) filtra por `Boleto.estado == "activo"`. El asiento cancelado se considera libre. |

### Riesgo Crítico 2: Acceso no autorizado a datos entre agencias

**Impacto:** Una agencia puede ver o modificar datos de otra agencia (violación de confidencialidad, incumplimiento Ley de Protección de Datos Personales Ley 29733 Perú).

| ID | Componente/Módulo | Tipo de Prueba | Descripción del Caso | Precondiciones | Datos de Entrada | Pasos de Ejecución | Resultado Esperado |
|---|---|---|---|---|---|---|---|
| RB-03 | Viajes — Listar | Basada en Riesgo | Admin de **Cruz del Sur** intenta acceder a viajes de **Oltursa** | Token JWT de `admin.cruz@cruzdelsur.com.pe` (id_agencia=1). Existen viajes para Oltursa (id_agencia=2). | `GET /admin/viajes?id_agencia=2` con token de Cruz del Sur | 1. Router: detecta `admin_agencia` con `id_agencia=1`. 2. **Sobrescribe** `id_agencia` con `1` (línea 41). 3. Llama a `get_viajes_by_agencia(db, 1, 0, 100)`. | `200`. **Protegido correctamente.** Solo retorna viajes de Cruz del Sur. El query param `?id_agencia=2` es ignorado. |
| RB-04 | Varios módulos | Basada en Riesgo | Admin de **Civa** lista boletos/pasajeros de otras agencias | Token de `admin.civa@civa.com.pe`. Existen boletos de todas las agencias. | `GET /admin/viajes/boletos/all` con token de Civa | 1. Depende de implementación: si `get_all_boletos` no filtra por agencia, Civa ve boletos de Cruz del Sur, Oltursa, Movil Bus. | **Riesgo alto si no hay filtro.** Verificar que `list_all_boletos` aplique filtro por JWT para rol `admin_agencia`. |
| RB-05 | Suscripciones/Planes | Basada en Riesgo | Admin de **Movil Bus** modifica plan de otra agencia | Token de `admin.movil@movilbus.com.pe`. | `PUT /admin/planes/{id_plan_de_otra_agencia}` | 1. Depende de autorización en service/router de suscripciones. | **Verificar** que el módulo de suscripciones valide que el plan pertenece a la agencia del token. |

### Riesgo Crítico 3: Token JWT compromise

**Impacto:** Un token robado permite acceso total a los recursos del usuario.

| ID | Componente/Módulo | Tipo de Prueba | Descripción del Caso | Precondiciones | Datos de Entrada | Pasos de Ejecución | Resultado Esperado |
|---|---|---|---|---|---|---|---|
| RB-06 | Auth | Basada en Riesgo | Reutilizar access token expirado | Access token de `sebastian.admin@bustoke.pe` con `exp` pasado (ej: modificado manualmente a fecha anterior) | Header: `Authorization: Bearer <token_expirado>` | 1. `GET /admin/viajes` con token expirado. 2. `decode_token()` → `JWTError` → `ValueError`. | `401 Unauthorized` con `{ "detail": "Token inválido o expirado" }`. |
| RB-07 | Auth | Basada en Riesgo | Token firmado con clave incorrecta | Token JWT firmado con otra `SECRET_KEY` | Header: `Authorization: Bearer <token_con_firma_invalida>` | 1. `GET /admin/viajes` con token mal firmado. | `401 Unauthorized`. Protegido por validación HMAC-SHA256. |

---

## Resumen de Hallazgos

| Ítem | Tipo | Severidad | Descripción |
|---|---|---|---|
| CN-30 | Defecto lógico | Media | No se valida que `fechaHoraLlegada > fechaHoraSalida` al crear viaje |
| CN-37 | Defecto funcional | Alta | `codigo_qr` unique constraint no manejada con `try-except`, causa `500` en lugar de `409 Conflict` |
| CN-35 | Defecto ausente | Baja | No hay validación de `precioFinal > 0` |
| RB-01 | Riesgo arquitectónico | **Crítica** | Race condition en venta de asientos: 2 requests concurrentes pueden vender el mismo asiento. Sin `FOR UPDATE` ni unique constraint compuesto. |
| RB-02 | Riesgo mitigado | Media | Cancelación libera asiento correctamente gracias a filtro por `estado == "activo"` |
| RB-03 | Control existente | — | Router de viajes protege correctamente el filtro por agencia (sobrescribe desde JWT) |
| RB-04 | Riesgo pendiente de verificar | **Alta** | Verificar que los routers de `boletos/all`, `pasajeros/all` y otros módulos (finanzas, suscripciones) apliquen el mismo filtro de `id_agencia` desde JWT para rol `admin_agencia` |
| RB-05 | Riesgo pendiente de verificar | Alta | Módulo de suscripciones requiere revisión de autorización por agencia |
| CB-04 | Defecto corregido | Media | `verify_password` maneja correctamente hashes corruptos (bcrypt inválido) — relacionado con `fix-pass.py` |

---

> **Documento generado a partir del análisis estático del código fuente.**
> Repositorio: `bustoke-admin-backend` — FastAPI + async SQLAlchemy 2.x + Pydantic v2 + PostgreSQL 15
> Credenciales de prueba referenciadas: `actividades/credenciales.md`

> **Usuarios de prueba disponibles:**
> - Superadmin: `sebastian.admin@bustoke.pe` / `TempPassword123!5`
> - Admin Cruz del Sur: `admin.cruz@cruzdelsur.com.pe` / `TempPassword123!1`
> - Admin Oltursa: `admin.oltursa@oltursa.com.pe` / `TempPassword123!2`
> - Admin Civa: `admin.civa@civa.com.pe` / `TempPassword123!3`
> - Admin Movil Bus: `admin.movil@movilbus.com.pe` / `TempPassword123!4`
