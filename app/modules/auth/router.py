from fastapi import APIRouter, Response

from app.dependencies import AdminOrSuper, CurrentUser, DbDep
from app.modules.auth import service
from app.modules.auth.schemas import (
    ForgotPasswordRequest,
    LoginRequest,
    RecoverEmailRequest,
    RefreshRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserOut,
)

router = APIRouter(prefix="/admin/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: DbDep):
    user = await service.authenticate_user(db, body.email, body.password)
    return service.build_token_response(user)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(body: RefreshRequest, db: DbDep):
    return await service.refresh_tokens(db, body.refresh_token)


@router.post("/logout")
async def logout(current_user: CurrentUser):
    # JWT es stateless; el cliente debe eliminar el token
    return {"message": "Sesión cerrada correctamente"}


@router.post("/logout-session")
async def logout_session(current_user: CurrentUser):
    # Logout de todas las sesiones (stateless — informacional)
    return {"message": "Todas las sesiones cerradas correctamente"}


@router.post("/forgot-password")
async def forgot_password(body: ForgotPasswordRequest, db: DbDep):
    return await service.forgot_password(db, body.email)


@router.post("/reset-password")
async def reset_password(body: ResetPasswordRequest, db: DbDep):
    return await service.reset_password(db, body.token, body.new_password)


@router.post("/recover-email")
async def recover_email(body: RecoverEmailRequest, db: DbDep):
    return await service.recover_email(db, body.email)


@router.get("/usuarios/{id_usuario}", response_model=UserOut)
async def get_usuario(id_usuario: int, db: DbDep, _: AdminOrSuper):
    return await service.get_usuario(db, id_usuario)
