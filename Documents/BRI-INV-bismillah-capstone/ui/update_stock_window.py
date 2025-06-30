# File: ui/update_stock_window.py
# Berisi UI untuk pop-up menambah atau mengurangi stok (Barang Masuk/Keluar).

import customtkinter
from tkinter import messagebox
import database as db
from PIL import Image
import os
import logging

class UpdateStockWindow(customtkinter.CTkToplevel):
    def __init__(self, master, item_id, refresh_callback, **kwargs):
        super().__init__(master, **kwargs)

        self.item_id = item_id
        self.refresh_callback = refresh_callback
        self.transaction_type = None  # 'masuk' atau 'keluar'

        self.item_data = db.get_item_by_id(self.item_id)
        if not self.item_data:
            messagebox.showerror("Error", "Gagal mengambil data item.", parent=self)
            self.destroy()
            return

        # --- Konfigurasi Window ---
        self.title("Update Status Barang")
        self.geometry("450x420") # Tinggi disesuaikan
        self.resizable(False, False)
        self.configure(fg_color="#FFFFFF")
        self.grab_set()

        # --- PERBAIKAN: Layout utama menggunakan grid untuk scroll ---
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.create_widgets()

    def get_asset_path(self, *paths):
        return os.path.join(db.get_base_path(), "assets", *paths)

    def create_widgets(self):
        # --- PERBAIKAN: Membuat frame utama yang bisa di-scroll ---
        scroll_frame = customtkinter.CTkScrollableFrame(self, fg_color="transparent", border_width=0)
        scroll_frame.grid(row=0, column=0, sticky="nsew")

        # Frame konten untuk padding di dalam scrollable frame
        main_frame = customtkinter.CTkFrame(scroll_frame, fg_color="transparent")
        main_frame.pack(padx=25, pady=20, fill="both", expand=True)

        customtkinter.CTkLabel(main_frame, text="Status Barang", font=("Inter", 24, "bold"), text_color="gray10").pack(anchor="w", pady=(0, 20))

        # --- Nama Barang (Read-only) ---
        customtkinter.CTkLabel(main_frame, text="Nama Barang", font=("Inter", 14, "bold"), text_color="gray30").pack(anchor="w")
        name_entry = customtkinter.CTkEntry(main_frame, font=("Inter", 16), height=45, corner_radius=8)
        name_entry.pack(fill="x", pady=(5, 15))
        name_entry.insert(0, self.item_data.get('item_name', ''))
        name_entry.configure(state="disabled", fg_color="#F8F9FA")

        # --- Pilihan Status (Barang Masuk / Keluar) ---
        customtkinter.CTkLabel(main_frame, text="Status", font=("Inter", 14, "bold"), text_color="gray30").pack(anchor="w")
        status_frame = customtkinter.CTkFrame(main_frame, fg_color="transparent")
        status_frame.pack(fill="x", pady=5)
        status_frame.grid_columnconfigure((0, 1), weight=1)

        # Tombol Barang Masuk
        self.btn_masuk = customtkinter.CTkButton(status_frame, text="Barang Masuk", height=60, border_width=1.5, text_color="#16A34A", border_color="#D1D5DB", fg_color="transparent", hover_color="#F0FBF4", command=lambda: self.select_status('masuk'))
        self.btn_masuk.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        # Tombol Barang Keluar
        self.btn_keluar = customtkinter.CTkButton(status_frame, text="Barang Keluar", height=60, border_width=1.5, text_color="#EF4444", border_color="#D1D5DB", fg_color="transparent", hover_color="#FFF1F2", command=lambda: self.select_status('keluar'))
        self.btn_keluar.grid(row=0, column=1, sticky="ew", padx=(10, 0))
        
        # --- Input Jumlah ---
        customtkinter.CTkLabel(main_frame, text="Jumlah", font=("Inter", 14, "bold"), text_color="gray30").pack(anchor="w", pady=(15, 0))
        self.quantity_entry = customtkinter.CTkEntry(main_frame, font=("Inter", 16), height=45, corner_radius=8, placeholder_text="Masukkan jumlah...")
        self.quantity_entry.pack(fill="x", pady=5)
        
        # --- Tombol Aksi ---
        # --- PERBAIKAN: Tombol dimasukkan ke dalam main_frame agar bisa di-scroll ---
        button_frame = customtkinter.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(side="bottom", padx=0, pady=(20, 0), fill="x")
        button_frame.grid_columnconfigure((0, 1), weight=1)

        close_button = customtkinter.CTkButton(button_frame, text="Tutup", command=self.destroy, height=45, font=("Inter", 14, "bold"), fg_color="#F8F9FA", text_color="gray30", border_width=1.5, border_color="#E0E0E0", hover_color="#E9ECEF")
        close_button.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        
        submit_button = customtkinter.CTkButton(button_frame, text="Simpan", command=self.submit_update, height=45, font=("Inter", 14, "bold"))
        submit_button.grid(row=0, column=1, padx=(10, 0), sticky="ew")

    def select_status(self, trans_type):
        self.transaction_type = trans_type
        if trans_type == 'masuk':
            self.btn_masuk.configure(border_color="#22C55E", fg_color="#F0FBF4")
            self.btn_keluar.configure(border_color="#D1D5DB", fg_color="transparent")
        else: # keluar
            self.btn_keluar.configure(border_color="#EF4444", fg_color="#FFF1F2")
            self.btn_masuk.configure(border_color="#D1D5DB", fg_color="transparent")

    def submit_update(self):
        if self.transaction_type is None:
            messagebox.showerror("Input Tidak Valid", "Silakan pilih status (Barang Masuk / Barang Keluar).", parent=self)
            return
        try:
            quantity = int(self.quantity_entry.get())
            if quantity <= 0: raise ValueError
        except ValueError:
            messagebox.showerror("Input Tidak Valid", "Jumlah harus berupa angka positif.", parent=self)
            return

        try:
            # Panggil fungsi baru di database
            db.adjust_stock(self.item_id, quantity, self.transaction_type)
            messagebox.showinfo("Sukses", "Stok berhasil diperbarui.", parent=self)
            self.refresh_callback()
            self.destroy()
        except ValueError as ve: # Khusus untuk error stok tidak cukup
             messagebox.showerror("Stok Tidak Cukup", str(ve), parent=self)
        except Exception as e:
            messagebox.showerror("Database Error", f"Gagal memperbarui stok: {e}", parent=self)

