class OpenHumansError(Exception):
    """Base class for exceptions in the openhumans module."""
    pass


class OpenHumansAPIResponseError(OpenHumansError):
    """Error or unexpected response from Open Humans API"""
    pass
