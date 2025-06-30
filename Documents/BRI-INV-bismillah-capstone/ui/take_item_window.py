# File: ui/take_item_window.py
# Berisi UI untuk pop-up mengambil barang.

import customtkinter
from tkinter import messagebox
import database as db
from PIL import Image
import os
import logging

class TakeItemWindow(customtkinter.CTkToplevel):
    def __init__(self, master, item_id, item_frame_ref, **kwargs):
        super().__init__(master, **kwargs)

        self.app = master
        self.item_id = item_id
        self.item_frame = item_frame_ref # Referensi untuk me-refresh tabel item

        # Ambil data item dari database
        self.item_data = db.get_item_by_id(self.item_id)
        if not self.item_data:
            messagebox.showerror("Error", "Item tidak ditemukan di database.")
            self.destroy()
            return

        # --- Konfigurasi Window ---
        self.title("Status Barang")
        # --- PERBAIKAN: Tinggi jendela ditambah sedikit ---
        self.geometry("450x550")
        self.resizable(False, False)
        self.configure(fg_color="#FFFFFF")
        self.grab_set()

        # --- PERBAIKAN: Konfigurasi grid untuk scrollable frame ---
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.create_widgets()

    def get_asset_path(self, *paths):
        """Helper untuk mendapatkan path absolut ke folder assets."""
        return os.path.join(db.get_base_path(), "assets", *paths)

    def create_widgets(self):
        """Membuat semua widget di dalam frame yang bisa di-scroll."""
        
        # --- PERBAIKAN: Membuat frame utama yang bisa di-scroll ---
        scroll_frame = customtkinter.CTkScrollableFrame(self, fg_color="transparent", border_width=0)
        scroll_frame.grid(row=0, column=0, sticky="nsew")
        
        # Frame konten untuk padding di dalam scrollable frame
        main_frame = customtkinter.CTkFrame(scroll_frame, fg_color="transparent")
        main_frame.pack(padx=25, pady=20, fill="both", expand=True)


        # --- Judul Window ---
        customtkinter.CTkLabel(main_frame, text="Status Barang", font=("Inter", 24, "bold"), text_color="gray10").pack(anchor="w", pady=(0, 20))

        # --- Nama Barang (Read-only) ---
        customtkinter.CTkLabel(main_frame, text="Nama Barang", font=("Inter", 14, "bold"), text_color="gray30").pack(anchor="w")
        self.item_name_entry = customtkinter.CTkEntry(main_frame, font=("Inter", 16), height=45, corner_radius=8, border_color="#D1D5DB")
        self.item_name_entry.pack(fill="x", pady=(5, 15))
        self.item_name_entry.insert(0, self.item_data['item_name'])
        self.item_name_entry.configure(state="disabled", fg_color="#F8F9FA")

        # --- Status Barang Keluar ---
        customtkinter.CTkLabel(main_frame, text="Status", font=("Inter", 14, "bold"), text_color="gray30").pack(anchor="w")
        status_frame = customtkinter.CTkFrame(main_frame, fg_color="transparent", border_color="#D9534F", border_width=1.5, corner_radius=10)
        status_frame.pack(fill="x", pady=5)
        
        try:
            icon_image = customtkinter.CTkImage(Image.open(self.get_asset_path("icons", "box_out_icon.png")), size=(32, 32))
            icon_label = customtkinter.CTkLabel(status_frame, image=icon_image, text="")
            icon_label.pack(side="left", padx=15, pady=12)
        except Exception as e:
            logging.warning(f"Icon status tidak ditemukan: {e}")

        status_text_frame = customtkinter.CTkFrame(status_frame, fg_color="transparent")
        status_text_frame.pack(side="left", padx=(0, 15), pady=12, fill="x")
        
        customtkinter.CTkLabel(status_text_frame, text="Barang Keluar", font=("Inter", 16, "bold"), text_color="#D9534F").pack(anchor="w")
        customtkinter.CTkLabel(status_text_frame, text="Terdapat Barang Yang Keluar", font=("Inter", 12), text_color="gray40").pack(anchor="w")


        # --- Input Jumlah ---
        customtkinter.CTkLabel(main_frame, text="Jumlah", font=("Inter", 14, "bold"), text_color="gray30").pack(anchor="w", pady=(15, 0))
        self.quantity_entry = customtkinter.CTkEntry(main_frame, font=("Inter", 16), height=45, corner_radius=8, border_color="#D1D5DB", placeholder_text=f"Stok tersedia: {self.item_data['stock']}")
        self.quantity_entry.pack(fill="x", pady=5)

        # --- Input Nama Pengguna ---
        customtkinter.CTkLabel(main_frame, text="Nama Pengguna", font=("Inter", 14, "bold"), text_color="gray30").pack(anchor="w", pady=(15, 0))
        self.user_name_entry = customtkinter.CTkEntry(main_frame, font=("Inter", 16), height=45, corner_radius=8, border_color="#D1D5DB", placeholder_text="Masukkan nama Anda")
        self.user_name_entry.pack(fill="x", pady=5)
        self.user_name_entry.bind("<Return>", self.submit_action) # Bind Enter
        
        # --- Tombol Aksi ---
        # --- PERBAIKAN: Tombol dimasukkan ke dalam main_frame agar bisa di-scroll ---
        button_frame = customtkinter.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(side="bottom", padx=0, pady=(20, 0), fill="x")
        button_frame.grid_columnconfigure((0, 1), weight=1)

        close_button = customtkinter.CTkButton(button_frame, text="Tutup", command=self.destroy, height=45, font=("Inter", 14, "bold"),
                                               fg_color="#F8F9FA", text_color="gray30", border_width=1.5, border_color="#E0E0E0", hover_color="#E9ECEF")
        close_button.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        submit_button = customtkinter.CTkButton(button_frame, text="Kirim", command=self.submit_action, height=45, font=("Inter", 14, "bold"))
        submit_button.grid(row=0, column=1, padx=(10, 0), sticky="ew")

    def submit_action(self, event=None):
        """Fungsi yang dijalankan saat tombol Kirim ditekan."""
        try:
            quantity_to_take = int(self.quantity_entry.get())
        except ValueError:
            messagebox.showerror("Input Tidak Valid", "Jumlah harus berupa angka.", parent=self)
            return

        user_name = self.user_name_entry.get().strip()
        current_stock = self.item_data['stock']

        # Validasi Input
        if not user_name:
            messagebox.showerror("Input Kosong", "Nama pengguna tidak boleh kosong.", parent=self)
            return
        if quantity_to_take <= 0:
            messagebox.showerror("Input Tidak Valid", "Jumlah barang yang diambil harus lebih dari 0.", parent=self)
            return
        if quantity_to_take > current_stock:
            messagebox.showerror("Stok Tidak Cukup", f"Stok barang tidak mencukupi. Stok tersedia: {current_stock}", parent=self)
            return

        # Proses ke database
        try:
            # Fungsi take_item sudah mencakup update stok dan pencatatan riwayat
            success = db.take_item(self.item_id, quantity_to_take, user_name)
            
            if success:
                messagebox.showinfo("Sukses", "Transaksi berhasil dicatat!", parent=self)
                self.item_frame.refresh_data() # Refresh halaman barang
                self.destroy()
            else:
                # Ini terjadi jika stok berubah setelah window dibuka
                 messagebox.showerror("Gagal", "Gagal memproses transaksi. Stok mungkin sudah tidak cukup.", parent=self)
        except Exception as e:
            messagebox.showerror("Database Error", f"Terjadi kesalahan saat memproses transaksi: {e}", parent=self)
