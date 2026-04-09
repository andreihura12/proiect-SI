from cryptography.fernet import Fernet

class AESHandler:
    @staticmethod
    def generate_key():
        return Fernet.generate_key()

    def __init__(self, key):
        self.cipher = Fernet(key)

    def encrypt(self, data: str) -> str:

        return self.cipher.encrypt(data.encode()).decode()

    def decrypt(self, encrypted_data: str) -> str:

        return self.cipher.decrypt(encrypted_data.encode()).decode()