import os
import hashlib

class FileService:
    def calculate_hash(self, file_path):
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
           while chunk := f.read(4096):
               sha256_hash.update(chunk)
        return sha256_hash.hexdigest()

    def get_file_size(self, file_path):
        return os.path.getsize(file_path)

    def get_file_type(self, file_path):
        return os.path.splitext(file_path)[1]

    def get_filename(self, file_path):
        return os.path.basename(file_path)

    def get_file_info(self, file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        return {
            "filename": self.get_filename(file_path),
            "path": file_path,
            "size_bytes": self.get_file_size(file_path),
            "file_type": self.get_file_type(file_path),
            "hash": self.calculate_hash(file_path)
        }