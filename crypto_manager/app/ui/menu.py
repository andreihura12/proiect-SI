import tkinter as tk
import os
import time
import hashlib
from tkinter import filedialog, messagebox, ttk
from app.services.file_service import FileService
from app.db.repository import CryptoRepository
from app.models.file_model import FileModel
from app.models.key_model import KeyModel
from app.crypto.openssl_handler import OpenSSLHandler


class CryptoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Crypto Manager Pro - Database & Audit Edition")
        self.root.geometry("1000x750")

        self.file_service = FileService()
        self.repo = CryptoRepository()
        self.openssl_handler = OpenSSLHandler()

        self.setup_ui()
        self.load_keys_to_combo()

    def setup_ui(self):
        frame_top = tk.LabelFrame(self.root, text="Pasul 1: Management Fisiere (CRUD)", padx=10, pady=10)
        frame_top.pack(fill="x", padx=20, pady=10)

        self.btn_browse = tk.Button(frame_top, text="Importa Fisier in DB", command=self.browse_and_save, bg="#e1e1e1")
        self.btn_browse.pack(side="left")

        self.lbl_status = tk.Label(frame_top, text="Selecteaza un fisier pentru a-l salva in SQL", fg="gray")
        self.lbl_status.pack(side="left", padx=10)

        frame_middle = tk.LabelFrame(self.root, text="Pasul 2: Operatii Criptare & Gestiune Chei", padx=10, pady=10)
        frame_middle.pack(fill="x", padx=20, pady=5)

        tk.Label(frame_middle, text="Algoritm:").grid(row=0, column=0, sticky="w", pady=5)
        self.combo_algo = ttk.Combobox(frame_middle, values=[
            "AES (OpenSSL)",
            "RSA (OpenSSL)",
            "AES (Cryptography Library)",
            "RSA (Cryptography Library)"
        ], width=30, state="readonly")
        self.combo_algo.set("AES (OpenSSL)")
        self.combo_algo.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame_middle, text="Foloseste Cheia:").grid(row=1, column=0, sticky="w", pady=5)
        self.combo_keys = ttk.Combobox(frame_middle, state="readonly", width=45)
        self.combo_keys.grid(row=1, column=1, padx=5, pady=5)

        btn_refresh = tk.Button(frame_middle, text="Refresh", command=self.load_keys_to_combo)
        btn_refresh.grid(row=1, column=2, padx=2)

        btn_debug = tk.Button(frame_middle, text="Debug Cheie", command=self.debug_key_info, bg="#fff3cd")
        btn_debug.grid(row=1, column=3, padx=5)

        # Rândul 3: Butoane Actiune
        btn_container = tk.Frame(frame_middle)
        btn_container.grid(row=2, column=0, columnspan=4, pady=15)

        self.btn_crypt = tk.Button(btn_container, text="Cripteaza & Audit", command=self.crypt_action, bg="#99ff99",
                                   width=25, font=('Helvetica', 9, 'bold'))
        self.btn_crypt.pack(side="left", padx=10)

        self.btn_decrypt = tk.Button(btn_container, text="Decripteaza & Audit", command=self.decrypt_action,
                                     bg="#99ccff", width=25, font=('Helvetica', 9, 'bold'))
        self.btn_decrypt.pack(side="left", padx=10)

        # --- TABEL VIZUALIZARE (Files) ---
        frame_bot = tk.LabelFrame(self.root, text="Vizualizare Date SQL (Tabela Files)", padx=10, pady=10)
        frame_bot.pack(fill="both", expand=True, padx=20, pady=10)

        columns = ("ID", "Nume", "Status", "Extensie", "Marime", "Hash")
        self.tree = ttk.Treeview(frame_bot, columns=columns, show="headings")

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

        self.tree.pack(fill="both", expand=True, side="left")
        scrollbar = ttk.Scrollbar(frame_bot, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        self.btn_delete = tk.Button(self.root, text="Sterge Fisier Selectat", command=self.delete_selected,
                                    bg="#ff9999")
        self.btn_delete.pack(pady=5)

    def load_keys_to_combo(self):
        try:
            keys = self.repo.get_all_keys() if hasattr(self.repo, 'get_all_keys') else []
            options = ["noua"]
            for k in keys:
                options.append(f"ID: {k.id} | {k.key_name} ({k.key_type})")

            self.combo_keys['values'] = options
            self.combo_keys.current(0)
        except Exception as e:
            print(f"Eroare incarcare chei: {e}")

    def debug_key_info(self):
        selection = self.combo_keys.get()
        if "noua" in selection or not selection:
            messagebox.showinfo("Debug", "Nicio cheie existenta selectata.")
            return

        try:
            key_id = int(selection.split("|")[0].replace("ID:", "").strip())
            key_data = self.repo.get_key_by_id(key_id)

            info = f"=== Detalii Cheie (DEBUG) ===\n\n"
            info += f"ID: {key_data.id}\n"
            info += f"Nume: {key_data.key_name}\n"
            info += f"Tip: {key_data.key_type}\n"
            info += f"Continut / Path: {key_data.key_path}\n"
            info += f"Status: {'Activa' if key_data.is_active else 'Inactiva'}"

            messagebox.showinfo("Debug Info", info)
        except Exception as e:
            messagebox.showerror("Eroare", f"Nu s-au putut prelua detaliile: {e}")

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
                messagebox.showinfo("Succes", "Fisierul a fost salvat in baza de date!")
            except Exception as e:
                messagebox.showerror("Eroare", f"Eroare la import: {e}")

    def crypt_action(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Atentie", "Selecteaza un fisier!")
            return

        item_data = self.tree.item(selected_item)
        file_id = item_data['values'][0]
        algo_chosen = self.combo_algo.get()
        key_selection = self.combo_keys.get()

        try:
            file_record = self.repo.get_file_by_id(file_id)
            input_path = file_record.path
            start_time = time.time()

            key_id = None
            framework_id = 1 if "OpenSSL" in algo_chosen else 2
            output_path = ""

            # Verificam daca folosim o cheie existenta sau generam una
            existing_key = None
            if "ID:" in key_selection:
                key_id = int(key_selection.split("|")[0].replace("ID:", "").strip())
                existing_key = self.repo.get_key_by_id(key_id)

            if algo_chosen == "AES (OpenSSL)":
                output_path = input_path + ".enc"
                password = existing_key.key_path if existing_key else "parola123"
                self.openssl_handler.encrypt_aes(input_path, output_path, password)

                if not existing_key:
                    new_key = KeyModel(algorithm_id=1, key_name=f"AES_Pass_{file_id}", key_type="Symmetric",
                                       key_path=password, is_active=1)
                    key_id = self.repo.create_key(new_key)

            elif algo_chosen == "RSA (OpenSSL)":
                output_path = input_path + ".rsa"
                if existing_key:
                    pub_path = existing_key.key_path.replace("private_", "public_")
                else:
                    if not os.path.exists("keys"): os.makedirs("keys")
                    priv_path, pub_path = f"keys/private_{file_id}.pem", f"keys/public_{file_id}.pem"
                    self.openssl_handler.generate_rsa_keys(priv_path, pub_path)
                    new_key = KeyModel(algorithm_id=2, key_name=f"RSA_Key_{file_id}", key_type="Asymmetric",
                                       key_path=priv_path, is_active=1)
                    key_id = self.repo.create_key(new_key)
                self.openssl_handler.encrypt_rsa(input_path, output_path, pub_path)

            elif algo_chosen == "AES (Cryptography Library)":
                from cryptography.fernet import Fernet
                output_path = input_path + ".crypt"
                key_val = existing_key.key_path.encode() if existing_key else Fernet.generate_key()

                f = Fernet(key_val)
                with open(input_path, "rb") as file:
                    data = file.read()
                with open(output_path, "wb") as file:
                    file.write(f.encrypt(data))

                if not existing_key:
                    new_key = KeyModel(algorithm_id=1, key_name=f"Fernet_{file_id}", key_type="Symmetric",
                                       key_path=key_val.decode(), is_active=1)
                    key_id = self.repo.create_key(new_key)

            elif algo_chosen == "RSA (Cryptography Library)":
                from cryptography.hazmat.primitives.asymmetric import padding
                from cryptography.hazmat.primitives import hashes, serialization
                output_path = input_path + ".lib_rsa"

                if existing_key:
                    with open(existing_key.key_path, "rb") as k_f:
                        priv_key = serialization.load_pem_private_key(k_f.read(), password=None)
                else:
                    from cryptography.hazmat.primitives.asymmetric import rsa
                    priv_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
                    if not os.path.exists("keys"): os.makedirs("keys")
                    priv_path = f"keys/priv_lib_{file_id}.pem"
                    with open(priv_path, "wb") as f:
                        f.write(priv_key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
                                                       serialization.NoEncryption()))
                    new_key = KeyModel(algorithm_id=2, key_name=f"RSA_Lib_{file_id}", key_type="Asymmetric",
                                       key_path=priv_path, is_active=1)
                    key_id = self.repo.create_key(new_key)

                with open(input_path, "rb") as file:
                    data = file.read()
                enc = priv_key.public_key().encrypt(data, padding.OAEP(mgf=padding.MGF1(hashes.SHA256()),
                                                                       algorithm=hashes.SHA256(), label=None))
                with open(output_path, "wb") as file:
                    file.write(enc)

            file_hash = hashlib.sha256(open(output_path, "rb").read()).hexdigest()
            self.repo.update_file_status(file_id, f"Criptat ({algo_chosen})")
            self.repo.update_file_hash(file_id, file_hash)

            exec_time = int((time.time() - start_time) * 1000)
            self.repo.log_operation(file_id, (1 if "AES" in algo_chosen else 2), framework_id, key_id, "Encryption",
                                    input_path, output_path)

            self.refresh_table()
            self.load_keys_to_combo()
            messagebox.showinfo("Succes", f"Criptare reusita!\nDurata: {exec_time}ms")

        except Exception as e:
            messagebox.showerror("Eroare", f"Criptarea a esuat: {str(e)}")

    def decrypt_action(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Atentie", "Selecteaza un fisier!")
            return

        item_data = self.tree.item(selected_item)
        file_id = item_data['values'][0]
        status = item_data['values'][2]

        if "Necriptat" in status:
            messagebox.showwarning("Info", "Fisierul nu este criptat.")
            return

        try:
            key_record = self.repo.get_last_key_for_file(file_id)
            file_record = self.repo.get_file_by_id(file_id)
            original_path = file_record.path
            dec_path = os.path.splitext(original_path)[0] + "_restored" + os.path.splitext(original_path)[1]

            if "OpenSSL" in status:
                if "AES" in status:
                    self.openssl_handler.decrypt_aes(original_path + ".enc", dec_path, key_record.key_path)
                else:
                    self.openssl_handler.decrypt_rsa(original_path + ".rsa", dec_path, key_record.key_path)

            # Nota: Poti extinde aici si pentru decriptarea cu framework-ul wrapper

            self.repo.update_file_status(file_id, "Necriptat")
            self.refresh_table()
            messagebox.showinfo("Succes", f"Decriptare finalizata!\nFisier: {dec_path}")
        except Exception as e:
            messagebox.showerror("Eroare", f"Decriptarea a esuat: {e}")

    def refresh_table(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        files = self.repo.get_all_files()
        for f in files:
            self.tree.insert("", "end", values=(f.id, f.filename, f.status, f.file_type, f.size_bytes, f.hash[:12]))

    def delete_selected(self):
        selected_item = self.tree.selection()
        if not selected_item: return
        file_id = self.tree.item(selected_item)['values'][0]
        if messagebox.askyesno("Confirmare", f"Stergi inregistrarea {file_id}?"):
            self.repo.delete_file(file_id)
            self.refresh_table()