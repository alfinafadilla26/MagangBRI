# File: ui/item_frame.py (Desain Baru & Minimalis Sesuai Gambar)

import customtkinter
from PIL import Image
import database as db
import logging
import os
from tkinter import messagebox

class ItemFrame(customtkinter.CTkFrame):
    def __init__(self, master, app, **kwargs):
        super().__init__(master, **kwargs)

        self.app = app # Simpan referensi ke jendela App utama
        self.configure(fg_color="#FFFFFF")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1) 

        # State management
        self.current_category_id = None
        self.current_category_name = "Semua Barang"
        self.category_buttons = []

        self.create_widgets()
        self.refresh_data()

    def get_asset_path(self, *paths):
        """Mendapatkan path absolut ke file di dalam folder assets."""
        return os.path.join(db.get_base_path(), "assets", *paths)

    def refresh_data(self):
        """Metode publik untuk me-refresh seluruh data di halaman ini."""
        self.after(50, self.initialize_data)

    def initialize_data(self):
        """Memuat data kategori dan item."""
        self.setup_category_filters()
        self.filter_items(category_id=None, category_name="Semua Barang")

    def create_widgets(self):
        """Membuat semua widget UI awal untuk halaman ini."""
        top_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        top_frame.grid(row=0, column=0, sticky="ew", padx=25, pady=(20, 10))
        top_frame.grid_columnconfigure(0, weight=1)

        self.search_entry = customtkinter.CTkEntry(top_frame, 
                                                   placeholder_text="Pencarian...", 
                                                   height=45, font=("Inter", 14), 
                                                   border_color="#E0E0E0", 
                                                   corner_radius=8,
                                                   fg_color="#FFFFFF")
        self.search_entry.grid(row=0, column=0, sticky="ew")
        self.search_entry.bind("<KeyRelease>", lambda e: self.on_search_change())
        
        customtkinter.CTkLabel(self, text="Category", font=customtkinter.CTkFont(size=24, weight="bold"), text_color="gray10").grid(row=1, column=0, sticky="w", padx=25)
        
        self.filter_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.filter_frame.grid(row=2, column=0, sticky="ew", padx=15, pady=(0, 15))
        
        self.item_list_title = customtkinter.CTkLabel(self, text="Semua Barang", font=customtkinter.CTkFont(size=24, weight="bold"), text_color="gray10")
        self.item_list_title.grid(row=3, column=0, pady=(0, 10), sticky="w", padx=25)

        self.scrollable_item_frame = customtkinter.CTkScrollableFrame(self, fg_color="transparent", border_width=0)
        self.scrollable_item_frame.grid(row=4, column=0, sticky="nsew", padx=15, pady=0)
        self.scrollable_item_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

    def create_category_button(self, parent, text, command):
        """Membuat satu tombol filter kategori (Desain Teks)."""
        button = customtkinter.CTkButton(parent, text=text, font=("Inter", 14, "bold"), command=command,
                                         height=40, corner_radius=8, fg_color="#F1F5F9",
                                         text_color="#64748B", hover_color="#E2E8F0")
        button.pack(side="left", padx=10, pady=5)
        return button

    def select_category_button(self, selected_button):
        """Mengubah visual tombol kategori yang aktif."""
        for btn in self.category_buttons:
            is_selected = (btn == selected_button)
            btn.configure(fg_color="#4A55A2" if is_selected else "#F1F5F9",
                          text_color="#FFFFFF" if is_selected else "#64748B")

    def setup_category_filters(self):
        for widget in self.filter_frame.winfo_children():
            widget.destroy()
        self.category_buttons.clear()

        all_cmd = lambda: self.filter_items(None, "Semua Barang")
        all_button = self.create_category_button(self.filter_frame, "Semua", all_cmd)
        self.category_buttons.append(all_button)

        categories = db.get_all_categories()
        if categories:
            for cat_id, cat_name in categories:
                cmd = lambda c_id=cat_id, c_name=cat_name: self.filter_items(c_id, c_name)
                button = self.create_category_button(self.filter_frame, cat_name, cmd)
                self.category_buttons.append(button)

        if self.category_buttons:
            self.select_category_button(self.category_buttons[0])

    def filter_items(self, category_id, category_name):
        self.current_category_id = category_id
        self.current_category_name = category_name
        
        for btn in self.category_buttons:
            if btn.cget("text") == category_name:
                self.select_category_button(btn)
                break
        else:
            if self.category_buttons:
                self.select_category_button(self.category_buttons[0])

        self.item_list_title.configure(text=self.current_category_name)
        self.on_search_change()

    def on_search_change(self):
        self.display_items(self.current_category_id, self.search_entry.get())

    def display_items(self, category_id=None, search_term=""):
        """Menampilkan item dan mencegah duplikasi nama."""
        for widget in self.scrollable_item_frame.winfo_children():
            widget.destroy()
        
        items = db.search_items(category_id=category_id, keyword=search_term)

        # --- PERBAIKAN: Mencegah item duplikat (berdasarkan nama) untuk ditampilkan ---
        displayed_item_names = set()
        unique_items = []
        for item in items:
            # Kolom nama item ada di indeks 1
            item_name = item[1] 
            if item_name.lower() not in displayed_item_names:
                unique_items.append(item)
                displayed_item_names.add(item_name.lower())
        # --- Akhir Perbaikan ---

        if not unique_items:
            no_item_label = customtkinter.CTkLabel(self.scrollable_item_frame, text="Tidak ada item untuk ditampilkan.", font=("Inter", 16), text_color="gray50")
            no_item_label.grid(row=0, column=0, columnspan=4, pady=50)
            return

        for i, item_data in enumerate(unique_items):
            self.create_item_card(self.scrollable_item_frame, item_data, i // 4, i % 4)

    def create_item_card(self, parent, item_data, row, column):
        """Membuat satu kartu UI untuk item barang dengan tinggi yang seragam."""
        # Kolom dari search_items: item_id, item_name, category_id, stock, description, date_added, image_url
        item_id, item_name, _, stock, _, created_at, _ = item_data
        
        card = customtkinter.CTkFrame(parent, fg_color="white", border_width=1, border_color="#E8E8E8", corner_radius=12, height=150)
        card.grid_propagate(False)
        card.grid(row=row, column=column, padx=10, pady=10, sticky="ew")
        
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(0, weight=1)
        card.grid_rowconfigure(1, weight=0)

        text_frame = customtkinter.CTkFrame(card, fg_color="transparent")
        text_frame.grid(row=0, column=0, sticky="nsew", padx=15, pady=(15, 10))
        text_frame.grid_columnconfigure(0, weight=1)

        name_label = customtkinter.CTkLabel(text_frame, text=item_name, font=("Inter", 16, "bold"), anchor="w", justify="left", wraplength=180)
        name_label.grid(row=0, column=0, sticky="ew")
        
        category_name = db.get_category_name_by_item_id(item_id)
        category_label = customtkinter.CTkLabel(text_frame, text=category_name or "Tanpa Kategori", font=("Inter", 12), text_color="gray50", anchor="w", justify="left")
        category_label.grid(row=1, column=0, sticky="ew")

        bottom_frame = customtkinter.CTkFrame(card, fg_color="transparent")
        bottom_frame.grid(row=1, column=0, sticky="ew", padx=15, pady=15)
        bottom_frame.grid_columnconfigure(0, weight=1)
        bottom_frame.grid_columnconfigure(2, weight=1)

        stock_button = customtkinter.CTkButton(bottom_frame, text=f"{stock} Stok", font=("Inter", 12, "bold"),
                                                height=32, corner_radius=16,
                                                fg_color="#EBF5FF", text_color="#1D4ED8", hover=False)
        stock_button.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        take_button = customtkinter.CTkButton(bottom_frame, text="Ambil", height=32,
                                              corner_radius=16, font=("Inter", 12, "bold"),
                                              command=lambda id=item_id: self.app.open_take_item_window_by_id(id))
        take_button.grid(row=0, column=2, sticky="ew", padx=(5, 0))

    def refresh_item_table(self):
        """Alias untuk refresh_data agar kompatibel dengan pemanggilan dari frame lain."""
        self.refresh_data()
