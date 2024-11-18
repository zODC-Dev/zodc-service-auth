class CreateUserPayload:
    email: str
    password: str
    full_name: str

    def __init__(self, email: str, password: str, full_name: str):
        self.email = email
        self.password = password
        self.full_name = full_name

class CreateUserPayloadSSO:
    email: str
    full_name: str
    microsoft_id: str

    def __init__(self, email: str, full_name: str, microsoft_id: str):
        self.email = email
        self.full_name = full_name
        self.microsoft_id = microsoft_id
