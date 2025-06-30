# File: ui/add_category_window.py
# Berisi UI untuk pop-up menambah kategori baru.

import customtkinter
from tkinter import messagebox
import database as db

class AddCategoryWindow(customtkinter.CTkToplevel):
    def __init__(self, master, refresh_callback, **kwargs):
        super().__init__(master, **kwargs)

        self.refresh_callback = refresh_callback # Fungsi untuk refresh tabel di frame utama

        # --- Konfigurasi Window ---
        self.title("Tambah Kategori")
        self.geometry("400x220")
        self.resizable(False, False)
        self.configure(fg_color="#FFFFFF")
        self.grab_set() # Membuat window ini modal

        # --- Layout Utama ---
        main_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        main_frame.pack(padx=25, pady=20, fill="both", expand=True)

        customtkinter.CTkLabel(main_frame, text="Tambah Kategori", font=("Inter", 24, "bold"), text_color="gray10").pack(anchor="w", pady=(0, 20))
        
        customtkinter.CTkLabel(main_frame, text="Nama Kategori", font=("Inter", 14, "bold"), text_color="gray30").pack(anchor="w")
        self.category_name_entry = customtkinter.CTkEntry(main_frame, font=("Inter", 16), height=45, corner_radius=8, placeholder_text="Masukkan Nama Kategori...")
        self.category_name_entry.pack(fill="x", pady=5)
        self.category_name_entry.bind("<Return>", self.submit_category) # Bind Enter key

        # --- Tombol Aksi ---
        button_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        button_frame.pack(side="bottom", padx=25, pady=(0, 20), fill="x")
        button_frame.grid_columnconfigure((0, 1), weight=1)

        close_button = customtkinter.CTkButton(button_frame, text="Tutup", command=self.destroy, height=45, font=("Inter", 14, "bold"),
                                               fg_color="#F8F9FA", text_color="gray30", border_width=1.5, border_color="#E0E0E0", hover_color="#E9ECEF")
        close_button.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        submit_button = customtkinter.CTkButton(button_frame, text="Tambah", command=self.submit_category, height=45, font=("Inter", 14, "bold"))
        submit_button.grid(row=0, column=1, padx=(10, 0), sticky="ew")

    def submit_category(self, event=None):
        """Menyimpan kategori baru ke database."""
        category_name = self.category_name_entry.get().strip()

        if not category_name:
            messagebox.showerror("Input Kosong", "Nama kategori tidak boleh kosong.", parent=self)
            return
        
        try:
            db.add_category(category_name)
            messagebox.showinfo("Sukses", f"Kategori '{category_name}' berhasil ditambahkan.", parent=self)
            self.refresh_callback() # Panggil fungsi refresh di frame utama
            self.destroy()
        except Exception as e:
            # Menangani kemungkinan nama kategori sudah ada (UNIQUE constraint)
            if "Duplicate entry" in str(e):
                messagebox.showerror("Error", f"Kategori dengan nama '{category_name}' sudah ada.", parent=self)
            else:
                messagebox.showerror("Database Error", f"Terjadi kesalahan: {e}", parent=self)

