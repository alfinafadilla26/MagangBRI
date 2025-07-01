# File: app.py (Versi Lengkap & Fungsional dengan Notifikasi)

import customtkinter
from tkinter import messagebox
import os
from PIL import Image

# Import semua kelas Frame dari folder 'ui'
import database as db
from ui.dashboard_frame import DashboardFrame
from ui.item_frame import ItemFrame
from ui.management_frame import ManagementFrame 
from ui.history_frame import HistoryFrame
from ui.login_window import LoginWindow
from ui.take_item_window import TakeItemWindow
from ui.notification_popup import NotificationPopup
# Pastikan semua file pop-up diimpor
from ui.add_item_window import AddItemWindow
from ui.add_category_window import AddCategoryWindow
from ui.edit_item_window import EditItemWindow
from ui.update_stock_window import UpdateStockWindow

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("Aplikasi Manajemen Inventaris")
        self.geometry("1280x720")
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.is_admin = False
        self.low_stock_items = [] # Untuk menyimpan data notifikasi
        
        # Variabel untuk menyimpan warna tombol
        self.default_button_color = "#297AB9"
        self.active_button_color = "#334155"
        
        self.create_main_layout()

    def create_main_layout(self):
        """Menciptakan layout utama: sidebar dan area konten."""
        # --- Sidebar ---
        self.sidebar_frame = customtkinter.CTkFrame(self, width=250, corner_radius=0, fg_color="#297AB9")
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(2, weight=1)

        logo_frame = customtkinter.CTkFrame(self.sidebar_frame, fg_color="transparent")
        logo_frame.grid(row=0, column=0, padx=20, pady=30)
        
        try:
            logo_path = os.path.join(db.get_base_path(), "assets", "logo_bri.png")
            logo_img = customtkinter.CTkImage(Image.open(logo_path), size=(120,40))
            customtkinter.CTkLabel(logo_frame, image=logo_img, text="").pack()
        except Exception:
            customtkinter.CTkLabel(logo_frame, text="BRI INV", font=("Arial", 24, "bold"), text_color="white").pack()

        nav_frame = customtkinter.CTkFrame(self.sidebar_frame, fg_color="transparent")
        nav_frame.grid(row=1, column=0, sticky="ew", padx=20)
        nav_frame.grid_columnconfigure(0, weight=1)

        self.dashboard_button = customtkinter.CTkButton(nav_frame, text="Dashboard", height=45, corner_radius=8, command=lambda: self.select_frame_by_name("dashboard"))
        self.dashboard_button.grid(row=0, column=0, sticky="ew", pady=5)       
        
        self.barang_button = customtkinter.CTkButton(nav_frame, text="Barang", height=45, corner_radius=8, command=lambda: self.select_frame_by_name("items"))
        self.barang_button.grid(row=1, column=0, sticky="ew", pady=5)
        
        self.management_button = customtkinter.CTkButton(nav_frame, text="Manajemen Barang", height=45, corner_radius=8, command=lambda: self.select_frame_by_name("management"))
        self.history_button = customtkinter.CTkButton(nav_frame, text="Riwayat", height=45, corner_radius=8, command=lambda: self.select_frame_by_name("history"))

        # Tombol Notifikasi di Sidebar
        try:
            bell_icon = customtkinter.CTkImage(Image.open(os.path.join(db.get_base_path(), "assets", "icons", "bell_icon.png")), size=(20, 20))
        except:
            bell_icon = None
        self.notification_button = customtkinter.CTkButton(nav_frame, text="Notifikasi", image=bell_icon, height=45, corner_radius=8, fg_color="#0354E9", hover_color="#FFFFFF", command=self.show_notification_popup)
        # Tombol ini akan ditampilkan/disembunyikan oleh update_ui_for_login_status

        self.login_logout_frame = customtkinter.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.login_logout_frame.grid(row=3, column=0, padx=20, pady=20, sticky="s")
        self.login_logout_frame.grid_columnconfigure(0, weight=1)

        self.login_button = customtkinter.CTkButton(self.login_logout_frame, text="MASUK", height=45, corner_radius=8, command=self.open_login_window)
        self.logout_button = customtkinter.CTkButton(self.login_logout_frame, text="Log out", height=45, corner_radius=8, fg_color="#D9534F", hover_color="#C9302C", command=self.logout)

        # --- Main Content Area ---
        # --- PERBAIKAN: fg_color diatur agar sama dengan warna latar utama, dan hapus corner_radius ---
        self.main_frame = customtkinter.CTkFrame(self, fg_color="#FDFDFD", corner_radius=0)
        # --- PERBAIKAN: Hapus padding (padx, pady) agar tidak ada celah ---
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Membuat instance semua halaman (sekarang master-nya adalah self.main_frame)
        self.dashboard_frame = DashboardFrame(self.main_frame, explore_callback=lambda: self.select_frame_by_name("items"))
        self.item_frame = ItemFrame(self.main_frame, app=self)
        self.management_frame = ManagementFrame(self.main_frame)
        self.history_frame = HistoryFrame(self.main_frame)

        self.update_ui_for_login_status()
        self.select_frame_by_name("dashboard")

    def select_frame_by_name(self, name):
        """Menyembunyikan semua frame dan menampilkan yang dipilih."""
        self.dashboard_button.configure(fg_color=self.default_button_color)
        self.barang_button.configure(fg_color=self.default_button_color)
        self.management_button.configure(fg_color=self.default_button_color)
        self.history_button.configure(fg_color=self.default_button_color)

        self.dashboard_frame.grid_forget()
        self.item_frame.grid_forget()
        self.management_frame.grid_forget()
        self.history_frame.grid_forget()

        if name == "dashboard":
            self.dashboard_frame.grid(row=0, column=0, sticky="nsew")
            self.dashboard_button.configure(fg_color=self.active_button_color)
        elif name == "items":
            self.item_frame.grid(row=0, column=0, sticky="nsew")
            self.item_frame.refresh_data()
            self.barang_button.configure(fg_color=self.active_button_color)
        elif name == "management" and self.is_admin:
            self.management_frame.grid(row=0, column=0, sticky="nsew")
            self.management_frame.refresh_all_tables()
            self.management_button.configure(fg_color=self.active_button_color)
        elif name == "history" and self.is_admin:
            self.history_frame.grid(row=0, column=0, sticky="nsew")
            self.history_frame.refresh_history_table()
            self.history_button.configure(fg_color=self.active_button_color)
        
        if self.is_admin:
            self.check_notifications()

    def update_ui_for_login_status(self):
        """Menampilkan atau menyembunyikan tombol berdasarkan status admin."""
        self.login_button.grid_forget()
        self.logout_button.grid_forget()
        self.management_button.grid_forget()
        self.history_button.grid_forget()
        self.notification_button.grid_forget() 

        if self.is_admin:
            self.management_button.grid(row=2, column=0, sticky="ew", pady=5)
            self.history_button.grid(row=3, column=0, sticky="ew", pady=5)
            self.logout_button.grid(row=0, column=0, sticky="ew")
            self.check_notifications()
        else:
            self.login_button.grid(row=0, column=0, sticky="ew")

    def check_notifications(self):
        """Mengecek item dengan stok rendah dan menampilkan tombol notifikasi."""
        
        self.low_stock_items = db.get_low_stock_items(threshold=5)
        count = len(self.low_stock_items)
        
        self.notification_button.grid_forget()
        if count > 0 and self.is_admin:
            self.notification_button.configure(text=f"Notifikasi ({count})")
            self.notification_button.grid(row=4, column=0, sticky="ew", pady=(15,5))

    def show_notification_popup(self):
        """Menampilkan pop-up notifikasi."""
        NotificationPopup(master=self, low_stock_items=self.low_stock_items)

    def open_login_window(self):
        """Membuka jendela pop-up untuk login."""
        LoginWindow(master=self, success_callback=self.successful_login)

    def successful_login(self):
        """Dipanggil setelah login dari LoginWindow berhasil."""
        self.is_admin = True
        self.update_ui_for_login_status()
        self.select_frame_by_name("dashboard")
        messagebox.showinfo("Login Berhasil", "Selamat datang, Admin!")
    
    def open_take_item_window_by_id(self, item_id):
        """Membuka jendela pop-up untuk mengambil barang."""
        TakeItemWindow(master=self, item_id=item_id, item_frame_ref=self.item_frame)

    def logout(self):
        """Proses untuk logout admin."""
        if messagebox.askyesno("Konfirmasi Logout", "Apakah Anda yakin ingin logout?"):
            self.is_admin = False
            self.update_ui_for_login_status()
            self.select_frame_by_name("dashboard")

# --- Bagian Eksekusi Utama ---
if __name__ == "__main__":
    try:
        db.create_tables()
        db.setup_default_admin()
        
        app = App()
        app.mainloop()
    except Exception as e:
        messagebox.showerror("Fatal Error", f"Gagal memulai aplikasi:\n{e}")
