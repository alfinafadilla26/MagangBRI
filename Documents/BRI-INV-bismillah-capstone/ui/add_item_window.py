# File: ui/add_item_window.py
# Berisi UI untuk pop-up menambah barang baru dengan logika update jika sudah ada.

import customtkinter
from tkinter import messagebox
import database as db
import os

class AddItemWindow(customtkinter.CTkToplevel):
    def __init__(self, master, refresh_callback, **kwargs):
        super().__init__(master, **kwargs)

        self.refresh_callback = refresh_callback

        self.placeholder_text = "Masukkan Deskripsi Barang..."

        # --- Konfigurasi Window ---
        self.title("Tambah Barang")
        self.geometry("500x580")
        self.resizable(False, False)
        self.configure(fg_color="#FFFFFF")
        self.grab_set()

        self.main_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(padx=25, pady=20, fill="both", expand=True)

        self.create_widgets()

    def create_widgets(self):
        """Membuat semua widget di jendela pop-up."""
        customtkinter.CTkLabel(self.main_frame, text="Tambah Barang", font=("Inter", 24, "bold"), text_color="gray10").pack(anchor="w", pady=(0, 20))

        # Nama Barang
        customtkinter.CTkLabel(self.main_frame, text="Nama Barang", font=("Inter", 14, "bold"), text_color="gray30").pack(anchor="w")
        self.item_name_entry = customtkinter.CTkEntry(self.main_frame, font=("Inter", 16), height=45, corner_radius=8, placeholder_text="Masukkan Nama Barang...")
        self.item_name_entry.pack(fill="x", pady=(5, 15))

        # Deskripsi
        customtkinter.CTkLabel(self.main_frame, text="Deskripsi", font=("Inter", 14, "bold"), text_color="gray30").pack(anchor="w")
        self.desc_textbox = customtkinter.CTkTextbox(self.main_frame, font=("Inter", 16), height=100, corner_radius=8, border_width=1, border_color="#D1D5DB")
        self.desc_textbox.pack(fill="x", pady=(5, 15))
        self.desc_textbox.insert("1.0", self.placeholder_text)
        self.desc_textbox.configure(text_color="gray60")
        self.desc_textbox.bind("<FocusIn>", self.clear_placeholder)
        self.desc_textbox.bind("<FocusOut>", self.add_placeholder)

        # Kategori
        customtkinter.CTkLabel(self.main_frame, text="Kategori", font=("Inter", 14, "bold"), text_color="gray30").pack(anchor="w")
        self.categories_map = {name: cat_id for cat_id, name in db.get_all_categories()}
        category_names = ["Pilih Kategori..."] + list(self.categories_map.keys())
        self.category_menu = customtkinter.CTkOptionMenu(self.main_frame, values=category_names, height=45, corner_radius=8, fg_color="#F8F9FA", button_color="#E9ECEF", text_color="gray10")
        self.category_menu.pack(fill="x", pady=(5, 15))

        # Stok
        customtkinter.CTkLabel(self.main_frame, text="Stok", font=("Inter", 14, "bold"), text_color="gray30").pack(anchor="w")
        self.stock_entry = customtkinter.CTkEntry(self.main_frame, font=("Inter", 16), height=45, corner_radius=8, placeholder_text="Masukkan Stok Barang... (E.x. 2)")
        self.stock_entry.pack(fill="x", pady=(5, 15))

        # Tombol Aksi
        button_frame = customtkinter.CTkFrame(self.main_frame, fg_color="transparent")
        button_frame.pack(side="bottom", padx=0, pady=(20, 0), fill="x")
        button_frame.grid_columnconfigure((0, 1), weight=1)

        close_button = customtkinter.CTkButton(button_frame, text="Tutup", command=self.destroy, height=45, font=("Inter", 14, "bold"), fg_color="#F8F9FA", text_color="gray30", border_width=1.5, border_color="#E0E0E0", hover_color="#E9ECEF")
        close_button.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        submit_button = customtkinter.CTkButton(button_frame, text="Tambah", command=self.submit_item, height=45, font=("Inter", 14, "bold"))
        submit_button.grid(row=0, column=1, padx=(10, 0), sticky="ew")

    def clear_placeholder(self, event):
        """Hapus teks placeholder saat textbox di-klik."""
        if self.desc_textbox.get("1.0", "end-1c").strip() == self.placeholder_text:
            self.desc_textbox.delete("1.0", "end")
            self.desc_textbox.configure(text_color=customtkinter.ThemeManager.theme["CTkEntry"]["text_color"])

    def add_placeholder(self, event):
        """Tambahkan kembali teks placeholder jika textbox kosong."""
        if not self.desc_textbox.get("1.0", "end-1c").strip():
            self.desc_textbox.insert("1.0", self.placeholder_text)
            self.desc_textbox.configure(text_color="gray60")

    def submit_item(self):
        """Mengambil data dari form dan menyimpannya ke database,
           dengan pengecekan duplikasi nama untuk update otomatis."""
        name = self.item_name_entry.get().strip()
        desc = self.desc_textbox.get("1.0", "end-1c").strip()
        stock_str = self.stock_entry.get().strip()
        category_name = self.category_menu.get()
        
        # Validasi dasar
        if not (name and stock_str):
            messagebox.showerror("Input Kosong", "Nama Barang dan Stok tidak boleh kosong.", parent=self)
            return
        if category_name == "Pilih Kategori...":
            messagebox.showerror("Input Tidak Valid", "Silakan pilih kategori barang.", parent=self)
            return
        try:
            stock_to_add = int(stock_str)
            if stock_to_add <= 0: raise ValueError
        except ValueError:
            messagebox.showerror("Input Tidak Valid", "Stok harus berupa angka positif.", parent=self)
            return
            
        # Jika deskripsi masih placeholder, anggap kosong
        if desc == self.placeholder_text:
            desc = ""

        try:
            # Cek apakah item dengan nama yang sama sudah ada
            existing_item = db.find_item_by_name(name)
            
            if existing_item:
                # Jika ada, update stoknya (barang masuk)
                item_id = existing_item['item_id']
                db.adjust_stock(item_id, stock_to_add, 'masuk')
                messagebox.showinfo("Sukses", f"Stok untuk '{name}' berhasil ditambahkan.", parent=self)
            else:
                # Jika tidak ada, buat item baru
                cat_id = self.categories_map.get(category_name)
                db.add_item(name, desc, stock_to_add, cat_id, None)
                messagebox.showinfo("Sukses", f"Barang baru '{name}' berhasil ditambahkan.", parent=self)
            
            self.refresh_callback()
            self.destroy()

        except Exception as e:
            messagebox.showerror("Database Error", f"Terjadi kesalahan: {e}", parent=self)
