from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from src.services.token import TokenUser
from src.utils.jwt import JWT_TOKEN

__oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(__oauth2_scheme)):
    jwt = JWT_TOKEN()
    payload = jwt.decode_token(token=token)
    return TokenUser(payload)