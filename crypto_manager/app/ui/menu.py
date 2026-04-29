import tkinter as tk
import os
import time
import hashlib
import psutil
from tkinter import filedialog, messagebox, ttk
from app.services.file_service import FileService
from app.db.repository import CryptoRepository
from app.models.file_model import FileModel
from app.models.key_model import KeyModel
from app.models.performance_model import PerformanceModel
from app.crypto.openssl_handler import OpenSSLHandler


class CryptoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Crypto Manager Pro - Unified Performance Table")
        self.root.geometry("1200x700")

        self.file_service = FileService()
        self.repo = CryptoRepository()
        self.openssl_handler = OpenSSLHandler()

        self.setup_ui()
        self.load_keys_to_combo()
        self.refresh_table()

    def setup_ui(self):
        frame_controls = tk.LabelFrame(self.root, text="Panou Control Operatii", padx=10, pady=10)
        frame_controls.pack(fill="x", padx=20, pady=10)

        tk.Button(frame_controls, text="Importa Fisier", command=self.browse_and_save, bg="#e1e1e1").pack(side="left",
                                                                                                          padx=5)

        tk.Label(frame_controls, text="Algoritm:").pack(side="left", padx=5)
        self.combo_algo = ttk.Combobox(frame_controls, values=[
            "AES (OpenSSL)", "RSA (OpenSSL)",
            "AES (Cryptography Library)", "RSA (Cryptography Library)"
        ], width=25, state="readonly")
        self.combo_algo.set("AES (OpenSSL)")
        self.combo_algo.pack(side="left", padx=5)

        tk.Label(frame_controls, text="Cheie:").pack(side="left", padx=5)
        self.combo_keys = ttk.Combobox(frame_controls, state="readonly", width=30)
        self.combo_keys.pack(side="left", padx=5)

        tk.Button(frame_controls, text="Refresh", command=self.load_keys_to_combo).pack(side="left", padx=2)
        tk.Button(frame_controls, text="Debug", command=self.debug_key_info, bg="#fff3cd").pack(side="left", padx=2)

        self.btn_crypt = tk.Button(frame_controls, text="Cripteaza", command=self.crypt_action, bg="#99ff99",
                                   font=('Helvetica', 9, 'bold'), width=15)
        self.btn_crypt.pack(side="left", padx=10)

        self.btn_decrypt = tk.Button(frame_controls, text="Decripteaza", command=self.decrypt_action, bg="#99ccff",
                                     font=('Helvetica', 9, 'bold'), width=15)
        self.btn_decrypt.pack(side="left", padx=5)

        frame_bot = tk.LabelFrame(self.root, text="Vizualizare Date SQL & Monitorizare Performanta", padx=10, pady=10)
        frame_bot.pack(fill="both", expand=True, padx=20, pady=10)

        self.columns = ("ID", "Nume", "Status", "Extensie", "Marime", "Hash", "RAM (KB)", "Timp (ms)")
        self.tree = ttk.Treeview(frame_bot, columns=self.columns, show="headings")

        for col in self.columns:
            self.tree.heading(col, text=col)
            if col == "Hash":
                width = 120
            elif col == "Nume":
                width = 200
            else:
                width = 90
            self.tree.column(col, width=width, anchor="center")

        self.tree.pack(fill="both", expand=True, side="left")

        scrollbar = ttk.Scrollbar(frame_bot, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        self.btn_delete = tk.Button(self.root, text="Sterge Selectat", command=self.delete_selected, bg="#ff9999")
        self.btn_delete.pack(pady=10)

    def load_keys_to_combo(self):
        try:
            keys = self.repo.get_all_keys()
            options = ["noua"] + [f"ID: {k.id} | {k.key_name}" for k in keys]
            self.combo_keys['values'] = options
            self.combo_keys.current(0)
        except Exception as e:
            print(f"Eroare chei: {e}")

    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            query = """
                SELECT f.id, f.filename, f.status, f.file_type, f.size_bytes, f.hash, p.memory, p.execution_time
                FROM Files f
                LEFT JOIN (
                    SELECT file_id, MAX(id) as last_op_id FROM Operations GROUP BY file_id
                ) last_op ON f.id = last_op.file_id
                LEFT JOIN Operations o ON last_op.last_op_id = o.id
                LEFT JOIN Performance p ON o.id = p.operation_id
                ORDER BY f.id ASC
            """
            from app.db.database import fetch_query
            rows = fetch_query(query)

            for r in rows:
                ram = r['memory'] if r['memory'] else "-"
                timp = r['execution_time'] if r['execution_time'] else "-"
                h = r['hash'][:12] if r['hash'] else "-"

                self.tree.insert("", "end", values=(
                    r['id'], r['filename'], r['status'], r['file_type'],
                    r['size_bytes'], h, ram, timp
                ))
        except Exception as e:
            print(f"Eroare refresh: {e}")

    def crypt_action(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Atentie", "Selecteaza un fisier!")
            return

        file_id = self.tree.item(selected_item)['values'][0]
        algo_chosen = self.combo_algo.get()
        key_selection = self.combo_keys.get()

        try:
            process = psutil.Process(os.getpid())
            start_mem, start_time = process.memory_info().rss, time.time()

            file_record = self.repo.get_file_by_id(file_id)
            input_path = file_record.path
            key_id, framework_id, output_path = None, (1 if "OpenSSL" in algo_chosen else 2), ""

            existing_key = None
            if "ID:" in key_selection:
                key_id = int(key_selection.split("|")[0].replace("ID:", "").strip())
                existing_key = self.repo.get_key_by_id(key_id)

            if "AES (OpenSSL)" == algo_chosen:
                output_path = input_path + ".enc"
                password = existing_key.key_path if existing_key else "parola123"
                self.openssl_handler.encrypt_aes(input_path, output_path, password)
                if not existing_key:
                    key_id = self.repo.create_key(
                        KeyModel(algorithm_id=1, key_name=f"AES_{file_id}", key_type="Symmetric", key_path=password,
                                 is_active=1))

            elif "RSA (OpenSSL)" == algo_chosen:
                output_path = input_path + ".rsa"
                if existing_key:
                    pub_path = existing_key.key_path.replace("private_", "public_")
                else:
                    if not os.path.exists("keys"): os.makedirs("keys")
                    priv_path, pub_path = f"keys/private_{file_id}.pem", f"keys/public_{file_id}.pem"
                    self.openssl_handler.generate_rsa_keys(priv_path, pub_path)
                    key_id = self.repo.create_key(
                        KeyModel(algorithm_id=2, key_name=f"RSA_{file_id}", key_type="Asymmetric", key_path=priv_path,
                                 is_active=1))
                self.openssl_handler.encrypt_rsa(input_path, output_path, pub_path)

            elif "AES (Cryptography Library)" == algo_chosen:
                from cryptography.fernet import Fernet
                output_path = input_path + ".crypt"
                key_val = existing_key.key_path.encode() if existing_key else Fernet.generate_key()
                f = Fernet(key_val)
                with open(input_path, "rb") as file:
                    data = file.read()
                with open(output_path, "wb") as file:
                    file.write(f.encrypt(data))
                if not existing_key:
                    key_id = self.repo.create_key(
                        KeyModel(algorithm_id=1, key_name=f"Fernet_{file_id}", key_type="Symmetric",
                                 key_path=key_val.decode(), is_active=1))

            elif "RSA (Cryptography Library)" == algo_chosen:
                from cryptography.hazmat.primitives.asymmetric import padding
                from cryptography.hazmat.primitives import hashes, serialization
                output_path = input_path + ".lib_rsa"
                if existing_key:
                    with open(existing_key.key_path, "rb") as k_f:
                        priv_key = serialization.load_pem_private_key(k_f.read(), password=None)
                else:
                    from cryptography.hazmat.primitives.asymmetric import rsa
                    priv_key = rsa.generate_private_key(65537, 2048)
                    if not os.path.exists("keys"): os.makedirs("keys")
                    priv_path = f"keys/priv_lib_{file_id}.pem"
                    with open(priv_path, "wb") as f:
                        f.write(priv_key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
                                                       serialization.NoEncryption()))
                    key_id = self.repo.create_key(
                        KeyModel(algorithm_id=2, key_name=f"RSA_Lib_{file_id}", key_type="Asymmetric",
                                 key_path=priv_path, is_active=1))
                with open(input_path, "rb") as file:
                    data = file.read()
                enc = priv_key.public_key().encrypt(data, padding.OAEP(mgf=padding.MGF1(hashes.SHA256()),
                                                                       algorithm=hashes.SHA256(), label=None))
                with open(output_path, "wb") as file:
                    file.write(enc)

            exec_time = int((time.time() - start_time) * 1000)
            mem_used = max(0, int((psutil.Process(os.getpid()).memory_info().rss - start_mem) / 1024))

            file_hash = hashlib.sha256(open(output_path, "rb").read()).hexdigest()
            self.repo.update_file_status(file_id, f"Criptat ({algo_chosen})")
            self.repo.update_file_hash(file_id, file_hash)

            op_id = self.repo.log_operation(file_id, (1 if "AES" in algo_chosen else 2), framework_id, key_id,
                                            "Encryption", input_path, output_path)
            self.repo.log_performance(
                PerformanceModel(operation_id=op_id, memory=str(mem_used), execution_time=str(exec_time)))

            self.refresh_table()
            self.load_keys_to_combo()
            messagebox.showinfo("Succes", f"Criptat în {exec_time}ms")
        except Exception as e:
            messagebox.showerror("Eroare", str(e))

    def decrypt_action(self):
        selected_item = self.tree.selection()
        if not selected_item: return
        file_id = self.tree.item(selected_item)['values'][0]
        status = self.tree.item(selected_item)['values'][2]
        if "Necriptat" in status: return
        try:
            key_record = self.repo.get_last_key_for_file(file_id)
            file_record = self.repo.get_file_by_id(file_id)
            dec_path = os.path.splitext(file_record.path)[0] + "_restored" + os.path.splitext(file_record.path)[1]
            if "OpenSSL" in status:
                if "AES" in status:
                    self.openssl_handler.decrypt_aes(file_record.path + ".enc", dec_path, key_record.key_path)
                else:
                    self.openssl_handler.decrypt_rsa(file_record.path + ".rsa", dec_path, key_record.key_path)
            self.repo.update_file_status(file_id, "Necriptat")
            self.refresh_table()
            messagebox.showinfo("Succes", "Fisier restaurat!")
        except Exception as e:
            messagebox.showerror("Eroare", str(e))

    def debug_key_info(self):
        selection = self.combo_keys.get()
        if "noua" in selection or not selection:
            messagebox.showinfo("Debug", "Nicio cheie existenta selectata.")
            return
        try:
            key_id = int(selection.split("|")[0].replace("ID:", "").strip())
            key_data = self.repo.get_key_by_id(key_id)
            info = f"ID: {key_data.id}\nNume: {key_data.key_name}\nTip: {key_data.key_type}\nPath: {key_data.key_path}"
            messagebox.showinfo("Debug Info", info)
        except Exception as e:
            messagebox.showerror("Eroare", f"Nu s-au putut prelua detaliile: {e}")

    def browse_and_save(self):
        path = filedialog.askopenfilename()
        if path:
            info = self.file_service.get_file_info(path)
            self.repo.create_file(FileModel(filename=info['filename'], path=info['path'], file_type=info['file_type'],
                                            size_bytes=info['size_bytes'], hash=info['hash'], status="Necriptat"))
            self.refresh_table()

    def delete_selected(self):
        selected_item = self.tree.selection()
        if selected_item:
            self.repo.delete_file(self.tree.item(selected_item)['values'][0])
            self.refresh_table()

