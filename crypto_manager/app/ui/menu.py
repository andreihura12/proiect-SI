import tkinter as tk
import os
from tkinter import filedialog, messagebox, ttk
from app.services.file_service import FileService
from app.db.repository import CryptoRepository
from app.models.file_model import FileModel
from app.crypto.openssl_handler import OpenSSLHandler


class CryptoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Crypto Manager - Modul Baze de Date (CRUD)")
        self.root.geometry("900x600")

        self.file_service = FileService()
        self.repo = CryptoRepository()
        self.openssl_handler = OpenSSLHandler()

        self.setup_ui()

    def setup_ui(self):
        frame_top = tk.LabelFrame(self.root, text="Pasul 1: Inregistrare Fisier (CREATE)", padx=10, pady=10)
        frame_top.pack(fill="x", padx=20, pady=10)

        self.btn_browse = tk.Button(frame_top, text="Alege Fisier pentru DB", command=self.browse_and_save,
                                    bg="#e1e1e1")
        self.btn_browse.pack(side="left")

        self.lbl_status = tk.Label(frame_top, text="Selecteaza un fisier pentru a-l salva in SQL", fg="gray")
        self.lbl_status.pack(side="left", padx=10)

        frame_middle = tk.LabelFrame(self.root, text="Pasul 2: Operatii Criptare (UPDATE Status)", padx=10, pady=10)
        frame_middle.pack(fill="x", padx=20, pady=5)

        tk.Label(frame_middle, text="Algoritm:").grid(row=0, column=0)
        self.combo_algo = ttk.Combobox(frame_middle, values=["AES (OpenSSL)", "RSA (OpenSSL)", "AES (Cryptography Library)",  # Varianta 3
    "RSA (Cryptography Library)" ])
        self.combo_algo.set("AES (OpenSSL)")
        self.combo_algo.grid(row=0, column=1, padx=5)

        self.btn_crypt = tk.Button(frame_middle, text="Cripteaza si Update Status", command=self.crypt_action,
                                   bg="#99ff99")
        self.btn_crypt.grid(row=0, column=2, padx=10)

        self.btn_decrypt = tk.Button(frame_middle, text="Decripteaza si Update Status", command=self.decrypt_action,
                                     bg="#99ccff")
        self.btn_decrypt.grid(row=0, column=3, padx=10)

        frame_bot = tk.LabelFrame(self.root, text="Vizualizare Date din SQL (READ / DELETE)", padx=10, pady=10)
        frame_bot.pack(fill="both", expand=True, padx=20, pady=10)

        columns = ("ID", "Nume", "Status", "Extensie", "Marime", "Hash")
        self.tree = ttk.Treeview(frame_bot, columns=columns, show="headings")

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)

        self.tree.pack(fill="both", expand=True, side="left")

        scrollbar = ttk.Scrollbar(frame_bot, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        self.btn_delete = tk.Button(self.root, text="Sterge Fisierul Selectat (DELETE)", command=self.delete_selected,
                                    bg="#ff9999")
        self.btn_delete.pack(pady=10)

        self.refresh_table()

    def browse_and_save(self):
        path = filedialog.askopenfilename()
        if path:
            try:
                info = self.file_service.get_file_info(path)
                new_file = FileModel(
                    filename=info['filename'],
                    path=info['path'],
                    file_type=info['file_type'],
                    size_bytes=info['size_bytes'],
                    hash=info['hash'],
                    status="Necriptat"
                )
                self.repo.create_file(new_file)
                self.refresh_table()
                messagebox.showinfo("Succes", "Fisierul a fost inserat!")
            except Exception as e:
                messagebox.showerror("Eroare", f"Nu s-a putut salva: {e}")

    def crypt_action(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Atentie", "Selecteaza un fisier din tabel!")
            return

        item_data = self.tree.item(selected_item)
        file_id = item_data['values'][0]
        algo_chosen = self.combo_algo.get()

        try:
            file_record = self.repo.get_file_by_id(file_id)
            if not file_record:
                messagebox.showerror("Eroare", "Fisierul nu a fost gasit in baza de date.")
                return

            input_path = file_record.path
            from app.models.key_model import KeyModel
            import time

            start_time = time.time()
            key_id = None
            framework_id = 1
            if algo_chosen == "AES (OpenSSL)":
                output_path = input_path + ".enc"
                password = "parola123"
                self.openssl_handler.encrypt_aes(input_path, output_path, password)

                # Salvăm cheia (parola) în DB
                new_key = KeyModel(algorithm_id=1, key_name=f"AES_Pass_{file_id}",
                                   key_type="Symmetric", key_path=password, is_active=1)
                key_id = self.repo.create_key(new_key)

            elif algo_chosen == "RSA (OpenSSL)":
                output_path = input_path + ".rsa"
                if not os.path.exists("keys"): os.makedirs("keys")
                priv_key_path = f"keys/private_{file_id}.pem"
                pub_key_path = f"keys/public_{file_id}.pem"

                self.openssl_handler.generate_rsa_keys(priv_key_path, pub_key_path)
                self.openssl_handler.encrypt_rsa(input_path, output_path, pub_key_path)

                new_key = KeyModel(algorithm_id=2, key_name=f"RSA_Key_{file_id}",
                                   key_type="Asymmetric", key_path=priv_key_path, is_active=1)
                key_id = self.repo.create_key(new_key)

            elif algo_chosen == "AES (Cryptography Library)":
                from cryptography.fernet import Fernet
                framework_id = 2
                output_path = input_path + ".crypt"

                key = Fernet.generate_key()
                f = Fernet(key)
                with open(input_path, "rb") as file:
                    data = file.read()
                encrypted_data = f.encrypt(data)
                with open(output_path, "wb") as file:
                    file.write(encrypted_data)

                new_key = KeyModel(algorithm_id=1, key_name=f"Fernet_Key_{file_id}",
                                   key_type="Symmetric", key_path=key.decode(), is_active=1)
                key_id = self.repo.create_key(new_key)

            # --- CAZ 4: RSA (Cryptography Library - Varianta 3: Wrapper) ---
            elif algo_chosen == "RSA (Cryptography Library)":
                from cryptography.hazmat.primitives.asymmetric import rsa, padding
                from cryptography.hazmat.primitives import hashes, serialization
                framework_id = 2
                output_path = input_path + ".lib_rsa"

                # Generare și Criptare
                priv_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
                with open(input_path, "rb") as file:
                    data = file.read()
                encrypted = priv_key.public_key().encrypt(
                    data, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                                       algorithm=hashes.SHA256(), label=None)
                )
                with open(output_path, "wb") as file:
                    file.write(encrypted)

                # Salvare cheie privată PEM
                if not os.path.exists("keys"): os.makedirs("keys")
                priv_key_path = f"keys/priv_lib_{file_id}.pem"
                with open(priv_key_path, "wb") as f:
                    f.write(priv_key.private_bytes(encoding=serialization.Encoding.PEM,
                                                   format=serialization.PrivateFormat.PKCS8,
                                                   encryption_algorithm=serialization.NoEncryption()))

                new_key = KeyModel(algorithm_id=2, key_name=f"RSA_Lib_{file_id}",
                                   key_type="Asymmetric", key_path=priv_key_path, is_active=1)
                key_id = self.repo.create_key(new_key)

            # --- FINALIZARE: Update DB, Hash și Operations ---
            # 1. Calculăm Hash-ul fișierului criptat (pentru audit)
            import hashlib
            with open(output_path, "rb") as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()

            # 2. Update status și hash în tabelul Files
            self.repo.update_file_status(file_id, f"Criptat ({algo_chosen})")
            self.repo.update_file_hash(file_id, file_hash)  # Presupunem că ai metoda asta

            # 3. Log în tabelul Operations (Management funcțional)
            exec_time = int((time.time() - start_time) * 1000)
            self.repo.log_operation(
                file_id=file_id,
                algo_id=(1 if "AES" in algo_chosen else 2),
                framework_id=framework_id,
                key_id=key_id,
                op_type="Encryption",
                in_path=input_path,
                out_path=output_path
            )

            self.refresh_table()
            messagebox.showinfo("Succes", f"Fișier criptat cu succes!\nExecuție: {exec_time}ms")

        except Exception as e:
            messagebox.showerror("Eroare criptare", f"A aparut o eroare: {str(e)}")

    def decrypt_action(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Atentie", "Selecteaza un fisier din tabel!")
            return

        item_data = self.tree.item(selected_item)
        file_id = item_data['values'][0]
        current_status = item_data['values'][2]

        if "Necriptat" in current_status:
            messagebox.showwarning("Operatie invalida", "Fisierul nu este criptat.")
            return

        try:
            file_record = self.repo.get_file_by_id(file_id)
            original_path = file_record.path

            if "AES" in current_status:
                encrypted_path = original_path + ".enc"
                decrypted_path = os.path.splitext(original_path)[0] + "_dec_aes" + os.path.splitext(original_path)[1]
                self.openssl_handler.decrypt_aes(encrypted_path, decrypted_path, "parola123")

            elif "RSA" in current_status:
                encrypted_path = original_path + ".rsa"
                decrypted_path = os.path.splitext(original_path)[0] + "_dec_rsa" + os.path.splitext(original_path)[1]


                priv_key_path = f"keys/private_{file_id}.pem"

                if not os.path.exists(priv_key_path):
                    messagebox.showerror("Eroare", "Cheia privata nu a fost gasita!")
                    return

                self.openssl_handler.decrypt_rsa(encrypted_path, decrypted_path, priv_key_path)

            self.repo.update_file_status(file_id, "Necriptat")
            self.refresh_table()
            messagebox.showinfo("Succes", f"Decriptare reușită!\nRezultat: {decrypted_path}")

        except Exception as e:
            messagebox.showerror("Eroare decriptare", f"A aparut o eroare: {e}")

        except Exception as e:
            messagebox.showerror("Eroare decriptare", f"A aparut o eroare: {e}")

    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        files = self.repo.get_all_files()
        for f in files:
            self.tree.insert("", "end", values=(f.id, f.filename, f.status, f.file_type, f.size_bytes, f.hash[:10]))

    def delete_selected(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Atentie", "Selecteaza un rand!")
            return
        item_data = self.tree.item(selected_item)
        file_id = item_data['values'][0]
        if messagebox.askyesno("Confirmare", f"Stergi ID {file_id}?"):
            self.repo.delete_file(file_id)
            self.refresh_table()