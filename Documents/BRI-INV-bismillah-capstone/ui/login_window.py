# File: ui/login_window.py (File Baru)

import customtkinter
from PIL import Image
import os
import database as db
from tkinter import messagebox
import logging

class LoginWindow(customtkinter.CTkToplevel):
    def __init__(self, master, success_callback, **kwargs):
        super().__init__(master, **kwargs)

        self.master_app = master  # Referensi ke jendela aplikasi utama
        self.success_callback = success_callback # Fungsi yang dipanggil jika login berhasil

        # --- Konfigurasi Window ---
        self.title("BRI-INV Login")
        self.geometry("800x500")
        self.resizable(False, False)
        self.configure(fg_color="#FFFFFF")
        self.grab_set() # Membuat window ini modal (fokus)

        # --- Layout Utama: 2 Kolom ---
        self.grid_columnconfigure(0, weight=1) # Kolom kiri (form)
        self.grid_columnconfigure(1, weight=1) # Kolom kanan (gambar)
        self.grid_rowconfigure(0, weight=1)

        self.create_widgets()

    def get_asset_path(self, *paths):
        """Helper untuk mendapatkan path absolut ke folder assets."""
        return os.path.join(db.get_base_path(), "assets", *paths)

    def create_widgets(self):
        """Membuat semua widget di jendela login."""
        # --- Kolom Kiri (Form Login) ---
        left_frame = customtkinter.CTkFrame(self, fg_color="#FFFFFF", corner_radius=0)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(60, 30), pady=40)
        left_frame.grid_columnconfigure(0, weight=1)

        # Header
        customtkinter.CTkLabel(left_frame, text="Masuk", font=("Inter", 32, "bold"), text_color="gray10").pack(anchor="w", pady=(20, 40))

        # Form
        customtkinter.CTkLabel(left_frame, text="Personal Number", font=("Inter", 14, "bold"), text_color="gray30").pack(anchor="w")
        self.pn_entry = customtkinter.CTkEntry(left_frame, font=("Inter", 16), height=45, corner_radius=8, border_color="#D1D5DB")
        self.pn_entry.pack(fill="x", pady=(5, 20))

        customtkinter.CTkLabel(left_frame, text="Password", font=("Inter", 14, "bold"), text_color="gray30").pack(anchor="w")
        self.password_entry = customtkinter.CTkEntry(left_frame, font=("Inter", 16), height=45, corner_radius=8, border_color="#D1D5DB", show="*")
        self.password_entry.pack(fill="x", pady=5)
        
        # Bind tombol Enter untuk attempt_login
        self.password_entry.bind("<Return>", self.attempt_login)

        # Tombol Masuk
        login_button = customtkinter.CTkButton(left_frame, text="Masuk", command=self.attempt_login, font=("Inter", 16, "bold"), height=50, corner_radius=8, fg_color="#0E69B0")
        login_button.pack(fill="x", pady=(40, 0))

        # --- Kolom Kanan (Gambar Latar & Logo) ---
        right_frame = customtkinter.CTkFrame(self, fg_color="#0E69B0", corner_radius=0)
        right_frame.grid(row=0, column=1, sticky="nsew")
        right_frame.grid_propagate(False)
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(0, weight=1)

        try:
            # Gunakan gambar latar belakang jika ada
            bg_image = customtkinter.CTkImage(Image.open(self.get_asset_path("logo_kanan_login.png")), size=(265, 291))
            bg_label = customtkinter.CTkLabel(right_frame, image=bg_image, text="")
            bg_label.place(relx=0.5, rely=0.5, anchor="center")
        except Exception:
            # Jika tidak ada, hanya warna solid
            pass 

        try:
            logo_image = customtkinter.CTkImage(Image.open(self.get_asset_path("logo_E.png")), size=(150, 150))
            logo_label = customtkinter.CTkLabel(right_frame, image=logo_image, text="", fg_color="transparent")
            logo_label.place(relx=0.5, rely=0.5, anchor="center")
        except Exception as e:
            logging.warning(f"Gambar logo 'logo_E.png' tidak ditemukan: {e}")
            customtkinter.CTkLabel(right_frame, text="BRI\nINV", font=("Inter", 40, "bold"), text_color="white").place(relx=0.5, rely=0.5, anchor="center")
            
    def attempt_login(self, event=None):
        """Mencoba untuk login dengan data dari form."""
        personal_number = self.pn_entry.get()
        password = self.password_entry.get()

        if not personal_number or not password:
            messagebox.showerror("Login Gagal", "Personal Number dan Password tidak boleh kosong.", parent=self)
            return

        is_valid = db.verify_admin(personal_number, password)

        if is_valid:
            self.success_callback() # Panggil fungsi sukses dari App
            self.destroy() # Tutup jendela login
        else:
            messagebox.showerror("Login Gagal", "Personal Number atau Password salah.", parent=self)
