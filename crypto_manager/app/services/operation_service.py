import time
from ..crypto.openssl_handler import OpenSSLHandler
from ..crypto.aes_handler import AESHandler
from ..crypto.rsa_handler import RSAHandler


class OperationService:

    def __init__(self):
        self.openssl_handler = OpenSSLHandler()
        self.aes_handler = AESHandler()
        self.rsa_handler = RSAHandler()

    def encrypt_file(self, file_path, output_path, algorithm, framework):

        start_time = time.time()

        if framework == "OpenSSL":

            if algorithm == "AES":
                self.openssl_handler.encrypt_aes(file_path, output_path)

            elif algorithm == "RSA":
                self.openssl_handler.encrypt_rsa(file_path, output_path)

        elif framework == "PyCryptodome":

            if algorithm == "AES":
                self.aes_handler.encrypt(file_path, output_path)

            elif algorithm == "RSA":
                self.rsa_handler.encrypt(file_path, output_path)

        end_time = time.time()

        execution_time = end_time - start_time

        return execution_time