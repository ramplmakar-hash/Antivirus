import tkinter as tk
from tkinter import filedialog, messagebox
import hashlib
import os

# "Черный список" хешей (пример)
SIGNATURES = {
    "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855": "Test.Virus"
}

def check_file(path):
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                h.update(chunk)
        return h.hexdigest()
    except: return None

def scan():
    folder = filedialog.askdirectory()
    if not folder: return
    found = []
    for r, d, files in os.walk(folder):
        for f in files:
            full_path = os.path.join(r, f)
            if check_file(full_path) in SIGNATURES:
                found.append(full_path)
    
    if found:
        messagebox.showwarning("Опасно!", f"Найдено вирусов: {len(found)}")
    else:
        messagebox.showinfo("Готово", "Все чисто!")

root = tk.Tk()
root.title("My PC Antivirus")
root.geometry("300x200")
tk.Label(root, text="Антивирус v1.0", font=("Arial", 15)).pack(pady=20)
tk.Button(root, text="Сканировать папку", command=scan, bg="green", fg="white").pack(pady=10)
root.mainloop()
