class NOSuchURL(Exception):
    def __init__(
        self, message: str = "No such URL found with corresponding short code"
    ) -> None:
        super().__init__()
        self.message = message
