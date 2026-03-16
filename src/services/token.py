class TokenUser:
    def __init__(self, payload):
        self.id = payload["sub"]
        self.name = payload["name"]
        self.rol = payload["role"]