

class ConnectionAlreadyAcquiredError(Exception):
    """Raised when a connection is requested but the previous connection is not put back in the pool"""
    pass