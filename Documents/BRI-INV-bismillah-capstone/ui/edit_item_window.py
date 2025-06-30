# File: ui/edit_item_window.py
# Berisi UI untuk pop-up mengedit barang yang sudah ada.

import customtkinter
from tkinter import messagebox
import database as db
import os

class EditItemWindow(customtkinter.CTkToplevel):
    def __init__(self, master, item_id, refresh_callback, **kwargs):
        super().__init__(master, **kwargs)

        self.item_id = item_id
        self.refresh_callback = refresh_callback
        
        # Ambil data item yang akan diedit dari database
        self.item_data = db.get_item_by_id(self.item_id)
        if not self.item_data:
            messagebox.showerror("Error", "Gagal mengambil data item dari database.", parent=self)
            self.destroy()
            return
            
        # --- Teks Placeholder ---
        self.placeholder_text = "Masukkan Deskripsi Barang..."
        self.is_placeholder_active = True # Untuk melacak status placeholder

        # --- Konfigurasi Window ---
        self.title("Edit Barang")
        self.geometry("500x580")
        self.resizable(False, False)
        self.configure(fg_color="#FFFFFF")
        self.grab_set()

        # --- PERBAIKAN: Membuat konten bisa di-scroll ---
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        scrollable_frame = customtkinter.CTkScrollableFrame(self, fg_color="transparent", border_width=0)
        scrollable_frame.grid(row=0, column=0, sticky="nsew")

        main_frame = customtkinter.CTkFrame(scrollable_frame, fg_color="transparent")
        main_frame.pack(padx=25, pady=20, fill="both", expand=True)

        customtkinter.CTkLabel(main_frame, text="Edit Barang", font=("Inter", 24, "bold"), text_color="gray10").pack(anchor="w", pady=(0, 20))

        # --- Form Input (sudah terisi data lama) ---
        # Nama Barang
        customtkinter.CTkLabel(main_frame, text="Nama Barang", font=("Inter", 14, "bold"), text_color="gray30").pack(anchor="w")
        self.item_name_entry = customtkinter.CTkEntry(main_frame, font=("Inter", 16), height=45, corner_radius=8)
        self.item_name_entry.pack(fill="x", pady=(5, 15))
        self.item_name_entry.insert(0, self.item_data.get('item_name', ''))

        # Deskripsi
        customtkinter.CTkLabel(main_frame, text="Deskripsi", font=("Inter", 14, "bold"), text_color="gray30").pack(anchor="w")
        self.desc_textbox = customtkinter.CTkTextbox(main_frame, font=("Inter", 16), height=100, corner_radius=8, border_width=1, border_color="#D1D5DB")
        self.desc_textbox.pack(fill="x", pady=(5, 15))
        
        # --- PERBAIKAN: Logika Placeholder untuk Textbox ---
        self.desc_textbox.bind("<FocusIn>", self.clear_placeholder)
        self.desc_textbox.bind("<FocusOut>", self.add_placeholder)
        # Panggil add_placeholder di awal untuk mengisi teks
        self.add_placeholder()
        
        # Kategori
        customtkinter.CTkLabel(main_frame, text="Kategori", font=("Inter", 14, "bold"), text_color="gray30").pack(anchor="w")
        self.categories_map = {name: cat_id for cat_id, name in db.get_all_categories()}
        category_names = list(self.categories_map.keys())
        self.category_menu = customtkinter.CTkOptionMenu(main_frame, values=category_names if category_names else ["Tidak ada kategori"], height=45, corner_radius=8, fg_color="#F8F9FA", button_color="#E9ECEF", text_color="gray10")
        self.category_menu.pack(fill="x", pady=(5, 15))
        
        current_category_name = db.get_category_name_by_item_id(self.item_id)
        if current_category_name and current_category_name in category_names:
            self.category_menu.set(current_category_name)

        # Stok
        customtkinter.CTkLabel(main_frame, text="Stok", font=("Inter", 14, "bold"), text_color="gray30").pack(anchor="w")
        self.stock_entry = customtkinter.CTkEntry(main_frame, font=("Inter", 16), height=45, corner_radius=8)
        self.stock_entry.pack(fill="x", pady=(5, 15))
        self.stock_entry.insert(0, str(self.item_data.get('stock', '0')))
        
        # --- Tombol Aksi ---
        button_frame = customtkinter.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(side="bottom", padx=0, pady=(20, 0), fill="x")
        button_frame.grid_columnconfigure((0, 1), weight=1)

        close_button = customtkinter.CTkButton(button_frame, text="Tutup", command=self.destroy, height=45, font=("Inter", 14, "bold"), fg_color="#F8F9FA", text_color="gray30", border_width=1.5, border_color="#E0E0E0", hover_color="#E9ECEF")
        close_button.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        submit_button = customtkinter.CTkButton(button_frame, text="Simpan", command=self.submit_update, height=45, font=("Inter", 14, "bold"))
        submit_button.grid(row=0, column=1, padx=(10, 0), sticky="ew")

    def clear_placeholder(self, event):
        """Hapus teks placeholder saat textbox di-klik."""
        if self.is_placeholder_active:
            self.desc_textbox.delete("1.0", "end")
            self.desc_textbox.configure(text_color=customtkinter.ThemeManager.theme["CTkEntry"]["text_color"]) # Warna teks normal
            self.is_placeholder_active = False

    def add_placeholder(self, event=None):
        """Tambahkan kembali teks placeholder jika textbox kosong."""
        if not self.desc_textbox.get("1.0", "end-1c"):
            # Jika deskripsi awal ada, tampilkan itu. Jika tidak, tampilkan placeholder.
            initial_desc = self.item_data.get('description', '')
            if initial_desc and not self.is_placeholder_active:
                self.desc_textbox.insert("1.0", initial_desc)
                self.desc_textbox.configure(text_color=customtkinter.ThemeManager.theme["CTkEntry"]["text_color"])
                self.is_placeholder_active = False
            else:
                self.desc_textbox.insert("1.0", self.placeholder_text)
                self.desc_textbox.configure(text_color="gray60")
                self.is_placeholder_active = True
        else:
             # Jika ada teks (bukan dari placeholder), pastikan is_placeholder adalah False
             if self.desc_textbox.get("1.0", "end-1c") != self.placeholder_text:
                 self.is_placeholder_active = False

    def submit_update(self):
        """Mengambil data dari form dan mengupdate-nya ke database."""
        name = self.item_name_entry.get().strip()
        desc_raw = self.desc_textbox.get("1.0", "end-1c").strip()
        stock_str = self.stock_entry.get().strip()
        category_name = self.category_menu.get()

        # Jika deskripsi masih placeholder, anggap kosong
        desc = "" if self.is_placeholder_active else desc_raw

        # Validasi
        if not (name and stock_str):
            messagebox.showerror("Input Kosong", "Nama dan Stok tidak boleh kosong.", parent=self)
            return
        if category_name == "Pilih Kategori..." or category_name == "Tidak ada kategori":
            messagebox.showerror("Input Tidak Valid", "Silakan pilih kategori barang yang valid.", parent=self)
            return
        try:
            stock = int(stock_str)
            if stock < 0: raise ValueError
        except ValueError:
            messagebox.showerror("Input Tidak Valid", "Stok harus berupa angka positif.", parent=self)
            return

        cat_id = self.categories_map.get(category_name)
        image_url = self.item_data.get('image_url')

        try:
            db.update_item(self.item_id, name, desc, stock, cat_id, image_url)
            messagebox.showinfo("Sukses", f"Barang '{name}' berhasil diperbarui.", parent=self)
            self.refresh_callback()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Database Error", f"Gagal memperbarui barang: {e}", parent=self)
