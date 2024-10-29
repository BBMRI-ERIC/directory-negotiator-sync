class TokenExpiredException(Exception):
    def __init__(self, message="Impossible to perform the request, token expired"):
        self.message = message
        super().__init__(self.message)
