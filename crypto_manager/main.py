from app.crypto.openssl_handler import OpenSSLHandler

def main():

    handler = OpenSSLHandler()

    input_file = "files/input/test.txt"
    encrypted_file = "files/encrypted/test.enc"
    decrypted_file = "files/decrypted/test_decrypted.txt"

    password = "parola123"

    try:
        print("Encrypting file...")
        handler.encrypt_aes(input_file, encrypted_file, password)

        print("Decrypting file...")
        handler.decrypt_aes(encrypted_file, decrypted_file, password)

        print("Test finished successfully.")

    except Exception as e:
        print("Error:", e)


if __name__ == "__main__":
    main()