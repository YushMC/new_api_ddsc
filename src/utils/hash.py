import bcrypt

class HASH_DATA:
    def __init__(self) -> None:
        self.rounds = 12  # bcrypt rounds for hashing

    def hash_string(self, password: str) -> str:
        """Hash a password using bcrypt"""
        # Truncate password to 72 bytes if necessary (bcrypt limitation)
        password_bytes = password.encode('utf-8')[:72]
        salt = bcrypt.gensalt(rounds=self.rounds)
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')

    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify a password against its hash"""
        try:
            # Truncate password to 72 bytes if necessary
            password_bytes = password.encode('utf-8')[:72]
            hashed_bytes = hashed.encode('utf-8')
            return bcrypt.checkpw(password_bytes, hashed_bytes)
        except Exception as e:
            print(f"Error verifying password: {e}")
            return False