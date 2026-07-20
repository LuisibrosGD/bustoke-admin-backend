import logging
import sys
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger("bustoke")


def setup_logging(level: int = logging.INFO) -> None:
    """Configura el logger raíz de la app con un formato legible y consistente.
    Idempotente: si ya hay handlers configurados, no duplica."""
    root = logging.getLogger("bustoke")
    if root.handlers:
        return
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    root.addHandler(handler)
    root.setLevel(level)
    root.propagate = False


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Registra cada request HTTP con método, ruta, código de estado, duración
    en ms y la IP del cliente. Un 5xx se registra como ERROR para que salte a
    la vista en los logs de producción."""

    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        client_ip = request.client.host if request.client else "-"
        try:
            response = await call_next(request)
        except Exception:
            elapsed_ms = (time.perf_counter() - start) * 1000
            logger.exception(
                "%s %s -> 500 (%.1fms) ip=%s", request.method, request.url.path, elapsed_ms, client_ip
            )
            raise

        elapsed_ms = (time.perf_counter() - start) * 1000
        log = logger.error if response.status_code >= 500 else (
            logger.warning if response.status_code >= 400 else logger.info
        )
        log(
            "%s %s -> %d (%.1fms) ip=%s",
            request.method,
            request.url.path,
            response.status_code,
            elapsed_ms,
            client_ip,
        )
        return response
