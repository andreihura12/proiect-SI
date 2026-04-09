from app.db.database import execute_query, fetch_query
from app.models.file_model import FileModel
from app.models.algorithm_model import AlgorithmModel
from app.models.key_model import KeyModel
from app.models.performance_model import PerformanceModel


class CryptoRepository:


    @staticmethod
    def create_file(file: FileModel):
        query = """INSERT INTO Files (filename, path, file_type, size_bytes, hash) 
                   VALUES (?, ?, ?, ?, ?)"""
        params = (file.filename, file.path, file.file_type, file.size_bytes, file.hash)
        execute_query(query, params)

    @staticmethod
    def get_all_files():
        rows = fetch_query("SELECT * FROM Files")
        return [FileModel(**dict(row)) for row in rows]

    @staticmethod
    def delete_file(file_id):
        execute_query("DELETE FROM Files WHERE id = ?", (file_id,))


    @staticmethod
    def create_algorithm(algo: AlgorithmModel):
        query = "INSERT INTO Algorithms (name, type, key_size, mode) VALUES (?, ?, ?, ?)"
        params = (algo.name, algo.type, algo.key_size, algo.mode)
        execute_query(query, params)

    @staticmethod
    def get_algorithm_by_name(name):
        rows = fetch_query("SELECT * FROM Algorithms WHERE name = ?", (name,))
        return AlgorithmModel(**dict(rows[0])) if rows else None


    @staticmethod
    def create_key(key: KeyModel):
        query = """INSERT INTO Keys (algorithm_id, key_name, key_type, key_path, is_active) 
                   VALUES (?, ?, ?, ?, ?)"""
        params = (key.algorithm_id, key.key_name, key.key_type, key.key_path, key.is_active)
        execute_query(query, params)


    @staticmethod
    def log_performance(perf: PerformanceModel):
        query = "INSERT INTO Performance (operation_id, memory, execution_time) VALUES (?, ?, ?)"
        params = (perf.operation_id, perf.memory, perf.execution_time)
        execute_query(query, params)

    @staticmethod
    def update_file_status(file_id, new_status):
        query = "UPDATE Files SET status = ? WHERE id = ?"
        params = (new_status, file_id)
        execute_query(query, params)
    @staticmethod
    def get_file_by_id(file_id):
        rows = fetch_query("SELECT * FROM Files WHERE id = ?", (file_id,))
        return FileModel(**dict(rows[0])) if rows else None

