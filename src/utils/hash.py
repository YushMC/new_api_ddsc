from passlib.context import CryptContext

class HASH_DATA:
    def __init__(self) -> None:
        self.__pwd_context =CryptContext(schemes=["bcrypt"])

    def hash_string(self, password: str)->str:
        return self.__pwd_context.hash(password)

    def verify_password(self, password: str, hashed: str)->bool:
        return self.__pwd_context.verify(password, hashed)