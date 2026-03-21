import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from ..services.file_service import FileService
from ..db.repository import CryptoRepository
from ..models.file_model import FileModel


class CryptoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Crypto Manager - Modul Baze de Date (CRUD)")
        self.root.geometry("800x500")

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

        frame_middle = tk.LabelFrame(self.root, text="Pasul 2: Operatii Criptare (Placeholder pentru Sapt. 3)", padx=10,
                                     pady=10)
        frame_middle.pack(fill="x", padx=20, pady=5)

        tk.Label(frame_middle, text="Algoritm:").grid(row=0, column=0)
        ttk.Combobox(frame_middle, values=["AES (OpenSSL)", "RSA (OpenSSL)"], state="disabled").grid(row=0, column=1,
                                                                                                     padx=5)

        btn_dummy = tk.Button(frame_middle, text="Cripteaza (Inactiv)", state="disabled")
        btn_dummy.grid(row=0, column=2, padx=10)

        frame_bot = tk.LabelFrame(self.root, text="Vizualizare Date din SQL (READ / DELETE)", padx=10, pady=10)
        frame_bot.pack(fill="both", expand=True, padx=20, pady=10)

        columns = ("ID", "Nume", "Extensie", "Marime (Bytes)", "Hash SHA256")
        self.tree = ttk.Treeview(frame_bot, columns=columns, show="headings")

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

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
                    hash=info['hash']
                )

                self.repo.create_file(new_file)

                self.lbl_status.config(text=f"Salvat: {info['filename']}", fg="green")
                self.refresh_table()  # Update tabel
                messagebox.showinfo("Succes", "Fisierul a fost inserat in baza de date!")
            except Exception as e:
                messagebox.showerror("Eroare", f"Nu s-a putut salva: {e}")

    def refresh_table(self):
        """Functia de READ din CRUD"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        files = self.repo.get_all_files()
        for f in files:
            self.tree.insert("", "end", values=(f.id, f.filename, f.file_type, f.size_bytes, f.hash[:15] + "..."))

    def delete_selected(self):
        """Functia de DELETE din CRUD"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Atentie", "Selecteaza un rand din tabel pentru a-l sterge!")
            return

        item_data = self.tree.item(selected_item)
        file_id = item_data['values'][0]

        if messagebox.askyesno("Confirmare", f"Sigur vrei sa stergi inregistrarea cu ID {file_id}?"):
            self.repo.delete_file(file_id)
            self.refresh_table()
            messagebox.showinfo("OK", "Inregistrare stearsa!")