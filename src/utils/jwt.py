from jose import jwt, JWTError
from datetime import datetime, timedelta, UTC
import os
from fastapi import HTTPException
from src.conf.all_keys import SESSION_KEYS

class JWT_TOKEN:
    def __init__(self) -> None:
        self.__KEY = os.getenv(SESSION_KEYS.JWT_KEY)
        self.__ALGO = os.getenv(SESSION_KEYS.ALGORITHM)
        if self.__KEY is None:
            raise ValueError("JWT key environment variable is not set.")
        if self.__ALGO is None:
            raise ValueError("JWT algorithm environment variable is not set.")

    def create_token(self, user):
        payload = {
            "sub": str(user.id),  # JWT spec requires 'sub' to be a string
            "name": user.name,
            "role": user.role,
            "logo": user.logo,
            "about_me": user.about_me,
            "exp": datetime.now(UTC) + timedelta(hours=48)
        }

        return jwt.encode(payload, self.__KEY, algorithm=self.__ALGO) # type: ignore
    
    def decode_token(self,token: str):
        try:
            return jwt.decode(token, self.__KEY, algorithms=[self.__ALGO])# type: ignore
        except JWTError:
            raise HTTPException(status_code=401, detail="Token inválido")

    