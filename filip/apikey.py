import random
import string


class Apikey:
    """
    This class holds the API key needed for service registration. If no other
    key is provides the possibility to create a random key.

    NOTE: It does not check if the key is maybe used by other services.

    """
    def __init__(self, key=''):
        self.key = key

    def generate_key(self, length: int = 10):
        self.key = ''.join(random.choice(
                string.ascii_lowercase+string.digits) for _ in range(
                length))
        return self.key






