class WrongPassword(Exception):
    def __init__(self, message: str = "Wrong password") -> None:
        super().__init__()
        self.message = message
