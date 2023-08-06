class KeyNotFound(Exception):
    """raise this when a key is not found"""


class ErrorFetchingRandom(Exception):
    """raise this when unable to fetch random bytes"""


class KeyNotCreated(Exception):
    """raise this when a key could not be created"""


class KeyNotDeleted(Exception):
    """raise this when a key could not be deleted"""


class ErrorFetchingKey(Exception):
    """raise this when an unknown error occurs while creating or getting a key"""


class KeyAlreadyExists(Exception):
    """raise this when a create key request is made for the key that already exists"""


class AccountNotFound(Exception):
    """raise this when an account is not found"""

class InvalidKeyType(Exception):
    """raise this when encryption or decryption tries to use an FPE key"""

class HideRequestFailed(Exception):
    """raise this when a FPE hide request fails"""

class UnhideRequestFailed(Exception):
    """raise this when a FPE unhide request fails"""
