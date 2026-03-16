class TokenUser:
    def __init__(self, payload):
        self.id = int(payload["sub"])  # Convert back from string to int
        self.name = payload["name"]
        self.rol = payload["role"]