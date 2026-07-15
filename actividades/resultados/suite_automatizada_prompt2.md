# Suite de Pruebas Automatizadas — Bustoke Admin Backend

**Herramienta elegida:** Postman (API) + Cypress (API + UI)

> Basado en el código fuente del proyecto Bustoke Admin Backend (FastAPI + SQLAlchemy async + JWT Auth).

---

## 1. Postman Collection — Pruebas de API (Integration/E2E)

A continuación se presenta la colección de Postman exportable como JSON. Cubre un flujo completo CRUD sobre los endpoints principales del sistema.

### Colección: `Bustoke Admin API`

`json
{
  "info": {
    "name": "Bustoke Admin API",
    "description": "Suite de pruebas E2E para la API administrativa de Bustoke",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "auth": {
    "type": "bearer",
    "bearer": [
      {
        "key": "token",
        "value": "{{ACCESS_TOKEN}}",
        "type": "string"
      }
    ]
  },
  "variable": [
    { "key": "PORT", "value": "5000" },
    { "key": "BASE_URL", "value": "http://localhost:{{PORT}}" },
    { "key": "ACCESS_TOKEN", "value": "" },
    { "key": "REFRESH_TOKEN", "value": "" },
    { "key": "ID_AGENCIA", "value": "" },
    { "key": "ID_BUS", "value": "" },
    { "key": "ID_RUTA", "value": "" },
    { "key": "ID_VIAJE", "value": "" },
    { "key": "ID_BOLETO", "value": "" },
    { "key": "ID_PASAJERO", "value": "" },
    { "key": "ID_TERMINAL", "value": "" },
    { "key": "ID_CHOFER", "value": "" },
    { "key": "ID_TARIFA", "value": "" },
    { "key": "ID_RECLAMO", "value": "" },
    { "key": "ID_TICKET", "value": "" }
  ],
  "item": [
    {
      "name": "Auth",
      "item": [
        {
          "name": "Login (superadmin)",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status 200', () => pm.response.to.have.status(200));",
                  "pm.test('Response tiene accessToken', () => {",
                  "  const json = pm.response.json();",
                  "  pm.expect(json).to.have.property('accessToken');",
                  "  pm.expect(json).to.have.property('refreshToken');",
                  "  pm.expect(json).to.have.property('rol');",
                  "  pm.expect(json.rol).to.eql('superadmin');",
                  "  pm.collectionVariables.set('ACCESS_TOKEN', json.accessToken);",
                  "  pm.collectionVariables.set('REFRESH_TOKEN', json.refreshToken);",
                  "});"
                ]
              }
            }
          ],
          "request": {
            "method": "POST",
            "description": "Autenticación como superadministrador. Obtiene ACCESS_TOKEN y REFRESH_TOKEN.",
            "header": [
              { "key": "Content-Type", "value": "application/json" }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"email\": \"sebastian.admin@bustoke.pe\",\n  \"password\": \"TempPassword123!5\"\n}"
            },
            "url": {
              "raw": "{{BASE_URL}}/admin/auth/login",
              "host": ["{{BASE_URL}}"],
              "path": ["admin", "auth", "login"]
            }
          }
        },
        {
          "name": "Refresh Token",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status 200', () => pm.response.to.have.status(200));",
                  "pm.test('Nuevo accessToken retornado', () => {",
                  "  const json = pm.response.json();",
                  "  pm.expect(json).to.have.property('accessToken');",
                  "  pm.expect(json).to.have.property('refreshToken');",
                  "  pm.collectionVariables.set('ACCESS_TOKEN', json.accessToken);",
                  "  pm.collectionVariables.set('REFRESH_TOKEN', json.refreshToken);",
                  "});"
                ]
              }
            }
          ],
          "request": {
            "method": "POST",
            "description": "Renueva el ACCESS_TOKEN usando el REFRESH_TOKEN antes de que expire.",
            "header": [
              { "key": "Content-Type", "value": "application/json" }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"refreshToken\": \"{{REFRESH_TOKEN}}\"\n}"
            },
            "url": {
              "raw": "{{BASE_URL}}/admin/auth/refresh",
              "host": ["{{BASE_URL}}"],
              "path": ["admin", "auth", "refresh"]
            }
          }
        },
        {
          "name": "Login (admin_agencia)",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status 200', () => pm.response.to.have.status(200));",
                  "pm.test('Response tiene accessToken y rol admin_agencia', () => {",
                  "  const json = pm.response.json();",
                  "  pm.expect(json).to.have.property('accessToken');",
                  "  pm.expect(json).to.have.property('refreshToken');",
                  "  pm.expect(json).to.have.property('rol');",
                  "  pm.expect(json.rol).to.eql('admin_agencia');",
                  "  pm.expect(json).to.have.property('idAgencia');",
                  "  pm.collectionVariables.set('ACCESS_TOKEN', json.accessToken);",
                  "  pm.collectionVariables.set('REFRESH_TOKEN', json.refreshToken);",
                  "  pm.collectionVariables.set('ID_AGENCIA', json.idAgencia);",
                  "});"
                ]
              }
            }
          ],
          "request": {
            "method": "POST",
            "description": "Autenticación como administrador de agencia. Obtiene tokens y el ID_AGENCIA.",
            "header": [
              { "key": "Content-Type", "value": "application/json" }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"email\": \"admin.cruz@cruzdelsur.com.pe\",\n  \"password\": \"TempPassword123!1\"\n}"
            },
            "url": {
              "raw": "{{BASE_URL}}/admin/auth/login",
              "host": ["{{BASE_URL}}"],
              "path": ["admin", "auth", "login"]
            }
          }
        },
        {
          "name": "POST — Cerrar sesión",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status 200', () => pm.response.to.have.status(200));",
                  "pm.test('Sesión cerrada', () => {",
                  "  const json = pm.response.json();",
                  "  pm.expect(json).to.have.property('message', 'Sesión cerrada correctamente');",
                  "  pm.collectionVariables.unset('ACCESS_TOKEN');",
                  "  pm.collectionVariables.unset('REFRESH_TOKEN');",
                  "});"
                ]
              }
            }
          ],
          "request": {
            "method": "POST",
            "description": "Cierra la sesión actual. Limpia el ACCESS_TOKEN y REFRESH_TOKEN de las variables.",
            "header": [
              { "key": "Content-Type", "value": "application/json" }
            ],
            "body": {
              "mode": "raw",
              "raw": "{}"
            },
            "url": {
              "raw": "{{BASE_URL}}/admin/auth/logout",
              "host": ["{{BASE_URL}}"],
              "path": ["admin", "auth", "logout"]
            }
          }
        },
        {
          "name": "POST — Cerrar todas las sesiones",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status 200', () => pm.response.to.have.status(200));",
                  "pm.test('Sesiones cerradas', () => {",
                  "  const json = pm.response.json();",
                  "  pm.expect(json).to.have.property('message', 'Todas las sesiones cerradas correctamente');",
                  "  pm.collectionVariables.unset('ACCESS_TOKEN');",
                  "  pm.collectionVariables.unset('REFRESH_TOKEN');",
                  "});"
                ]
              }
            }
          ],
          "request": {
            "method": "POST",
            "description": "Cierra todas las sesiones (informativo). Limpia el ACCESS_TOKEN y REFRESH_TOKEN de las variables.",
            "header": [
              { "key": "Content-Type", "value": "application/json" }
            ],
            "body": {
              "mode": "raw",
              "raw": "{}"
            },
            "url": {
              "raw": "{{BASE_URL}}/admin/auth/logout-session",
              "host": ["{{BASE_URL}}"],
              "path": ["admin", "auth", "logout-session"]
            }
          }
        }
      ]
    },
    {
      "name": "Agencias",
      "item": [
        {
          "name": "GET — Listar agencias",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status 200', () => pm.response.to.have.status(200));",
                  "pm.test('Response es un array', () => {",
                  "  const json = pm.response.json();",
                  "  pm.expect(json).to.be.an('array');",
                  "  if (json.length > 0) {",
                  "    pm.expect(json[0]).to.have.property('idAgencia');",
                  "    pm.expect(json[0]).to.have.property('razonSocial');",
                  "    pm.expect(json[0]).to.have.property('ruc');",
                  "    pm.expect(json[0]).to.have.property('estado');",
                  "  }",
                  "});"
                ]
              }
            }
          ],
          "request": {
            "method": "GET",
            "description": "Obtiene todas las agencias (superadmin) o solo la propia (admin_agencia).",
            "url": {
              "raw": "{{BASE_URL}}/admin/agencias/",
              "host": ["{{BASE_URL}}"],
              "path": ["admin", "agencias", ""]
            }
          }
        },
        {
          "name": "POST — Crear agencia",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status 201', () => pm.response.to.have.status(201));",
                  "pm.test('Agencia creada con ID', () => {",
                  "  const json = pm.response.json();",
                  "  pm.expect(json).to.have.property('idAgencia');",
                  "  pm.expect(json).to.have.property('razonSocial', 'Agencia Test');",
                  "  pm.expect(json).to.have.property('ruc', '20123456789');",
                  "  pm.expect(json).to.have.property('estado', 'activa');",
                  "  pm.collectionVariables.set('ID_AGENCIA', json.idAgencia);",
                  "});"
                ]
              }
            }
          ],
          "request": {
            "method": "POST",
            "description": "Crea una nueva agencia. Solo superadmin.",
            "header": [
              { "key": "Content-Type", "value": "application/json" }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"razonSocial\": \"Agencia Test\",\n  \"ruc\": \"20123456789\",\n  \"direccion\": \"Av. Prueba 123\",\n  \"estado\": \"activa\"\n}"
            },
            "url": {
              "raw": "{{BASE_URL}}/admin/agencias/",
              "host": ["{{BASE_URL}}"],
              "path": ["admin", "agencias", ""]
            }
          }
        },
        {
          "name": "GET — Obtener agencia por ID",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status 200', () => pm.response.to.have.status(200));",
                  "pm.test('Estructura de agencia válida', () => {",
                  "  const json = pm.response.json();",
                  "  pm.expect(json).to.have.property('idAgencia');",
                  "  pm.expect(json).to.have.property('razonSocial');",
                  "  pm.expect(json).to.have.property('ruc');",
                  "  pm.expect(json.estado).to.match(/^(activa|suspendida)$/);",
                  "});"
                ]
              }
            }
          ],
          "request": {
            "method": "GET",
            "description": "Obtiene los datos de una agencia específica por su ID.",
            "url": {
              "raw": "{{BASE_URL}}/admin/agencias/{{ID_AGENCIA}}",
              "host": ["{{BASE_URL}}"],
              "path": ["admin", "agencias", "{{ID_AGENCIA}}"]
            }
          }
        },
        {
          "name": "PUT — Actualizar agencia",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status 200', () => pm.response.to.have.status(200));",
                  "pm.test('Datos actualizados', () => {",
                  "  const json = pm.response.json();",
                  "  pm.expect(json.razonSocial).to.eql('Agencia Test Modificada');",
                  "});"
                ]
              }
            }
          ],
          "request": {
            "method": "PUT",
            "description": "Actualiza los datos de una agencia existente. Solo superadmin.",
            "header": [
              { "key": "Content-Type", "value": "application/json" }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"razonSocial\": \"Agencia Test Modificada\"\n}"
            },
            "url": {
              "raw": "{{BASE_URL}}/admin/agencias/{{ID_AGENCIA}}",
              "host": ["{{BASE_URL}}"],
              "path": ["admin", "agencias", "{{ID_AGENCIA}}"]
            }
          }
        },
        {
          "name": "DELETE — Eliminar agencia",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status 204', () => pm.response.to.have.status(204));"
                ]
              }
            }
          ],
          "request": {
            "method": "DELETE",
            "description": "Elimina una agencia por ID. Solo superadmin.",
            "url": {
              "raw": "{{BASE_URL}}/admin/agencias/{{ID_AGENCIA}}",
              "host": ["{{BASE_URL}}"],
              "path": ["admin", "agencias", "{{ID_AGENCIA}}"]
            }
          }
        }
      ]
    },
    {
      "name": "Terminales",
      "item": [
        {
          "name": "GET — Listar terminales",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status 200', () => pm.response.to.have.status(200));",
                  "pm.test('Response es un array', () => {",
                  "  const json = pm.response.json();",
                  "  pm.expect(json).to.be.an('array');",
                  "  if (json.length > 0) {",
                  "    pm.expect(json[0]).to.have.property('idTerminal');",
                  "    pm.expect(json[0]).to.have.property('nombre');",
                  "    pm.expect(json[0]).to.have.property('direccion');",
                  "  }",
                  "});"
                ]
              }
            }
          ],
          "request": {
            "method": "GET",
            "description": "Obtiene el listado de terminales disponibles.",
            "url": {
              "raw": "{{BASE_URL}}/admin/terminales/",
              "host": ["{{BASE_URL}}"],
              "path": ["admin", "terminales", ""]
            }
          }
        },
        {
          "name": "POST — Crear terminal",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status 201', () => pm.response.to.have.status(201));",
                  "pm.test('Terminal creado', () => {",
                  "  const json = pm.response.json();",
                  "  pm.expect(json).to.have.property('idTerminal');",
                  "  pm.expect(json).to.have.property('nombre');",
                  "  pm.collectionVariables.set('ID_TERMINAL', json.idTerminal);",
                  "});"
                ]
              }
            }
          ],
          "request": {
            "method": "POST",
            "description": "Crea un nuevo terminal. Admin agencia lo asocia automáticamente.",
            "header": [
              { "key": "Content-Type", "value": "application/json" }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"nombre\": \"Terminal Test\",\n  \"direccion\": \"Av. Terminal 456\",\n  \"idDistrito\": 1\n}"
            },
            "url": {
              "raw": "{{BASE_URL}}/admin/terminales/",
              "host": ["{{BASE_URL}}"],
              "path": ["admin", "terminales", ""]
            }
          }
        },
        {
          "name": "GET — Obtener terminal por ID",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status 200', () => pm.response.to.have.status(200));",
                  "pm.test('Estructura TerminalOut válida', () => {",
                  "  const json = pm.response.json();",
                  "  pm.expect(json).to.have.property('idTerminal');",
                  "  pm.expect(json).to.have.property('nombre');",
                  "  pm.expect(json).to.have.property('direccion');",
                  "  pm.expect(json.idTerminal).to.eql(parseInt(pm.collectionVariables.get('ID_TERMINAL')));",
                  "});"
                ]
              }
            }
          ],
          "request": {
            "method": "GET",
            "description": "Obtiene los datos de un terminal específico por su ID.",
            "url": {
              "raw": "{{BASE_URL}}/admin/terminales/{{ID_TERMINAL}}",
              "host": ["{{BASE_URL}}"],
              "path": ["admin", "terminales", "{{ID_TERMINAL}}"]
            }
          }
        },
        {
          "name": "PUT — Actualizar terminal",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status 200', () => pm.response.to.have.status(200));",
                  "pm.test('Terminal actualizado', () => {",
                  "  const json = pm.response.json();",
                  "  pm.expect(json.nombre).to.eql('Terminal Modificado');",
                  "});"
                ]
              }
            }
          ],
          "request": {
            "method": "PUT",
            "description": "Actualiza los datos de un terminal existente.",
            "header": [
              { "key": "Content-Type", "value": "application/json" }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"nombre\": \"Terminal Modificado\"\n}"
            },
            "url": {
              "raw": "{{BASE_URL}}/admin/terminales/{{ID_TERMINAL}}",
              "host": ["{{BASE_URL}}"],
              "path": ["admin", "terminales", "{{ID_TERMINAL}}"]
            }
          }
        },
        {
          "name": "DELETE — Eliminar terminal",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status 204', () => pm.response.to.have.status(204));"
                ]
              }
            }
          ],
          "request": {
            "method": "DELETE",
            "description": "Elimina un terminal por ID.",
            "url": {
              "raw": "{{BASE_URL}}/admin/terminales/{{ID_TERMINAL}}",
              "host": ["{{BASE_URL}}"],
              "path": ["admin", "terminales", "{{ID_TERMINAL}}"]
            }
          }
        }
      ]
    },
    {
      "name": "Flota — Buses y Asientos",
      "item": [
        {
          "name": "POST — Crear bus",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status 201', () => pm.response.to.have.status(201));",
                  "pm.test('Bus creado con estructura válida', () => {",
                  "  const json = pm.response.json();",
                  "  pm.expect(json).to.have.property('idBus');",
                  "  pm.expect(json).to.have.property('placa');",
                  "  pm.expect(json).to.have.property('cantidadPisos');",
                  "  pm.expect(json.cantidadPisos).to.be.a('number');",
                  "  pm.collectionVariables.set('ID_BUS', json.idBus);",
                  "});"
                ]
              }
            }
          ],
          "request": {
            "method": "POST",
            "description": "Registra un nuevo bus en la flota de una agencia.",
            "header": [
              { "key": "Content-Type", "value": "application/json" }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"placa\": \"ABC-123\",\n  \"capacidad\": 40,\n  \"cantidadPisos\": 1,\n  \"idAgencia\": {{ID_AGENCIA}}\n}"
            },
            "url": {
              "raw": "{{BASE_URL}}/admin/flota/buses",
              "host": ["{{BASE_URL}}"],
              "path": ["admin", "flota", "buses"]
            }
          }
        },
        {
          "name": "GET — Listar buses",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status 200', () => pm.response.to.have.status(200));",
                  "pm.test('Response es array con estructura BusOut', () => {",
                  "  const json = pm.response.json();",
                  "  pm.expect(json).to.be.an('array');",
                  "  if (json.length > 0) {",
                  "    pm.expect(json[0]).to.have.property('idBus');",
                  "    pm.expect(json[0]).to.have.property('placa');",
                  "    pm.expect(json[0]).to.have.property('idAgencia');",
                  "    pm.expect(json[0]).to.have.property('cantidadPisos');",
                  "  }",
                  "});"
                ]
              }
            }
          ],
          "request": {
            "method": "GET",
            "description": "Obtiene el listado de buses registrados.",
            "url": {
              "raw": "{{BASE_URL}}/admin/flota/buses",
              "host": ["{{BASE_URL}}"],
              "path": ["admin", "flota", "buses"]
            }
          }
        },
        {
          "name": "GET — Asientos de un bus",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status 200', () => pm.response.to.have.status(200));",
                  "pm.test('Estructura de asientos', () => {",
                  "  const json = pm.response.json();",
                  "  pm.expect(json).to.be.an('array');",
                  "  if (json.length > 0) {",
                  "    pm.expect(json[0]).to.have.property('idAsiento');",
                  "    pm.expect(json[0]).to.have.property('numeroAsiento');",
                  "    pm.expect(json[0]).to.have.property('tipoServicio');",
                  "    pm.expect(json[0]).to.have.property('piso');",
                  "    pm.expect(json[0]).to.have.property('coordX');",
                  "    pm.expect(json[0]).to.have.property('coordY');",
                  "  }",
                  "});"
                ]
              }
            }
          ],
          "request": {
            "method": "GET",
            "description": "Obtiene el layout de asientos de un bus específico.",
            "url": {
              "raw": "{{BASE_URL}}/admin/flota/buses/{{ID_BUS}}/asientos",
              "host": ["{{BASE_URL}}"],
              "path": ["admin", "flota", "buses", "{{ID_BUS}}", "asientos"]
            }
          }
        }
      ]
    },
    {
      "name": "Rutas y Tarifas",
      "item": [
        {
          "name": "POST — Crear ruta",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status 201', () => pm.response.to.have.status(201));",
                  "pm.test('Ruta creada', () => {",
                  "  const json = pm.response.json();",
                  "  pm.expect(json).to.have.property('idRuta');",
                  "  pm.expect(json).to.have.property('idTerminalOrigen');",
                  "  pm.expect(json).to.have.property('idTerminalDestino');",
                  "  pm.expect(json).to.have.property('tarifaBase');",
                  "  pm.collectionVariables.set('ID_RUTA', json.idRuta);",
                  "});"
                ]
              }
            }
          ],
          "request": {
            "method": "POST",
            "description": "Crea una nueva ruta entre dos terminales.",
            "header": [
              { "key": "Content-Type", "value": "application/json" }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"idTerminalOrigen\": {{ID_TERMINAL}},\n  \"idTerminalDestino\": 2,\n  \"tarifaBase\": 50.00,\n  \"idAgencia\": {{ID_AGENCIA}}\n}"
            },
            "url": {
              "raw": "{{BASE_URL}}/admin/rutas/",
              "host": ["{{BASE_URL}}"],
              "path": ["admin", "rutas", ""]
            }
          }
        },
        {
          "name": "POST — Crear tarifa de ruta",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status 201', () => pm.response.to.have.status(201));",
                  "pm.test('Tarifa creada', () => {",
                  "  const json = pm.response.json();",
                  "  pm.expect(json).to.have.property('idTarifa');",
                  "  pm.expect(json).to.have.property('precio');",
                  "  pm.expect(json).to.have.property('tipoServicio');",
                  "});"
                ]
              }
            }
          ],
          "request": {
            "method": "POST",
            "description": "Agrega una tarifa por tipo de servicio a una ruta.",
            "header": [
              { "key": "Content-Type", "value": "application/json" }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"idRuta\": {{ID_RUTA}},\n  \"tipoServicio\": \"vip\",\n  \"precio\": 75.00\n}"
            },
            "url": {
              "raw": "{{BASE_URL}}/admin/rutas/tarifas",
              "host": ["{{BASE_URL}}"],
              "path": ["admin", "rutas", "tarifas"]
            }
          }
        }
      ]
    },
    {
      "name": "Choferes",
      "item": [
        {
          "name": "GET — Listar choferes",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status 200', () => pm.response.to.have.status(200));",
                  "pm.test('Response es un array de choferes', () => {",
                  "  const json = pm.response.json();",
                  "  pm.expect(json).to.be.an('array');",
                  "  if (json.length > 0) {",
                  "    pm.expect(json[0]).to.have.property('id');",
                  "    pm.expect(json[0]).to.have.property('nombres');",
                  "    pm.expect(json[0]).to.have.property('numeroDocumento');",
                  "  }",
                  "});"
                ]
              }
            }
          ],
          "request": {
            "method": "GET",
            "description": "Obtiene el listado de choferes (filtrable por id_agencia).",
            "url": {
              "raw": "{{BASE_URL}}/admin/choferes/",
              "host": ["{{BASE_URL}}"],
              "path": ["admin", "choferes", ""]
            }
          }
        },
        {
          "name": "POST — Crear chofer",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status 201', () => pm.response.to.have.status(201));",
                  "pm.test('Chofer creado', () => {",
                  "  const json = pm.response.json();",
                  "  pm.expect(json).to.have.property('id');",
                  "  pm.expect(json).to.have.property('nombres', 'Carlos');",
                  "  pm.expect(json).to.have.property('apellidoPaterno', 'Lopez');",
                  "  pm.expect(json).to.have.property('numeroDocumento', '12345678');",
                  "  pm.collectionVariables.set('ID_CHOFER', json.id);",
                  "});"
                ]
              }
            }
          ],
          "request": {
            "method": "POST",
            "description": "Registra un nuevo chofer en el sistema.",
            "header": [
              { "key": "Content-Type", "value": "application/json" }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"nombres\": \"Carlos\",\n  \"apellidoPaterno\": \"Lopez\",\n  \"apellidoMaterno\": \"Garcia\",\n  \"numeroDocumento\": \"12345678\",\n  \"idTipoDocumento\": 1,\n  \"activo\": true,\n  \"idAgencia\": {{ID_AGENCIA}}\n}"
            },
            "url": {
              "raw": "{{BASE_URL}}/admin/choferes/",
              "host": ["{{BASE_URL}}"],
              "path": ["admin", "choferes", ""]
            }
          }
        },
        {
          "name": "GET — Obtener chofer por ID",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status 200', () => pm.response.to.have.status(200));",
                  "pm.test('Estructura ChoferOut válida', () => {",
                  "  const json = pm.response.json();",
                  "  pm.expect(json).to.have.property('id');",
                  "  pm.expect(json).to.have.property('nombres');",
                  "  pm.expect(json).to.have.property('apellidoPaterno');",
                  "  pm.expect(json).to.have.property('numeroDocumento');",
                  "});"
                ]
              }
            }
          ],
          "request": {
            "method": "GET",
            "description": "Obtiene los detalles de un chofer específico por su ID.",
            "url": {
              "raw": "{{BASE_URL}}/admin/choferes/{{ID_CHOFER}}",
              "host": ["{{BASE_URL}}"],
              "path": ["admin", "choferes", "{{ID_CHOFER}}"]
            }
          }
        },
        {
          "name": "PUT — Actualizar chofer",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status 200', () => pm.response.to.have.status(200));",
                  "pm.test('Chofer actualizado', () => {",
                  "  const json = pm.response.json();",
                  "  pm.expect(json.nombres).to.eql('Carlos Updated');",
                  "});"
                ]
              }
            }
          ],
          "request": {
            "method": "PUT",
            "description": "Actualiza los datos de un chofer existente.",
            "header": [
              { "key": "Content-Type", "value": "application/json" }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"nombres\": \"Carlos Updated\"\n}"
            },
            "url": {
              "raw": "{{BASE_URL}}/admin/choferes/{{ID_CHOFER}}",
              "host": ["{{BASE_URL}}"],
              "path": ["admin", "choferes", "{{ID_CHOFER}}"]
            }
          }
        },
        {
          "name": "DELETE — Eliminar chofer",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status 200', () => pm.response.to.have.status(200));",
                  "pm.test('Mensaje de confirmación', () => {",
                  "  const json = pm.response.json();",
                  "  pm.expect(json.message).to.include('Chofer');",
                  "});"
                ]
              }
            }
          ],
          "request": {
            "method": "DELETE",
            "description": "Elimina un chofer por ID.",
            "url": {
              "raw": "{{BASE_URL}}/admin/choferes/{{ID_CHOFER}}",
              "host": ["{{BASE_URL}}"],
              "path": ["admin", "choferes", "{{ID_CHOFER}}"]
            }
          }
        }
      ]
    },
    {
      "name": "Viajes",
      "item": [
        {
          "name": "POST — Crear viaje",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status 201', () => pm.response.to.have.status(201));",
                  "pm.test('Viaje creado con estructura válida', () => {",
                  "  const json = pm.response.json();",
                  "  pm.expect(json).to.have.property('idViaje');",
                  "  pm.expect(json).to.have.property('idRuta');",
                  "  pm.expect(json).to.have.property('idBus');",
                  "  pm.expect(json).to.have.property('fechaHoraSalida');",
                  "  pm.expect(json).to.have.property('estado');",
                  "  pm.expect(json.estado).to.eql('programado');",
                  "  pm.collectionVariables.set('ID_VIAJE', json.idViaje);",
                  "});"
                ]
              }
            }
          ],
          "request": {
            "method": "POST",
            "description": "Programa un nuevo viaje con ruta, bus y chofer.",
            "header": [
              { "key": "Content-Type", "value": "application/json" }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"idRuta\": {{ID_RUTA}},\n  \"idBus\": {{ID_BUS}},\n  \"idChofer\": {{ID_CHOFER}},\n  \"fechaHoraSalida\": \"2026-07-10T08:00:00\",\n  \"fechaHoraLlegada\": \"2026-07-10T12:00:00\",\n  \"estado\": \"programado\"\n}"
            },
            "url": {
              "raw": "{{BASE_URL}}/admin/viajes/",
              "host": ["{{BASE_URL}}"],
              "path": ["admin", "viajes", ""]
            }
          }
        },
        {
          "name": "GET — Listar viajes",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status 200', () => pm.response.to.have.status(200));",
                  "pm.test('Array de viajes con estructura ViajeOut', () => {",
                  "  const json = pm.response.json();",
                  "  pm.expect(json).to.be.an('array');",
                  "  if (json.length > 0) {",
                  "    pm.expect(json[0]).to.have.property('idViaje');",
                  "    pm.expect(json[0]).to.have.property('idRuta');",
                  "    pm.expect(json[0]).to.have.property('idBus');",
                  "    pm.expect(json[0]).to.have.property('fechaHoraSalida');",
                  "    pm.expect(json[0]).to.have.property('estado');",
                  "  }",
                  "});"
                ]
              }
            }
          ],
          "request": {
            "method": "GET",
            "description": "Obtiene el listado de viajes programados.",
            "url": {
              "raw": "{{BASE_URL}}/admin/viajes/",
              "host": ["{{BASE_URL}}"],
              "path": ["admin", "viajes", ""]
            }
          }
        },
        {
          "name": "GET — Obtener viaje por ID",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status 200', () => pm.response.to.have.status(200));",
                  "pm.test('Estructura ViajeOut completa', () => {",
                  "  const json = pm.response.json();",
                  "  pm.expect(json).to.have.property('idViaje');",
                  "  pm.expect(json).to.have.property('idRuta');",
                  "  pm.expect(json).to.have.property('idBus');",
                  "  pm.expect(json).to.have.property('idChofer');",
                  "  pm.expect(json).to.have.property('fechaHoraSalida');",
                  "  pm.expect(json).to.have.property('fechaHoraLlegada');",
                  "  pm.expect(json).to.have.property('estado');",
                  "  pm.expect(json.idViaje).to.eql(parseInt(pm.collectionVariables.get('ID_VIAJE')));",
                  "});"
                ]
              }
            }
          ],
          "request": {
            "method": "GET",
            "description": "Obtiene los detalles de un viaje específico.",
            "url": {
              "raw": "{{BASE_URL}}/admin/viajes/{{ID_VIAJE}}",
              "host": ["{{BASE_URL}}"],
              "path": ["admin", "viajes", "{{ID_VIAJE}}"]
            }
          }
        },
        {
          "name": "PUT — Actualizar viaje",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status 200', () => pm.response.to.have.status(200));",
                  "pm.test('Viaje actualizado', () => {",
                  "  const json = pm.response.json();",
                  "  pm.expect(json.estado).to.eql('en_curso');",
                  "});"
                ]
              }
            }
          ],
          "request": {
            "method": "PUT",
            "description": "Actualiza el estado o datos de un viaje (ej: a en_curso).",
            "header": [
              { "key": "Content-Type", "value": "application/json" }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"estado\": \"en_curso\"\n}"
            },
            "url": {
              "raw": "{{BASE_URL}}/admin/viajes/{{ID_VIAJE}}",
              "host": ["{{BASE_URL}}"],
              "path": ["admin", "viajes", "{{ID_VIAJE}}"]
            }
          }
        }
      ]
    },
    {
      "name": "Boletos y Pasajeros",
      "item": [
        {
          "name": "POST — Crear pasajero",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status 201', () => pm.response.to.have.status(201));",
                  "pm.test('Pasajero creado', () => {",
                  "  const json = pm.response.json();",
                  "  pm.expect(json).to.have.property('idPasajero');",
                  "  pm.expect(json).to.have.property('nombres');",
                  "  pm.expect(json).to.have.property('numeroDocumento');",
                  "  pm.collectionVariables.set('ID_PASAJERO', json.idPasajero);",
                  "});"
                ]
              }
            }
          ],
          "request": {
            "method": "POST",
            "description": "Registra un nuevo pasajero en el sistema.",
            "header": [
              { "key": "Content-Type", "value": "application/json" }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"nombres\": \"Maria\",\n  \"apellidos\": \"Gonzalez\",\n  \"numeroDocumento\": \"87654321\",\n  \"idTipoDocumento\": 1,\n  \"fechaNacimiento\": \"1990-05-15\"\n}"
            },
            "url": {
              "raw": "{{BASE_URL}}/admin/viajes/pasajeros",
              "host": ["{{BASE_URL}}"],
              "path": ["admin", "viajes", "pasajeros"]
            }
          }
        },
        {
          "name": "POST — Crear boleto",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status 201', () => pm.response.to.have.status(201));",
                  "pm.test('Boleto creado con codigo QR', () => {",
                  "  const json = pm.response.json();",
                  "  pm.expect(json).to.have.property('idBoleto');",
                  "  pm.expect(json).to.have.property('codigoQr');",
                  "  pm.expect(json).to.have.property('precioFinal');",
                  "  pm.expect(json).to.have.property('estado');",
                  "  pm.expect(json.estado).to.eql('activo');",
                  "  pm.collectionVariables.set('ID_BOLETO', json.idBoleto);",
                  "});"
                ]
              }
            }
          ],
          "request": {
            "method": "POST",
            "description": "Emite un boleto para un viaje con asiento y pasajero.",
            "header": [
              { "key": "Content-Type", "value": "application/json" }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"idViaje\": {{ID_VIAJE}},\n  \"idPasajero\": {{ID_PASAJERO}},\n  \"idAsiento\": 1,\n  \"emailContacto\": \"maria@example.com\",\n  \"canal\": \"web\",\n  \"precioFinal\": 75.00,\n  \"aceptoTerminos\": true\n}"
            },
            "url": {
              "raw": "{{BASE_URL}}/admin/viajes/boletos",
              "host": ["{{BASE_URL}}"],
              "path": ["admin", "viajes", "boletos"]
            }
          }
        },
        {
          "name": "PUT — Check-in de boleto",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status 200', () => pm.response.to.have.status(200));",
                  "pm.test('Check-in exitoso', () => {",
                  "  const json = pm.response.json();",
                  "  pm.expect(json.estadoCheckin).to.eql('realizado');",
                  "  pm.expect(json.usado).to.eql(true);",
                  "});"
                ]
              }
            }
          ],
          "request": {
            "method": "PUT",
            "description": "Realiza el check-in de un boleto, marcándolo como usado.",
            "url": {
              "raw": "{{BASE_URL}}/admin/viajes/boletos/{{ID_BOLETO}}/check-in",
              "host": ["{{BASE_URL}}"],
              "path": ["admin", "viajes", "boletos", "{{ID_BOLETO}}", "check-in"]
            }
          }
        },
        {
          "name": "GET — Boletos de un viaje",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status 200', () => pm.response.to.have.status(200));",
                  "pm.test('Array de boletos con estructura BoletoOut', () => {",
                  "  const json = pm.response.json();",
                  "  pm.expect(json).to.be.an('array');",
                  "  if (json.length > 0) {",
                  "    pm.expect(json[0]).to.have.property('idBoleto');",
                  "    pm.expect(json[0]).to.have.property('codigoQr');",
                  "    pm.expect(json[0]).to.have.property('pasajero');",
                  "    pm.expect(json[0]).to.have.property('asiento');",
                  "  }",
                  "});"
                ]
              }
            }
          ],
          "request": {
            "method": "GET",
            "description": "Obtiene todos los boletos emitidos para un viaje.",
            "url": {
              "raw": "{{BASE_URL}}/admin/viajes/{{ID_VIAJE}}/boletos",
              "host": ["{{BASE_URL}}"],
              "path": ["admin", "viajes", "{{ID_VIAJE}}", "boletos"]
            }
          }
        },
        {
          "name": "DELETE — Eliminar boleto",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status 204', () => pm.response.to.have.status(204));"
                ]
              }
            }
          ],
          "request": {
            "method": "DELETE",
            "description": "Elimina un boleto por ID.",
            "url": {
              "raw": "{{BASE_URL}}/admin/viajes/boletos/{{ID_BOLETO}}",
              "host": ["{{BASE_URL}}"],
              "path": ["admin", "viajes", "boletos", "{{ID_BOLETO}}"]
            }
          }
        }
      ]
    },
    {
      "name": "Manifiestos",
      "item": [
        {
          "name": "GET — Listar manifiestos",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status 200', () => pm.response.to.have.status(200));",
                  "pm.test('Array de manifiestos', () => {",
                  "  const json = pm.response.json();",
                  "  pm.expect(json).to.be.an('array');",
                  "  if (json.length > 0) {",
                  "    pm.expect(json[0]).to.have.property('id');",
                  "    pm.expect(json[0]).to.have.property('idViaje');",
                  "    pm.expect(json[0]).to.have.property('estadoEnvio');",
                  "  }",
                  "});"
                ]
              }
            }
          ],
          "request": {
            "method": "GET",
            "description": "Obtiene el listado de manifiestos SUTRAN generados.",
            "url": {
              "raw": "{{BASE_URL}}/admin/manifiestos/",
              "host": ["{{BASE_URL}}"],
              "path": ["admin", "manifiestos", ""]
            }
          }
        },
        {
          "name": "GET — Obtener manifiesto por ID",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status 200', () => pm.response.to.have.status(200));",
                  "pm.test('Estructura ManifiestoDetalleOut', () => {",
                  "  const json = pm.response.json();",
                  "  pm.expect(json).to.have.property('id');",
                  "  pm.expect(json).to.have.property('idViaje');",
                  "  pm.expect(json).to.have.property('placaBus');",
                  "  pm.expect(json).to.have.property('rutaOrigen');",
                  "  pm.expect(json).to.have.property('rutaDestino');",
                  "});"
                ]
              }
            }
          ],
          "request": {
            "method": "GET",
            "description": "Obtiene el detalle completo de un manifiesto SUTRAN.",
            "url": {
              "raw": "{{BASE_URL}}/admin/manifiestos/1",
              "host": ["{{BASE_URL}}"],
              "path": ["admin", "manifiestos", "1"]
            }
          }
        }
      ]
    },
    {
      "name": "Pasajeros",
      "item": [
        {
          "name": "GET — Listar pasajeros",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status 200', () => pm.response.to.have.status(200));",
                  "pm.test('Array de pasajeros', () => {",
                  "  const json = pm.response.json();",
                  "  pm.expect(json).to.be.an('array');",
                  "  if (json.length > 0) {",
                  "    pm.expect(json[0]).to.have.property('id');",
                  "    pm.expect(json[0]).to.have.property('nombres');",
                  "    pm.expect(json[0]).to.have.property('numeroDocumento');",
                  "  }",
                  "});"
                ]
              }
            }
          ],
          "request": {
            "method": "GET",
            "description": "Obtiene el listado de pasajeros registrados en el sistema.",
            "url": {
              "raw": "{{BASE_URL}}/admin/pasajeros/",
              "host": ["{{BASE_URL}}"],
              "path": ["admin", "pasajeros", ""]
            }
          }
        },
        {
          "name": "POST — Crear pasajero",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status 201', () => pm.response.to.have.status(201));",
                  "pm.test('Pasajero creado', () => {",
                  "  const json = pm.response.json();",
                  "  pm.expect(json).to.have.property('id');",
                  "  pm.expect(json).to.have.property('nombres', 'Ana');",
                  "  pm.expect(json).to.have.property('numeroDocumento', '11122333');",
                  "  pm.collectionVariables.set('ID_PASAJERO', json.id);",
                  "});"
                ]
              }
            }
          ],
          "request": {
            "method": "POST",
            "description": "Registra un nuevo pasajero en el sistema.",
            "header": [
              { "key": "Content-Type", "value": "application/json" }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"nombres\": \"Ana\",\n  \"apellidoPaterno\": \"Maria\",\n  \"apellidoMaterno\": \"Lopez\",\n  \"numeroDocumento\": \"11122333\",\n  \"idTipoDocumento\": 1,\n  \"fechaNacimiento\": \"1995-08-20\"\n}"
            },
            "url": {
              "raw": "{{BASE_URL}}/admin/pasajeros/",
              "host": ["{{BASE_URL}}"],
              "path": ["admin", "pasajeros", ""]
            }
          }
        },
        {
          "name": "GET — Obtener pasajero por ID",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status 200', () => pm.response.to.have.status(200));",
                  "pm.test('Estructura PasajeroOut', () => {",
                  "  const json = pm.response.json();",
                  "  pm.expect(json).to.have.property('id');",
                  "  pm.expect(json).to.have.property('nombres');",
                  "  pm.expect(json).to.have.property('numeroDocumento');",
                  "  pm.expect(json).to.have.property('apellidoPaterno');",
                  "});"
                ]
              }
            }
          ],
          "request": {
            "method": "GET",
            "description": "Obtiene los datos de un pasajero por su ID.",
            "url": {
              "raw": "{{BASE_URL}}/admin/pasajeros/{{ID_PASAJERO}}",
              "host": ["{{BASE_URL}}"],
              "path": ["admin", "pasajeros", "{{ID_PASAJERO}}"]
            }
          }
        },
        {
          "name": "PUT — Actualizar pasajero",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status 200', () => pm.response.to.have.status(200));",
                  "pm.test('Pasajero actualizado', () => {",
                  "  const json = pm.response.json();",
                  "  pm.expect(json.nombres).to.eql('Ana Updated');",
                  "});"
                ]
              }
            }
          ],
          "request": {
            "method": "PUT",
            "description": "Actualiza los datos de un pasajero existente.",
            "header": [
              { "key": "Content-Type", "value": "application/json" }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"nombres\": \"Ana Updated\"\n}"
            },
            "url": {
              "raw": "{{BASE_URL}}/admin/pasajeros/{{ID_PASAJERO}}",
              "host": ["{{BASE_URL}}"],
              "path": ["admin", "pasajeros", "{{ID_PASAJERO}}"]
            }
          }
        },
        {
          "name": "DELETE — Eliminar pasajero",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status 200', () => pm.response.to.have.status(200));",
                  "pm.test('Mensaje de confirmación', () => {",
                  "  const json = pm.response.json();",
                  "  pm.expect(json.message).to.include('Pasajero');",
                  "});"
                ]
              }
            }
          ],
          "request": {
            "method": "DELETE",
            "description": "Elimina un pasajero por ID.",
            "url": {
              "raw": "{{BASE_URL}}/admin/pasajeros/{{ID_PASAJERO}}",
              "host": ["{{BASE_URL}}"],
              "path": ["admin", "pasajeros", "{{ID_PASAJERO}}"]
            }
          }
        }
      ]
    },
    {
      "name": "Reclamos",
      "item": [
        {
          "name": "GET — Listar reclamos",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status 200', () => pm.response.to.have.status(200));",
                  "pm.test('Array de reclamos', () => {",
                  "  const json = pm.response.json();",
                  "  pm.expect(json).to.be.an('array');",
                  "  if (json.length > 0) {",
                  "    pm.expect(json[0]).to.have.property('id');",
                  "    pm.expect(json[0]).to.have.property('motivo');",
                  "    pm.expect(json[0]).to.have.property('estado');",
                  "  }",
                  "});"
                ]
              }
            }
          ],
          "request": {
            "method": "GET",
            "description": "Obtiene el listado de reclamos (filtrable por id_agencia).",
            "url": {
              "raw": "{{BASE_URL}}/admin/reclamos/",
              "host": ["{{BASE_URL}}"],
              "path": ["admin", "reclamos", ""]
            }
          }
        },
        {
          "name": "POST — Crear reclamo",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status 201', () => pm.response.to.have.status(201));",
                  "pm.test('Reclamo creado', () => {",
                  "  const json = pm.response.json();",
                  "  pm.expect(json).to.have.property('id');",
                  "  pm.expect(json).to.have.property('motivo', 'Demora');",
                  "  pm.expect(json).to.have.property('estado', 'abierto');",
                  "  pm.collectionVariables.set('ID_RECLAMO', json.id);",
                  "});"
                ]
              }
            }
          ],
          "request": {
            "method": "POST",
            "description": "Registra un nuevo reclamo de un pasajero.",
            "header": [
              { "key": "Content-Type", "value": "application/json" }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"idUsuario\": 1,\n  \"idAgencia\": {{ID_AGENCIA}},\n  \"motivo\": \"Demora\",\n  \"detalle\": \"El viaje salio con 2 horas de retraso\",\n  \"estado\": \"abierto\"\n}"
            },
            "url": {
              "raw": "{{BASE_URL}}/admin/reclamos/",
              "host": ["{{BASE_URL}}"],
              "path": ["admin", "reclamos", ""]
            }
          }
        },
        {
          "name": "GET — Obtener reclamo por ID",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status 200', () => pm.response.to.have.status(200));",
                  "pm.test('Estructura ReclamoOut', () => {",
                  "  const json = pm.response.json();",
                  "  pm.expect(json).to.have.property('id');",
                  "  pm.expect(json).to.have.property('motivo');",
                  "  pm.expect(json).to.have.property('detalle');",
                  "  pm.expect(json).to.have.property('estado');",
                  "});"
                ]
              }
            }
          ],
          "request": {
            "method": "GET",
            "description": "Obtiene el detalle de un reclamo por ID.",
            "url": {
              "raw": "{{BASE_URL}}/admin/reclamos/{{ID_RECLAMO}}",
              "host": ["{{BASE_URL}}"],
              "path": ["admin", "reclamos", "{{ID_RECLAMO}}"]
            }
          }
        },
        {
          "name": "PUT — Actualizar reclamo",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status 200', () => pm.response.to.have.status(200));",
                  "pm.test('Reclamo actualizado', () => {",
                  "  const json = pm.response.json();",
                  "  pm.expect(json.estado).to.eql('resuelto');",
                  "});"
                ]
              }
            }
          ],
          "request": {
            "method": "PUT",
            "description": "Actualiza el estado o detalle de un reclamo.",
            "header": [
              { "key": "Content-Type", "value": "application/json" }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"estado\": \"resuelto\"\n}"
            },
            "url": {
              "raw": "{{BASE_URL}}/admin/reclamos/{{ID_RECLAMO}}",
              "host": ["{{BASE_URL}}"],
              "path": ["admin", "reclamos", "{{ID_RECLAMO}}"]
            }
          }
        },
        {
          "name": "DELETE — Eliminar reclamo",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status 200', () => pm.response.to.have.status(200));",
                  "pm.test('Mensaje de confirmación', () => {",
                  "  const json = pm.response.json();",
                  "  pm.expect(json.message).to.include('Reclamo');",
                  "});"
                ]
              }
            }
          ],
          "request": {
            "method": "DELETE",
            "description": "Elimina un reclamo por ID.",
            "url": {
              "raw": "{{BASE_URL}}/admin/reclamos/{{ID_RECLAMO}}",
              "host": ["{{BASE_URL}}"],
              "path": ["admin", "reclamos", "{{ID_RECLAMO}}"]
            }
          }
        },
        {
          "name": "GET — Mensajes de un reclamo",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status 200', () => pm.response.to.have.status(200));",
                  "pm.test('Array de mensajes', () => {",
                  "  const json = pm.response.json();",
                  "  pm.expect(json).to.be.an('array');",
                  "  if (json.length > 0) {",
                  "    pm.expect(json[0]).to.have.property('id');",
                  "    pm.expect(json[0]).to.have.property('textMensaje');",
                  "  }",
                  "});"
                ]
              }
            }
          ],
          "request": {
            "method": "GET",
            "description": "Obtiene los mensajes asociados a un reclamo.",
            "url": {
              "raw": "{{BASE_URL}}/admin/reclamos/{{ID_RECLAMO}}/mensajes",
              "host": ["{{BASE_URL}}"],
              "path": ["admin", "reclamos", "{{ID_RECLAMO}}", "mensajes"]
            }
          }
        },
        {
          "name": "POST — Crear mensaje en reclamo",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status 201', () => pm.response.to.have.status(201));",
                  "pm.test('Mensaje creado', () => {",
                  "  const json = pm.response.json();",
                  "  pm.expect(json).to.have.property('id');",
                  "  pm.expect(json).to.have.property('textMensaje');",
                  "});"
                ]
              }
            }
          ],
          "request": {
            "method": "POST",
            "description": "Agrega un mensaje a un reclamo existente.",
            "header": [
              { "key": "Content-Type", "value": "application/json" }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"idReclamo\": {{ID_RECLAMO}},\n  \"idUsuario\": 1,\n  \"textMensaje\": \"Estamos revisando su caso\"\n}"
            },
            "url": {
              "raw": "{{BASE_URL}}/admin/reclamos/{{ID_RECLAMO}}/mensajes",
              "host": ["{{BASE_URL}}"],
              "path": ["admin", "reclamos", "{{ID_RECLAMO}}", "mensajes"]
            }
          }
        }
      ]
    },
    {
      "name": "Soporte",
      "item": [
        {
          "name": "GET — Listar tickets",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status 200', () => pm.response.to.have.status(200));",
                  "pm.test('Array de tickets', () => {",
                  "  const json = pm.response.json();",
                  "  pm.expect(json).to.be.an('array');",
                  "  if (json.length > 0) {",
                  "    pm.expect(json[0]).to.have.property('id');",
                  "    pm.expect(json[0]).to.have.property('asunto');",
                  "    pm.expect(json[0]).to.have.property('estado');",
                  "  }",
                  "});"
                ]
              }
            }
          ],
          "request": {
            "method": "GET",
            "description": "Obtiene el listado de tickets de soporte (filtrable por id_agencia).",
            "url": {
              "raw": "{{BASE_URL}}/admin/soporte/",
              "host": ["{{BASE_URL}}"],
              "path": ["admin", "soporte", ""]
            }
          }
        },
        {
          "name": "POST — Crear ticket",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status 201', () => pm.response.to.have.status(201));",
                  "pm.test('Ticket creado', () => {",
                  "  const json = pm.response.json();",
                  "  pm.expect(json).to.have.property('id');",
                  "  pm.expect(json).to.have.property('asunto');",
                  "  pm.expect(json).to.have.property('estado', 'abierto');",
                  "  pm.collectionVariables.set('ID_TICKET', json.id);",
                  "});"
                ]
              }
            }
          ],
          "request": {
            "method": "POST",
            "description": "Crea un nuevo ticket de soporte técnico.",
            "header": [
              { "key": "Content-Type", "value": "application/json" }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"idAgencia\": {{ID_AGENCIA}},\n  \"asunto\": \"Problema con modulo de ventas\",\n  \"descripcion\": \"No se pueden emitir boletos desde la web\",\n  \"estado\": \"abierto\"\n}"
            },
            "url": {
              "raw": "{{BASE_URL}}/admin/soporte/",
              "host": ["{{BASE_URL}}"],
              "path": ["admin", "soporte", ""]
            }
          }
        },
        {
          "name": "GET — Obtener ticket por ID",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status 200', () => pm.response.to.have.status(200));",
                  "pm.test('Estructura TicketSoporteOut', () => {",
                  "  const json = pm.response.json();",
                  "  pm.expect(json).to.have.property('id');",
                  "  pm.expect(json).to.have.property('asunto');",
                  "  pm.expect(json).to.have.property('descripcion');",
                  "  pm.expect(json).to.have.property('estado');",
                  "});"
                ]
              }
            }
          ],
          "request": {
            "method": "GET",
            "description": "Obtiene el detalle de un ticket de soporte por ID.",
            "url": {
              "raw": "{{BASE_URL}}/admin/soporte/{{ID_TICKET}}",
              "host": ["{{BASE_URL}}"],
              "path": ["admin", "soporte", "{{ID_TICKET}}"]
            }
          }
        },
        {
          "name": "GET — Historial de cambios de ticket",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status 200', () => pm.response.to.have.status(200));",
                  "pm.test('Array de historial', () => {",
                  "  const json = pm.response.json();",
                  "  pm.expect(json).to.be.an('array');",
                  "  if (json.length > 0) {",
                  "    pm.expect(json[0]).to.have.property('campo');",
                  "    pm.expect(json[0]).to.have.property('valorNuevo');",
                  "  }",
                  "});"
                ]
              }
            }
          ],
          "request": {
            "method": "GET",
            "description": "Obtiene el historial de cambios de un ticket de soporte.",
            "url": {
              "raw": "{{BASE_URL}}/admin/soporte/{{ID_TICKET}}/historial",
              "host": ["{{BASE_URL}}"],
              "path": ["admin", "soporte", "{{ID_TICKET}}", "historial"]
            }
          }
        },
        {
          "name": "PUT — Actualizar ticket",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status 200', () => pm.response.to.have.status(200));",
                  "pm.test('Ticket actualizado', () => {",
                  "  const json = pm.response.json();",
                  "  pm.expect(json.estado).to.eql('en_progreso');",
                  "});"
                ]
              }
            }
          ],
          "request": {
            "method": "PUT",
            "description": "Actualiza el estado, asunto o descripción de un ticket.",
            "header": [
              { "key": "Content-Type", "value": "application/json" }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"estado\": \"en_progreso\"\n}"
            },
            "url": {
              "raw": "{{BASE_URL}}/admin/soporte/{{ID_TICKET}}",
              "host": ["{{BASE_URL}}"],
              "path": ["admin", "soporte", "{{ID_TICKET}}"]
            }
          }
        },
        {
          "name": "DELETE — Eliminar ticket",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status 200', () => pm.response.to.have.status(200));",
                  "pm.test('Mensaje de confirmación', () => {",
                  "  const json = pm.response.json();",
                  "  pm.expect(json.message).to.include('Ticket');",
                  "});"
                ]
              }
            }
          ],
          "request": {
            "method": "DELETE",
            "description": "Elimina un ticket de soporte por ID.",
            "url": {
              "raw": "{{BASE_URL}}/admin/soporte/{{ID_TICKET}}",
              "host": ["{{BASE_URL}}"],
              "path": ["admin", "soporte", "{{ID_TICKET}}"]
            }
          }
        }
      ]
    },
    {
      "name": "Reportes",
      "item": [
        {
          "name": "GET — Reporte por slug",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status 200', () => pm.response.to.have.status(200));",
                  "pm.test('Estructura ReporteGenericoOut', () => {",
                  "  const json = pm.response.json();",
                  "  pm.expect(json).to.have.property('slug');",
                  "  pm.expect(json).to.have.property('data');",
                  "  pm.expect(json).to.have.property('total');",
                  "  pm.expect(json.data).to.be.an('array');",
                  "});"
                ]
              }
            }
          ],
          "request": {
            "method": "GET",
            "description": "Obtiene datos de un reporte según el slug (ventas, viajes, manifiesto-sutran, financiero).",
            "url": {
              "raw": "{{BASE_URL}}/reports/ventas",
              "host": ["{{BASE_URL}}"],
              "path": ["reports", "ventas"]
            }
          }
        },
        {
          "name": "GET — Exportar reporte a Excel",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status 200', () => pm.response.to.have.status(200));",
                  "pm.test('Response es un archivo Excel', () => {",
                  "  pm.expect(pm.response.headers.get('content-type')).to.include('spreadsheet');",
                  "  pm.expect(pm.response.headers.get('content-disposition')).to.include('.xlsx');",
                  "});"
                ]
              }
            }
          ],
          "request": {
            "method": "GET",
            "description": "Descarga un reporte en formato Excel según el slug.",
            "url": {
              "raw": "{{BASE_URL}}/reports/ventas/export/excel",
              "host": ["{{BASE_URL}}"],
              "path": ["reports", "ventas", "export", "excel"]
            }
          }
        }
      ]
    },
    {
      "name": "Dashboard",
      "item": [
        {
          "name": "GET — Dashboard",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status 200', () => pm.response.to.have.status(200));",
                  "pm.test('Estructura DashboardOut', () => {",
                  "  const json = pm.response.json();",
                  "  pm.expect(json).to.have.property('kpis');",
                  "  pm.expect(json.kpis).to.have.property('totalViajes');",
                  "  pm.expect(json.kpis).to.have.property('totalBoletosVendidos');",
                  "  pm.expect(json.kpis).to.have.property('ingresosTotales');",
                  "  pm.expect(json).to.have.property('monthlyTrips');",
                  "  pm.expect(json).to.have.property('recentActivities');",
                  "  pm.expect(json).to.have.property('upcomingTrips');",
                  "  pm.expect(json).to.have.property('alerts');",
                  "});"
                ]
              }
            }
          ],
          "request": {
            "method": "GET",
            "description": "Obtiene KPIs, viajes mensuales, actividades recientes y alertas.",
            "url": {
              "raw": "{{BASE_URL}}/admin/dashboard/",
              "host": ["{{BASE_URL}}"],
              "path": ["admin", "dashboard", ""]
            }
          }
        }
      ]
    }
  ]
}
`
```

---

## 2. Cypress — Pruebas de API (Integration/E2E)

Archivo: `cypress/e2e/api/bustoke-api.cy.js`

```javascript
/// <reference types="cypress" />

const BASE_URL = 'http://localhost:5000';

let accessToken;
let refreshToken;
let idAgencia;
let idBus;
let idRuta;
let idViaje;
let idBoleto;
let idPasajero;
let idTerminal;
let idChofer;

describe('Bustoke Admin API — Flujo completo CRUD', () => {

  // ===================== AUTH =====================

  it('POST /admin/auth/login — Login como superadmin', () => {
    cy.request('POST', `${BASE_URL}/admin/auth/login`, {
      email: 'superadmin@bustoke.pe',
      password: 'admin123'
    }).then((res) => {
      expect(res.status).to.eq(200);
      expect(res.body).to.have.property('accessToken');
      expect(res.body).to.have.property('refreshToken');
      expect(res.body).to.have.property('rol');
      expect(res.body.rol).to.eq('superadmin');
      accessToken = res.body.accessToken;
      refreshToken = res.body.refreshToken;
    });
  });

  it('POST /admin/auth/refresh — Renovar token', () => {
    cy.request({
      method: 'POST',
      url: `${BASE_URL}/admin/auth/refresh`,
      body: { refreshToken },
      headers: { Authorization: `Bearer ${accessToken}` }
    }).then((res) => {
      expect(res.status).to.eq(200);
      expect(res.body).to.have.property('accessToken');
      accessToken = res.body.accessToken;
      refreshToken = res.body.refreshToken;
    });
  });

  // ===================== AGENCIAS =====================

  it('POST /admin/agencias/ — Crear agencia', () => {
    cy.request({
      method: 'POST',
      url: `${BASE_URL}/admin/agencias/`,
      headers: { Authorization: `Bearer ${accessToken}` },
      body: {
        razonSocial: 'Agencia Test Cypress',
        ruc: '20999999999',
        direccion: 'Av. Cypress 123',
        estado: 'activa'
      }
    }).then((res) => {
      expect(res.status).to.eq(201);
      expect(res.body).to.have.property('idAgencia');
      expect(res.body.razonSocial).to.eq('Agencia Test Cypress');
      idAgencia = res.body.idAgencia;
    });
  });

  it('GET /admin/agencias/ — Listar agencias', () => {
    cy.request({
      method: 'GET',
      url: `${BASE_URL}/admin/agencias/`,
      headers: { Authorization: `Bearer ${accessToken}` }
    }).then((res) => {
      expect(res.status).to.eq(200);
      expect(res.body).to.be.an('array');
      if (res.body.length > 0) {
        expect(res.body[0]).to.have.all.keys(
          'idAgencia', 'ruc', 'razonSocial', 'estado'
        );
      }
    });
  });

  it('GET /admin/agencias/:id — Obtener agencia por ID', () => {
    cy.request({
      method: 'GET',
      url: `${BASE_URL}/admin/agencias/${idAgencia}`,
      headers: { Authorization: `Bearer ${accessToken}` }
    }).then((res) => {
      expect(res.status).to.eq(200);
      expect(res.body.idAgencia).to.eq(idAgencia);
      expect(res.body.ruc).to.match(/^\d{11}$/);
    });
  });

  it('PUT /admin/agencias/:id — Actualizar agencia', () => {
    cy.request({
      method: 'PUT',
      url: `${BASE_URL}/admin/agencias/${idAgencia}`,
      headers: { Authorization: `Bearer ${accessToken}` },
      body: { razonSocial: 'Agencia Modificada' }
    }).then((res) => {
      expect(res.status).to.eq(200);
      expect(res.body.razonSocial).to.eq('Agencia Modificada');
    });
  });

  // ===================== TERMINALES =====================

  it('POST /admin/terminales/ — Crear terminal', () => {
    cy.request({
      method: 'POST',
      url: `${BASE_URL}/admin/terminales/`,
      headers: { Authorization: `Bearer ${accessToken}` },
      body: {
        nombre: 'Terminal Cypress',
        direccion: 'Av. Terminal 789',
        idDistrito: 1
      }
    }).then((res) => {
      expect(res.status).to.eq(201);
      expect(res.body).to.have.property('idTerminal');
      idTerminal = res.body.idTerminal;
    });
  });

  // ===================== BUSES =====================

  it('POST /admin/flota/buses — Crear bus', () => {
    cy.request({
      method: 'POST',
      url: `${BASE_URL}/admin/flota/buses`,
      headers: { Authorization: `Bearer ${accessToken}` },
      body: {
        placa: 'XYZ-999',
        cantidadPisos: 2,
        idAgencia
      }
    }).then((res) => {
      expect(res.status).to.eq(201);
      expect(res.body).to.have.property('idBus');
      expect(res.body.placa).to.eq('XYZ-999');
      expect(res.body.cantidadPisos).to.eq(2);
      idBus = res.body.idBus;
    });
  });

  it('GET /admin/flota/buses — Listar buses', () => {
    cy.request({
      method: 'GET',
      url: `${BASE_URL}/admin/flota/buses`,
      headers: { Authorization: `Bearer ${accessToken}` }
    }).then((res) => {
      expect(res.status).to.eq(200);
      expect(res.body).to.be.an('array');
    });
  });

  it('GET /admin/flota/buses/:id/asientos — Listar asientos del bus', () => {
    cy.request({
      method: 'GET',
      url: `${BASE_URL}/admin/flota/buses/${idBus}/asientos`,
      headers: { Authorization: `Bearer ${accessToken}` }
    }).then((res) => {
      expect(res.status).to.eq(200);
      expect(res.body).to.be.an('array');
      if (res.body.length > 0) {
        expect(res.body[0]).to.have.property('numeroAsiento');
        expect(res.body[0]).to.have.property('tipoServicio');
        expect(res.body[0]).to.have.property('piso');
      }
    });
  });

  // ===================== RUTAS =====================

  it('POST /admin/rutas/ — Crear ruta', () => {
    cy.request({
      method: 'POST',
      url: `${BASE_URL}/admin/rutas/`,
      headers: { Authorization: `Bearer ${accessToken}` },
      body: {
        idTerminalOrigen: idTerminal,
        idTerminalDestino: 2,
        tarifaBase: 50.00,
        idAgencia
      }
    }).then((res) => {
      expect(res.status).to.eq(201);
      expect(res.body).to.have.property('idRuta');
      idRuta = res.body.idRuta;
    });
  });

  it('POST /admin/rutas/tarifas — Crear tarifa', () => {
    cy.request({
      method: 'POST',
      url: `${BASE_URL}/admin/rutas/tarifas`,
      headers: { Authorization: `Bearer ${accessToken}` },
      body: {
        idRuta,
        tipoServicio: 'vip',
        precio: 75.00
      }
    }).then((res) => {
      expect(res.status).to.eq(201);
      expect(res.body).to.have.property('idTarifa');
      expect(res.body.precio).to.eq(75.00);
    });
  });

  // ===================== CHOFERES =====================

  it('POST /admin/choferes/ — Crear chofer', () => {
    cy.request({
      method: 'POST',
      url: `${BASE_URL}/admin/choferes/`,
      headers: { Authorization: `Bearer ${accessToken}` },
      body: {
        nombres: 'Pedro',
        apellidos: 'Ramirez',
        numeroDocumento: '99999999',
        idTipoDocumento: 1,
        activo: true,
        idAgencia
      }
    }).then((res) => {
      expect(res.status).to.eq(201);
      expect(res.body).to.have.property('idChofer');
      idChofer = res.body.idChofer;
    });
  });

  // ===================== VIAJES =====================

  it('POST /admin/viajes/ — Crear viaje', () => {
    cy.request({
      method: 'POST',
      url: `${BASE_URL}/admin/viajes/`,
      headers: { Authorization: `Bearer ${accessToken}` },
      body: {
        idRuta,
        idBus,
        idChofer,
        fechaHoraSalida: '2026-07-10T08:00:00',
        fechaHoraLlegada: '2026-07-10T12:00:00',
        estado: 'programado'
      }
    }).then((res) => {
      expect(res.status).to.eq(201);
      expect(res.body).to.have.property('idViaje');
      expect(res.body.estado).to.eq('programado');
      idViaje = res.body.idViaje;
    });
  });

  it('GET /admin/viajes/ — Listar viajes con filtros', () => {
    cy.request({
      method: 'GET',
      url: `${BASE_URL}/admin/viajes/?id_agencia=${idAgencia}`,
      headers: { Authorization: `Bearer ${accessToken}` }
    }).then((res) => {
      expect(res.status).to.eq(200);
      expect(res.body).to.be.an('array');
    });
  });

  it('GET /admin/viajes/:id — Obtener viaje por ID', () => {
    cy.request({
      method: 'GET',
      url: `${BASE_URL}/admin/viajes/${idViaje}`,
      headers: { Authorization: `Bearer ${accessToken}` }
    }).then((res) => {
      expect(res.status).to.eq(200);
      expect(res.body.idViaje).to.eq(idViaje);
      expect(res.body).to.have.property('idRuta');
      expect(res.body).to.have.property('idBus');
      expect(res.body).to.have.property('idChofer');
      expect(res.body).to.have.property('fechaHoraSalida');
      expect(res.body).to.have.property('estado');
    });
  });

  it('PUT /admin/viajes/:id — Actualizar viaje a en_curso', () => {
    cy.request({
      method: 'PUT',
      url: `${BASE_URL}/admin/viajes/${idViaje}`,
      headers: { Authorization: `Bearer ${accessToken}` },
      body: { estado: 'en_curso' }
    }).then((res) => {
      expect(res.status).to.eq(200);
      expect(res.body.estado).to.eq('en_curso');
    });
  });

  // ===================== PASAJEROS Y BOLETOS =====================

  it('POST /admin/viajes/pasajeros — Crear pasajero', () => {
    cy.request({
      method: 'POST',
      url: `${BASE_URL}/admin/viajes/pasajeros`,
      headers: { Authorization: `Bearer ${accessToken}` },
      body: {
        nombres: 'Lucia',
        apellidos: 'Fernandez',
        numeroDocumento: '77777777',
        idTipoDocumento: 1,
        fechaNacimiento: '1995-03-20'
      }
    }).then((res) => {
      expect(res.status).to.eq(201);
      expect(res.body).to.have.property('idPasajero');
      idPasajero = res.body.idPasajero;
    });
  });

  it('POST /admin/viajes/boletos — Crear boleto', () => {
    cy.request({
      method: 'POST',
      url: `${BASE_URL}/admin/viajes/boletos`,
      headers: { Authorization: `Bearer ${accessToken}` },
      body: {
        idViaje,
        idPasajero,
        idAsiento: 1,
        emailContacto: 'lucia@example.com',
        canal: 'web',
        precioFinal: 75.00,
        aceptoTerminos: true
      }
    }).then((res) => {
      expect(res.status).to.eq(201);
      expect(res.body).to.have.property('idBoleto');
      expect(res.body).to.have.property('codigoQr');
      expect(res.body.estado).to.eq('activo');
      idBoleto = res.body.idBoleto;
    });
  });

  it('GET /admin/viajes/:id/boletos — Boletos del viaje', () => {
    cy.request({
      method: 'GET',
      url: `${BASE_URL}/admin/viajes/${idViaje}/boletos`,
      headers: { Authorization: `Bearer ${accessToken}` }
    }).then((res) => {
      expect(res.status).to.eq(200);
      expect(res.body).to.be.an('array');
      expect(res.body.length).to.be.at.least(1);
    });
  });

  it('PUT /admin/viajes/boletos/:id/check-in — Check-in de boleto', () => {
    cy.request({
      method: 'PUT',
      url: `${BASE_URL}/admin/viajes/boletos/${idBoleto}/check-in`,
      headers: { Authorization: `Bearer ${accessToken}` }
    }).then((res) => {
      expect(res.status).to.eq(200);
      expect(res.body.estadoCheckin).to.eq('realizado');
      expect(res.body.usado).to.eq(true);
    });
  });

  // ===================== CLEANUP =====================

  it('DELETE /admin/viajes/boletos/:id — Eliminar boleto', () => {
    cy.request({
      method: 'DELETE',
      url: `${BASE_URL}/admin/viajes/boletos/${idBoleto}`,
      headers: { Authorization: `Bearer ${accessToken}` }
    }).then((res) => {
      expect(res.status).to.eq(204);
    });
  });

  it('DELETE /admin/agencias/:id — Eliminar agencia (cleanup)', () => {
    cy.request({
      method: 'DELETE',
      url: `${BASE_URL}/admin/agencias/${idAgencia}`,
      headers: { Authorization: `Bearer ${accessToken}` }
    }).then((res) => {
      expect(res.status).to.eq(204);
    });
  });
});
```

---

## 3. Cypress — Pruebas de Interfaz UI (E2E)

Archivo: `cypress/e2e/ui/flujo-autenticacion.cy.js`

```javascript
/// <reference types="cypress" />

describe('Flujo de Autenticación — Login y Navegación', () => {

  beforeEach(() => {
    cy.visit('http://localhost:3000/login'); // URL del frontend
  });

  it('Muestra el formulario de login correctamente', () => {
    // Verificar que los elementos del formulario existen
    cy.get('input[type="email"]').should('be.visible');
    cy.get('input[type="password"]').should('be.visible');
    cy.get('button[type="submit"]').should('contain.text', 'Iniciar Sesión');
  });

  it('Login exitoso redirige al dashboard', () => {
    // Interceptar la petición de login
    cy.intercept('POST', 'http://localhost:5000/admin/auth/login').as('loginRequest');

    // Llenar credenciales y enviar
    cy.get('input[type="email"]').type('admin@bustoke.pe');
    cy.get('input[type="password"]').type('password123');
    cy.get('button[type="submit"]').click();

    // Esperar respuesta de la API
    cy.wait('@loginRequest').then((interception) => {
      expect(interception.response.statusCode).to.eq(200);
      expect(interception.response.body).to.have.property('accessToken');
    });

    // Verificar redirección al dashboard
    cy.url().should('include', '/dashboard');
    cy.contains('Dashboard').should('be.visible');
  });

  it('Login con credenciales inválidas muestra error', () => {
    cy.intercept('POST', 'http://localhost:5000/admin/auth/login').as('loginRequest');

    cy.get('input[type="email"]').type('invalido@bustoke.pe');
    cy.get('input[type="password"]').type('wrongpass');
    cy.get('button[type="submit"]').click();

    cy.wait('@loginRequest');

    // Verificar que se muestra mensaje de error
    cy.get('[data-testid="error-message"]')
      .should('be.visible')
      .and('contain.text', 'Credenciales inválidas');
  });

  it('Cierre de sesión funciona correctamente', () => {
    // Login primero
    cy.login('admin@bustoke.pe', 'password123'); // Comando custom

    cy.url().should('include', '/dashboard');

    // Click en botón de cerrar sesión
    cy.get('[data-testid="logout-button"]').click();

    // Confirmar redirección al login
    cy.url().should('include', '/login');
    cy.get('input[type="email"]').should('be.visible');
  });

  it('Redirección al login si no hay token', () => {
    // Intentar acceder al dashboard sin autenticación
    cy.visit('http://localhost:3000/dashboard');

    // Verificar redirección a login
    cy.url().should('include', '/login');
    cy.get('input[type="email"]').should('be.visible');
  });
});
```

Archivo: `cypress/e2e/ui/flujo-creacion-viaje.cy.js`

```javascript
/// <reference types="cypress" />

describe('Flujo Crítico — Creación de Viaje', () => {

  beforeEach(() => {
    cy.login('admin@bustoke.pe', 'password123');
    cy.visit('http://localhost:3000/viajes');
  });

  it('Crear un nuevo viaje exitosamente', () => {
    // Interceptar peticiones
    cy.intercept('POST', 'http://localhost:5000/admin/viajes/').as('createViaje');
    cy.intercept('GET', 'http://localhost:5000/admin/viajes/').as('listViajes');

    // Hacer clic en botón "Nuevo Viaje"
    cy.get('[data-testid="nuevo-viaje-btn"]').click();

    // Verificar que el modal/formulario se abre
    cy.get('[data-testid="viaje-form"]').should('be.visible');

    // Seleccionar ruta
    cy.get('[data-testid="select-ruta"]').click();
    cy.get('[data-testid="select-ruta"]').find('option').first().then(($opt) => {
      const rutaId = $opt.val();
      cy.get('[data-testid="select-ruta"]').select(rutaId);
    });

    // Seleccionar bus
    cy.get('[data-testid="select-bus"]').click();
    cy.get('[data-testid="select-bus"]').find('option').first().then(($opt) => {
      cy.get('[data-testid="select-bus"]').select($opt.val());
    });

    // Seleccionar chofer
    cy.get('[data-testid="select-chofer"]').click();
    cy.get('[data-testid="select-chofer"]').find('option').first().then(($opt) => {
      cy.get('[data-testid="select-chofer"]').select($opt.val());
    });

    // Completar fecha y hora de salida
    cy.get('[data-testid="input-fecha-salida"]').type('2026-07-15T14:00:00');

    // Completar fecha y hora de llegada
    cy.get('[data-testid="input-fecha-llegada"]').type('2026-07-15T18:30:00');

    // Seleccionar estado
    cy.get('[data-testid="select-estado"]').select('programado');

    // Enviar formulario
    cy.get('[data-testid="submit-viaje-btn"]').click();

    // Esperar respuesta de creación
    cy.wait('@createViaje').then((interception) => {
      expect(interception.response.statusCode).to.eq(201);
      expect(interception.response.body).to.have.property('idViaje');
    });

    // Verificar que el viaje aparece en la tabla
    cy.wait('@listViajes');
    cy.get('[data-testid="tabla-viajes"]').should('contain.text', 'programado');
  });

  it('Validación: campos requeridos en formulario de viaje', () => {
    cy.get('[data-testid="nuevo-viaje-btn"]').click();
    cy.get('[data-testid="submit-viaje-btn"]').click();

    // Verificar mensajes de validación
    cy.get('[data-testid="select-ruta"]:invalid').should('exist');
    cy.get('[data-testid="select-bus"]:invalid').should('exist');
  });
});
```

---

## Instrucciones de Ejecución

### Postman
1. Abrir Postman → **Import** → seleccionar el JSON de la colección.
2. Ejecutar **Login** para obtener el token automáticamente.
3. Ejecutar la colección en orden (las variables se auto-almacenan).

### Cypress
1. Instalar Cypress en el proyecto:
   ```bash
   npm install cypress --save-dev
   ```
2. Copiar los archivos `.cy.js` en `cypress/e2e/`.
3. Ejecutar en modo interactivo:
   ```bash
   npx cypress open
   ```
4. O en modo headless:
   ```bash
   npx cypress run
   ```

> **Nota:** Los valores de credenciales y payloads deben ajustarse a los datos reales de la base de datos de cada entorno.
