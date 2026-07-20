# fix_pass.py (versión con SQL directo)
import asyncio
import secrets
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, update

from app.config import settings
from app.modules.auth.models import Usuario
from app.core.security import get_password_hash


async def fix_corrupted_passwords():
    """Repara hashes de contraseñas corruptos usando SQL directo"""

    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        # Obtener solo los datos necesarios
        result = await db.execute(select(Usuario))
        users = result.scalars().all()

        if not users:
            print("❌ No se encontraron usuarios")
            await engine.dispose()
            return

        fixed_count = 0

        for user in users:
            # Validar el hash
            is_valid = (
                user.password_hash
                and len(user.password_hash) >= 50
                and user.password_hash.startswith(("$2a$", "$2b$", "$2y$"))
            )

            if not is_valid:
                print(f"⚠️  Usuario inválido: {user.email} (ID: {user.id_usuario})")
                print(
                    f"   Hash actual: {user.password_hash[:30] if user.password_hash else 'None'}..."
                )
                print(
                    f"   Longitud del hash: {len(user.password_hash) if user.password_hash else 0}"
                )

                # Generar una contraseña temporal aleatoria (no predecible)
                temp_password = secrets.token_urlsafe(12)
                new_hash = get_password_hash(temp_password)

                # UPDATE directo usando SQL
                stmt = (
                    update(Usuario)
                    .where(Usuario.id_usuario == user.id_usuario)
                    .values(password_hash=new_hash)
                )

                await db.execute(stmt)
                fixed_count += 1

                print(f"   ✅ Reparado con contraseña: {temp_password}\n")

        if fixed_count > 0:
            await db.commit()
            print(f"✅ Se repararon {fixed_count} usuario(s)")
            print("\n📝 Contraseñas temporales asignadas. Cambia en el próximo login.")
        else:
            print("✅ Todos los hashes son válidos")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(fix_corrupted_passwords())
