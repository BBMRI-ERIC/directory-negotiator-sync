class TokenExpiredException(Exception):
    """
    Class defining a custom exception raised when a token is expired.
    """
    def __init__(self, message="Impossible to perform the request, token expired"):
        self.message = message
        super().__init__(self.message)


class NegotiatorAPIException(Exception):
    """
    Class defining a custom exception raised when a Negotiator API fails.
    """
    def __init__(self,
                 message="Error occurred while trying to perform a POST/PUT/PATCH to the Negotiator API for resources synchronization"):
        self.message = message
        super().__init__(self.message)


class DirectoryAPIException(Exception):
    """
    Class defining a custom exception raised when a Directory API fails.
    """
    def __init__(self,
                 message="Error occurred while trying to get biobanks/collections/networks/services from the Directory API"):
        self.message = message
        super().__init__(self.message)
