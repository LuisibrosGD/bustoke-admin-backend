from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.core.logging import RequestLoggingMiddleware, setup_logging

# Routers
from app.modules.auth.router import router as auth_router
from app.modules.agencias.router import router as agencias_router
from app.modules.flota.router import router as flota_router
from app.modules.rutas.router import router as rutas_router
from app.modules.viajes.router import router as viajes_router
from app.modules.terminales.router import router as terminales_router
from app.modules.suscripciones.router import (
    plan_router,
    suscripcion_router as suscripciones_router,
)
from app.modules.soporte.router import router as soporte_router
from app.modules.reclamos.router import router as reclamos_router
from app.modules.finanzas.router import router as finanzas_router
from app.modules.reportes.router import router as reportes_router
from app.modules.ubigeo.router import router as ubigeo_router
from app.modules.boletos.router import router as boletos_router
from app.modules.pasajeros.router import router as pasajeros_router
from app.modules.agencias_terminales.router import router as agencias_terminales_router
from app.modules.choferes.router import router as choferes_router
from app.modules.public.router import router as public_router
from app.modules.manifiestos.router import router as manifiestos_router
from app.modules.dashboard.router import router as dashboard_router
from app.modules.notificaciones.router import router as notificaciones_router
from app.modules.search.router import router as search_router
from app.modules.usuarios.router import router as usuarios_router

@asynccontextmanager
async def lifespan(application: FastAPI):
    # El esquema (incluyendo la tabla `pagos` y el enum `metodo_pago`) se
    # gestiona con Alembic (ver alembic/versions/004_pagos_metodo_pago.py),
    # no en cada arranque del proceso: evita condiciones de carrera cuando
    # arrancan varios workers/réplicas a la vez.
    setup_logging()
    yield


app = FastAPI(
    title="Bustoke Admin API",
    version="1.0.0",
    description="Backend de administración para Bustoke",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── Middleware ────────────────────────────────────────────────────────────────
# El de logging se agrega primero para que envuelva a todos los demás y mida
# el tiempo total de cada request.
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth_router)
app.include_router(agencias_router)
app.include_router(flota_router)
app.include_router(rutas_router)
app.include_router(viajes_router)
app.include_router(terminales_router)
app.include_router(plan_router)
app.include_router(suscripciones_router)
app.include_router(soporte_router)
app.include_router(reclamos_router)
app.include_router(finanzas_router)
app.include_router(reportes_router)
app.include_router(ubigeo_router)
app.include_router(boletos_router)
app.include_router(pasajeros_router)
app.include_router(agencias_terminales_router)
app.include_router(choferes_router)
app.include_router(manifiestos_router)
app.include_router(public_router)
app.include_router(dashboard_router)
app.include_router(notificaciones_router)
app.include_router(search_router)
app.include_router(usuarios_router)


@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "app": "Bustoke Admin API", "version": "1.0.0"}


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy"}
