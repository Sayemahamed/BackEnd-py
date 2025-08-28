class EmailAlreadyRegistered(Exception):
    def __init__(self, email: str,message: str="Email already exists") -> None:
        super().__init__()
        self.email = email
        self.message = message

class UserNotFound(Exception):
    def __init__(self, message: str="User not found") -> None:
        super().__init__()
        self.message = message

class UserAlreadyExists(Exception):
    def __init__(self,email:str, message: str="User already exists") -> None:
        super().__init__()
        self.email = email
        self.message = message