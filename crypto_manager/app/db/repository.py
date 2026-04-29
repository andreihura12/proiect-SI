from app.db.database import execute_query, fetch_query, get_connection
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
    def get_file_by_id(file_id):
        rows = fetch_query("SELECT * FROM Files WHERE id = ?", (file_id,))
        return FileModel(**dict(rows[0])) if rows else None

    @staticmethod
    def delete_file(file_id):
        execute_query("""
                DELETE FROM Performance WHERE operation_id IN (
                    SELECT id FROM Operations WHERE file_id = ?
                )""", (file_id,))

        execute_query("DELETE FROM Operations WHERE file_id = ?", (file_id,))
        execute_query("DELETE FROM Files WHERE id = ?", (file_id,))

    @staticmethod
    def update_file_status(file_id, new_status):
        query = "UPDATE Files SET status = ? WHERE id = ?"
        execute_query(query, (new_status, file_id))

    @staticmethod
    def update_file_hash(file_id, new_hash):
        query = "UPDATE Files SET hash = ? WHERE id = ?"
        execute_query(query, (new_hash, file_id))

    @staticmethod
    def create_key(key: KeyModel):
        query = """INSERT INTO Keys (algorithm_id, key_name, key_type, key_path, is_active) 
                   VALUES (?, ?, ?, ?, ?)"""
        params = (key.algorithm_id, key.key_name, key.key_type, key.key_path, key.is_active)

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        last_id = cursor.lastrowid
        conn.close()
        return last_id

    @staticmethod
    def get_all_keys():
        rows = fetch_query("SELECT * FROM Keys WHERE is_active = 1")
        return [KeyModel(**dict(row)) for row in rows]

    @staticmethod
    def get_key_by_id(key_id):
        rows = fetch_query("SELECT * FROM Keys WHERE id = ?", (key_id,))
        return KeyModel(**dict(rows[0])) if rows else None

    @staticmethod
    def get_last_key_for_file(file_id):
        query = """SELECT key_id FROM Operations 
                   WHERE file_id = ? AND operation_type = 'Encryption' 
                   ORDER BY id DESC LIMIT 1"""
        rows = fetch_query(query, (file_id,))
        if rows:
            return CryptoRepository.get_key_by_id(rows[0]['key_id'])
        return None

    @staticmethod
    def log_operation(file_id, algo_id, framework_id, key_id, op_type, in_path, out_path):
        query = """INSERT INTO Operations (file_id, algorithm_id, framework_id, key_id, 
                       operation_type, input_path, output_path, status) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""
        params = (file_id, algo_id, framework_id, key_id, op_type, in_path, out_path, 'Succes')

        from app.db.database import get_connection
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        op_id = cursor.lastrowid
        conn.close()
        return op_id

    @staticmethod
    def log_performance(perf: PerformanceModel):
        query = "INSERT INTO Performance (operation_id, memory, execution_time) VALUES (?, ?, ?)"
        params = (perf.operation_id, perf.memory, perf.execution_time)
        execute_query(query, params)

    @staticmethod
    def create_algorithm(algo: AlgorithmModel):
        query = "INSERT INTO Algorithms (name, type, key_size, mode) VALUES (?, ?, ?, ?)"
        params = (algo.name, algo.type, algo.key_size, algo.mode)
        execute_query(query, params)

    @staticmethod
    def get_algorithm_by_name(name):
        rows = fetch_query("SELECT * FROM Algorithms WHERE name = ?", (name,))
        return AlgorithmModel(**dict(rows[0])) if rows else None