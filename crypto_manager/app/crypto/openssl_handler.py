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