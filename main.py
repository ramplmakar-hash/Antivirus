import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import hashlib
import os
import datetime
import shutil

# --- БАЗА ДАННЫХ ХЕШЕЙ ---
SIGNATURES = {
    "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855": "EICAR.Test.File",
    "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8": "Trojan.Generic.Downloader"
}

# Опасные расширения
DANGEROUS_EXTS = ('.exe', '.bat', '.vbs', '.js', '.scr', '.msi', '.cmd', '.com', '.pif')

def xor_cipher(data):
    """Шифрование файла для карантина"""
    return bytearray([b ^ 0x42 for b in data])

class ShieldMasterPro:
    def __init__(self, root):
        self.root = root
        self.root.title("ShieldMaster Pro v3.0")
        self.root.geometry("600x450")
        self.root.configure(bg="#0f172a")

        # Заголовок
        tk.Label(root, text="🛡️ SHIELDMASTER PRO", fg="#38bdf8", bg="#0f172a", 
                 font=("Arial", 18, "bold")).pack(pady=15)

        # Консоль
        self.log_area = tk.Text(root, height=15, width=70, bg="#020617", fg="#10b981", 
                                font=("Consolas", 8), borderwidth=0)
        self.log_area.pack(pady=10)

        # Кнопка
        self.scan_btn = tk.Button(root, text="ЗАПУСТИТЬ СКАНЕР", command=self.start_scan, 
                                  bg="#38bdf8", fg="#0f172a", font=("Arial", 11, "bold"), 
                                  padx=20, pady=10)
        self.scan_btn.pack(pady=10)

    def log(self, message):
        timestamp = datetime.datetime.now().strftime('%H:%M:%S')
        self.log_area.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_area.see(tk.END)
        self.root.update()

    def get_file_hash(self, path):
        sha256 = hashlib.sha256()
        try:
            with open(path, "rb") as f:
                # ТУТ БЫЛА ОШИБКА, ТЕПЕРЬ ОТСТУПЫ ВЕРНЫЕ:
                while True:
                    chunk = f.read(8192)
                    if not chunk:
                        break
                    sha256.update(chunk)
            return sha256.hexdigest()
        except:
            return None

    def move_to_quarantine(self, file_path):
        try:
            q_dir = os.path.join(os.getcwd(), "INFECTED_QUARANTINE")
            if not os.path.exists(q_dir):
                os.makedirs(q_dir)
                if os.name == 'nt':
                    os.system(f'attrib +h +s "{q_dir}"')

            with open(file_path, "rb") as f:
                raw_data = f.read()
            
            encrypted_data = xor_cipher(raw_data)
            secure_name = hashlib.md5(file_path.encode()).hexdigest() + ".dead"
            
            with open(os.path.join(q_dir, secure_name), "wb") as f:
                f.write(encrypted_data)
            
            os.remove(file_path)
            return True
        except:
            return False

    def start_scan(self):
        target_dir = filedialog.askdirectory()
        if not target_dir:
            return
        
        self.log(f"Начало анализа: {target_dir}")
        self.scan_btn.config(state="disabled")

        found_threats = 0
        for root_path, _, files in os.walk(target_dir):
            for filename in files:
                if not filename.lower().endswith(DANGEROUS_EXTS):
                    continue
                
                full_path = os.path.join(root_path, filename)
                f_hash = self.get_file_hash(full_path)
                
                is_virus = f_hash in SIGNATURES
                is_suspicious = filename.count('.') > 1
                
                if is_virus or is_suspicious:
                    found_threats += 1
                    threat_type = SIGNATURES.get(f_hash, "Suspicious.Heuristic")
                    self.log(f"⚠️ НАЙДЕНО: {filename}")
                    
                    user_choice = messagebox.askyesno(
                        "УГРОЗА!", 
                        f"Файл: {filename}\nТип: {threat_type}\n\nВ карантин?"
                    )
                    
                    if user_choice:
                        if self.move_to_quarantine(full_path):
                            self.log(f"✅ Изолирован: {filename}")
                        else:
                            self.log(f"❌ Ошибка изоляции: {filename}")
                    else:
                        self.log(f"❗ Пропущено пользователем: {filename}")

        self.scan_btn.config(state="normal")
        self.log(f"Готово. Угроз: {found_threats}")
        messagebox.showinfo("Сканер", f"Завершено. Найдено: {found_threats}")

if __name__ == "__main__":
    app_root = tk.Tk()
    scanner = ShieldMasterPro(app_root)
    app_root.mainloop()
    
