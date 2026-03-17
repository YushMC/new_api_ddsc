from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from src.services.token import TokenUser
from src.utils.jwt import JWT_TOKEN
from src.models.enums import UserRolEnum

__oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(__oauth2_scheme)):
    jwt = JWT_TOKEN()
    payload = jwt.decode_token(token=token)
    return TokenUser(payload)

def verify_admin_role(user: TokenUser = Depends(get_current_user)):
    """Verify that the user has OWNER or EDITOR role"""
    if user.rol not in (UserRolEnum.OWNER, UserRolEnum.EDITOR):
        raise HTTPException(status_code=403, detail="Solo administradores pueden acceder a esta ruta")
    return user
