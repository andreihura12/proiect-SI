import tkinter as tk
from app.db.database import init_db
from app.ui.menu import CryptoApp

if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = CryptoApp(root)
    root.mainloop()