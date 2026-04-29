import tkinter as tk
from app.ui.menu import CryptoApp

if __name__ == "__main__":
    root = tk.Tk()
    app = CryptoApp(root)
    root.mainloop()