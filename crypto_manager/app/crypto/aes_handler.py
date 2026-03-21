from cryptography.fernet import Fernet

class AESHandler:
    @staticmethod
    def generate_key():
        return Fernet.generate_key()

    def __init__(self, key):
        self.cipher = Fernet(key)

    def encrypt(self, data: str) -> str:
        # Transformă textul în bytes, îl criptează și returnează string
        return self.cipher.encrypt(data.encode()).decode()

    def decrypt(self, encrypted_data: str) -> str:
        # Decriptează și transformă înapoi în text clar
        return self.cipher.decrypt(encrypted_data.encode()).decode()