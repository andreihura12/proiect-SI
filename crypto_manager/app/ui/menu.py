import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from app.services.file_service import FileService
from app.db.repository import CryptoRepository
from app.models.file_model import FileModel


class CryptoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Crypto Manager - Modul Baze de Date (CRUD)")
        self.root.geometry("900x600")

        self.file_service = FileService()
        self.repo = CryptoRepository()

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
        self.combo_algo = ttk.Combobox(frame_middle, values=["AES (OpenSSL)", "RSA (OpenSSL)"])
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
            messagebox.showwarning("Atentie", "Selecteaza un fisier din tabel pentru a-l cripta!")
            return

        item_data = self.tree.item(selected_item)
        file_id = item_data['values'][0]
        algo_chosen = self.combo_algo.get()
        new_status = f"Criptat cu {algo_chosen}"

        try:
            self.repo.update_file_status(file_id, new_status)

            self.refresh_table()
            messagebox.showinfo("Update DB", f"Statusul a fost actualizat in: {new_status}")
        except Exception as e:
            messagebox.showerror("Eroare Update", f"A aparut o eroare: {e}")

    def decrypt_action(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Atentie", "Selecteaza un fisier din tabel!")
            return

        item_data = self.tree.item(selected_item)
        file_id = item_data['values'][0]
        current_status = item_data['values'][2]

        if "Criptat" not in current_status:
            messagebox.showwarning("Operatie Invalida", "Fisierul este deja necriptat!")
            return

        new_status = "Necriptat"

        try:
            self.repo.update_file_status(file_id, new_status)

            self.refresh_table()
            messagebox.showinfo("Update DB", "Fisierul a fost decriptat cu succes in baza de date!")
        except Exception as e:
            messagebox.showerror("Eroare Update", f"A aparut o eroare: {e}")

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