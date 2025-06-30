# File: ui/management_frame.py
# Berisi UI untuk halaman manajemen barang oleh Admin.

import customtkinter
from PIL import Image
import os
import database as db
import logging
from tkinter import messagebox
# --- Impor semua kelas window pop-up ---
from ui.add_item_window import AddItemWindow
from ui.add_category_window import AddCategoryWindow
from ui.edit_item_window import EditItemWindow 
from ui.update_stock_window import UpdateStockWindow

class ManagementFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.configure(fg_color="#FDFDFD")
        
        # Konfigurasi grid utama
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.category_widgets = {}

        self.create_widgets()

    def get_asset_path(self, *paths):
        """Helper untuk mendapatkan path absolut ke folder assets."""
        return os.path.join(db.get_base_path(), "assets", *paths)

    def create_widgets(self):
        """Membuat semua widget UI awal untuk halaman ini."""
        # --- Top Bar ---
        top_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        top_frame.grid(row=0, column=0, sticky="ew", padx=30, pady=20)
        top_frame.grid_columnconfigure(1, weight=1) # Spacer

        # Tombol Aksi
        action_button_frame = customtkinter.CTkFrame(top_frame, fg_color="transparent")
        action_button_frame.grid(row=0, column=2, sticky="e")

        add_item_button = customtkinter.CTkButton(action_button_frame, text="+ Tambah Barang", command=self.add_item_popup)
        add_item_button.pack(side="left", padx=10)
        
        add_category_button = customtkinter.CTkButton(action_button_frame, text="+ Tambah Kategori", command=self.add_category_popup)
        add_category_button.pack(side="left")

        # Admin Info
        admin_frame = customtkinter.CTkFrame(top_frame, fg_color="transparent")
        admin_frame.grid(row=0, column=0, sticky="w")
        try:
            user_icon = customtkinter.CTkImage(Image.open(self.get_asset_path("icons", "user_icon.png")), size=(24,24))
            customtkinter.CTkLabel(admin_frame, image=user_icon, text="").pack(side="right", padx=(10,0))
        except Exception:
            pass
        
        admin_text_frame = customtkinter.CTkFrame(admin_frame, fg_color="transparent")
        admin_text_frame.pack(side="right")
        customtkinter.CTkLabel(admin_text_frame, text="Halo, Niken", font=("Inter", 14)).pack(anchor="e")
        customtkinter.CTkLabel(admin_text_frame, text="Super Admin", font=("Inter", 12, "bold"), text_color="gray50").pack(anchor="e")

        # --- Area Daftar Item ---
        self.scrollable_frame = customtkinter.CTkScrollableFrame(self, fg_color="transparent", border_width=0)
        self.scrollable_frame.grid(row=1, column=0, sticky="nsew", padx=30)
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

    def refresh_all_tables(self):
        """Mengambil data baru dari DB dan membangun ulang seluruh tampilan."""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.category_widgets.clear()
        
        categories = db.get_all_categories()
        if not categories:
            customtkinter.CTkLabel(self.scrollable_frame, text="Belum ada kategori. Silakan tambahkan kategori baru.").pack(pady=20)
            return

        for i, (cat_id, cat_name) in enumerate(categories):
            self.create_category_accordion(cat_id, cat_name, i)

    def create_category_accordion(self, cat_id, cat_name, row_index):
        """Membuat satu bagian accordion untuk sebuah kategori."""
        header_frame = customtkinter.CTkFrame(self.scrollable_frame, fg_color="#F1F5F9", height=50, corner_radius=8, cursor="hand2")
        header_frame.grid(row=row_index * 2, column=0, sticky="ew", pady=(10,0))
        header_frame.grid_columnconfigure(1, weight=1)
        
        customtkinter.CTkLabel(header_frame, text=cat_name, font=("Inter", 16, "bold"), text_color="#1E293B").grid(row=0, column=1, padx=20, sticky="w")
        
        arrow_label = customtkinter.CTkLabel(header_frame, text="v", font=("Inter", 16, "bold"))
        arrow_label.grid(row=0, column=2, padx=20)

        content_frame = customtkinter.CTkFrame(self.scrollable_frame, fg_color="transparent")
        
        self.category_widgets[cat_id] = {
            "header": header_frame, "content": content_frame,
            "arrow": arrow_label, "is_expanded": False,
            "row": row_index * 2 + 1
        }

        items = db.get_items_by_category(cat_id)
        if not items:
            customtkinter.CTkLabel(content_frame, text="Tidak ada item di kategori ini.", text_color="gray50").pack(pady=10)
        else:
            for item_data in items:
                self.create_item_row(content_frame, item_data)
        
        header_frame.bind("<Button-1>", lambda e, c_id=cat_id: self.toggle_accordion(c_id))
        for child in header_frame.winfo_children():
            child.bind("<Button-1>", lambda e, c_id=cat_id: self.toggle_accordion(c_id))

    def toggle_accordion(self, cat_id):
        """Membuka atau menutup accordion."""
        category = self.category_widgets.get(cat_id)
        if not category: return

        if category["is_expanded"]:
            category["content"].grid_forget()
            category["arrow"].configure(text="v")
            category["is_expanded"] = False
        else:
            category["content"].grid(row=category["row"], column=0, sticky="ew", padx=10, pady=(0,10))
            category["arrow"].configure(text="^")
            category["is_expanded"] = True

    def create_item_row(self, parent, item_data):
        """Membuat satu baris untuk sebuah item."""
        if len(item_data) < 8: return
        
        item_id, item_name, cat_name, stock, desc, created_at, image_url, cat_id = item_data
        
        row_frame = customtkinter.CTkFrame(parent, fg_color="#FFFFFF", border_width=1, border_color="#E2E8F0", corner_radius=8)
        row_frame.pack(fill="x", pady=4)
        row_frame.grid_columnconfigure(1, weight=1)
        
        status_dot = customtkinter.CTkLabel(row_frame, text="●", font=("Arial", 20), text_color="#22C55E")
        status_dot.grid(row=0, column=0, padx=15, pady=10)
        
        customtkinter.CTkLabel(row_frame, text=item_name, font=("Inter", 14), anchor="w").grid(row=0, column=1, sticky="w")
        customtkinter.CTkLabel(row_frame, text=f"{stock} stok", font=("Inter", 14), text_color="gray50").grid(row=0, column=2, padx=20)
        
        formatted_date = created_at.strftime('%d/%m/%Y %H:%M') if created_at else "N/A"
        customtkinter.CTkLabel(row_frame, text=formatted_date, font=("Inter", 14), text_color="gray50").grid(row=0, column=3, padx=20)
        
        action_frame = customtkinter.CTkFrame(row_frame, fg_color="transparent")
        action_frame.grid(row=0, column=4, padx=15)
        
        status_label = customtkinter.CTkLabel(action_frame, text="Status", font=("Inter", 14, "underline"), text_color="gray50", cursor="hand2")
        status_label.pack(side="left", padx=8)
        status_label.bind("<Button-1>", lambda e, i=item_id: self.open_status_popup(i))

        edit_label = customtkinter.CTkLabel(action_frame, text="Edit", font=("Inter", 14, "underline"), text_color="#3B82F6", cursor="hand2")
        edit_label.pack(side="left", padx=8)
        edit_label.bind("<Button-1>", lambda e, i=item_id: self.edit_item(i))

        delete_label = customtkinter.CTkLabel(action_frame, text="Delete", font=("Inter", 14, "underline"), text_color="#EF4444", cursor="hand2")
        delete_label.pack(side="left")
        delete_label.bind("<Button-1>", lambda e, i=item_id, n=item_name: self.delete_item(i, n))

    def add_item_popup(self):
        """Membuka jendela pop-up untuk menambah barang baru."""
        AddItemWindow(master=self, refresh_callback=self.refresh_all_tables)

    def add_category_popup(self):
        """Membuka jendela pop-up untuk menambah kategori baru."""
        AddCategoryWindow(master=self, refresh_callback=self.refresh_all_tables)

    def edit_item(self, item_id):
        """Membuka jendela pop-up untuk mengedit barang."""
        EditItemWindow(master=self, item_id=item_id, refresh_callback=self.refresh_all_tables)

    def open_status_popup(self, item_id):
        """Membuka jendela pop-up untuk menambah/mengurangi stok."""
        UpdateStockWindow(master=self, item_id=item_id, refresh_callback=self.refresh_all_tables)
    
    def delete_item(self, item_id, item_name):
        if messagebox.askyesno("Konfirmasi Hapus", f"Apakah Anda yakin ingin menghapus '{item_name}'?\n\nTindakan ini tidak bisa dibatalkan."):
            try:
                db.delete_item(item_id)
                messagebox.showinfo("Sukses", f"'{item_name}' berhasil dihapus.")
                self.refresh_all_tables()
            except Exception as e:
                messagebox.showerror("Error", f"Gagal menghapus item: {e}")
