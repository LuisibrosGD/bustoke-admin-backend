import time
from collections import defaultdict, deque

from fastapi import status
from fastapi.exceptions import HTTPException

# Ventana deslizante en memoria por clave. NOTA: esto es por-proceso; con
# varios workers/réplicas cada uno lleva su propia cuenta. Para un límite
# global compartido habría que respaldarlo en Redis — suficiente para frenar
# fuerza bruta básica en un despliegue de una sola instancia, que es el caso
# de esta etapa. Documentado como limitación conocida, no como bug.
_hits: dict[str, deque[float]] = defaultdict(deque)


class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    def check(self, key: str) -> None:
        """Registra un intento para `key` y lanza 429 si excede el límite en la
        ventana. Se llama explícitamente desde el endpoint con la clave correcta
        (p. ej. el email en login) en vez de la IP: el login pasa por el proxy
        BFF de Next.js, así que la IP de origen es siempre la misma y no sirve
        para distinguir usuarios — el email sí identifica la cuenta atacada."""
        now = time.monotonic()
        window_start = now - self.window_seconds

        bucket = _hits[key]
        while bucket and bucket[0] < window_start:
            bucket.popleft()

        if len(bucket) >= self.max_requests:
            retry_after = int(self.window_seconds - (now - bucket[0])) + 1
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Demasiados intentos. Intenta de nuevo en unos momentos.",
                headers={"Retry-After": str(retry_after)},
            )

        bucket.append(now)


# Límite pensado para login: frena fuerza bruta de contraseñas contra una cuenta
# sin molestar el uso legítimo (un usuario real no falla ~10 logins por minuto).
login_rate_limit = RateLimiter(max_requests=10, window_seconds=60)
