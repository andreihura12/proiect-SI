import subprocess

class OpenSSLHandler:
    def encrypt_aes(self,input_path,output_path,password):
        command = [
            "openssl", "enc", "-aes-256-cbc",
            "-salt",
            "-in", input_path,
            "-out", output_path,
            "-pass", f"pass:{password}"
        ]
        result=subprocess.run(command, capture_output=True,text=True)

        if result.returncode != 0:
            raise Exception(f"OpenSSL encryption failed: {result.stderr}")
        return True


    def decrypt_aes(self,input_path,output_path,password):
        command = [
            "openssl", "enc", "-d","-aes-256-cbc",
            "-in", input_path,
            "-out", output_path,
            "-pass", f"pass:{password}"
        ]
        result=subprocess.run(command, capture_output=True,text=True)

        if result.returncode != 0:
            raise Exception(f"OpenSSL decryption failed: {result.stderr}")
        return True

    def generate_rsa_keys(self, private_key_path, public_key_path):
        cmd_priv = ["openssl", "genpkey", "-algorithm", "RSA", "-out", private_key_path, "-pkeyopt",
                    "rsa_keygen_bits:2048"]
        result_priv = subprocess.run(cmd_priv, capture_output=True, text=True)

        # 2. Extragem cheia publică
        cmd_pub = ["openssl", "rsa", "-pubout", "-in", private_key_path, "-out", public_key_path]
        result_pub = subprocess.run(cmd_pub, capture_output=True, text=True)

        if result_priv.returncode != 0 or result_pub.returncode != 0:
            raise Exception("OpenSSL RSA Key Generation failed")
        return True

    def encrypt_rsa(self, input_path, output_path, public_key_path):
        command = [
            "openssl", "pkeyutl", "-encrypt",
            "-pubin", "-inkey", public_key_path,
            "-in", input_path,
            "-out", output_path
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"OpenSSL RSA encryption failed: {result.stderr}")
        return True

    def decrypt_rsa(self, input_path, output_path, private_key_path):
        command = [
            "openssl", "pkeyutl", "-decrypt",
            "-inkey", private_key_path,
            "-in", input_path,
            "-out", output_path
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"OpenSSL RSA decryption failed: {result.stderr}")
        return True