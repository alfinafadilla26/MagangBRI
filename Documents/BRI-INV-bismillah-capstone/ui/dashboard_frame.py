# File: ui/dashboard_frame.py
# Berisi UI untuk halaman utama/dashboard yang dilihat oleh User Guest. (Versi Desain Final)

import customtkinter
from PIL import Image
import os
import database as db # Diperlukan untuk get_base_path
import logging

class DashboardFrame(customtkinter.CTkFrame):
    def __init__(self, master, explore_callback, **kwargs):
        super().__init__(master, **kwargs)
        
        self.explore_callback = explore_callback # Fungsi untuk pindah ke halaman item
        self.configure(fg_color="#F8F9FA") # Warna latar yang lebih lembut dan modern

        # Konfigurasi grid agar konten bisa di-scroll
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Buat frame utama yang bisa di-scroll
        self.scrollable_frame = customtkinter.CTkScrollableFrame(self, fg_color="transparent", border_width=0)
        self.scrollable_frame.grid(row=0, column=0, sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        
        # --- 1. Hero Banner ---
        self.create_hero_banner()

        # --- 2. Penjelasan Cara Kerja ---
        self.create_how_it_works_section()

    def get_asset_path(self, *paths):
        """Helper untuk mendapatkan path absolut ke folder assets."""
        return os.path.join(db.get_base_path(), "assets", *paths)

    def create_hero_banner(self):
        """Membuat bagian banner promosi di bagian atas dengan desain baru."""
        banner_container = customtkinter.CTkFrame(self.scrollable_frame, fg_color="transparent")
        banner_container.grid(row=0, column=0, sticky="ew", padx=30, pady=20)
        banner_container.grid_columnconfigure(0, weight=1)

        banner_frame = customtkinter.CTkFrame(banner_container, fg_color="#297AB9", corner_radius=20, border_width=1, border_color="#297AB9")
        banner_frame.pack(fill="both", expand=True)
        
        banner_frame.grid_columnconfigure(0, weight=3)
        banner_frame.grid_columnconfigure(1, weight=2)

        text_container = customtkinter.CTkFrame(banner_frame, fg_color="transparent")
        text_container.grid(row=0, column=0, padx=50, pady=50, sticky="nsew")
        
        customtkinter.CTkLabel(text_container, text="Transparasi Stok,\nTerpusat, Terkendali", font=customtkinter.CTkFont(family="Inter", size=38, weight="bold"), text_color="white", justify="left").pack(anchor="w", pady=(0,5))
        customtkinter.CTkLabel(text_container, text="Dengan Gudang Digital, Barang Tidak Akan Kehabisan!", font=customtkinter.CTkFont(family="Inter", size=16), text_color="#E0E7FF", justify="left").pack(anchor="w", pady=(0, 30))
        
        explore_button = customtkinter.CTkButton(text_container, text="Eksplor Sekarang!", font=customtkinter.CTkFont(family="Inter", size=16, weight="bold"), 
                                                 fg_color="#FFFFFF", text_color="#297AB9", hover_color="#F5F3FF", 
                                                 height=50, width=220, corner_radius=12, command=self.explore_callback,
                                                 border_width=2, border_color="#FFFFFF")
        explore_button.pack(anchor="w")

        image_container = customtkinter.CTkFrame(banner_frame, fg_color="transparent")
        image_container.grid(row=0, column=1, sticky="nsew", padx=(0, 30), pady=30)
        try:
            phone_image = customtkinter.CTkImage(Image.open(self.get_asset_path("phone_dashboard.png")), size=(260, 260))
            customtkinter.CTkLabel(image_container, image=phone_image, text="").pack(anchor="center", expand=True)
        except Exception as e:
            logging.warning(f"Gambar banner 'phone_dashboard' tidak ditemukan: {e}")
            # --- PERBAIKAN DI SINI ---
            # Menambahkan master (image_container) pada CTkLabel fallback
            customtkinter.CTkLabel(image_container, text="phone_dashboard", text_color="white").pack(anchor="center", expand=True)

    def create_how_it_works_section(self):
        """Membuat bagian 'Bagaimana BRI INV Bekerja?' dengan desain baru."""
        works_container = customtkinter.CTkFrame(self.scrollable_frame, fg_color="transparent")
        works_container.grid(row=1, column=0, sticky="ew", padx=30, pady=(40, 60))
        works_container.grid_columnconfigure(0, weight=1)

        customtkinter.CTkLabel(works_container, text="Bagaimana BRI INV Bekerja?", font=customtkinter.CTkFont(family="Inter", size=30, weight="bold"), text_color="#1F2937").pack(pady=(0, 40))

        # Canvas untuk menampung gambar garis dan kartu langkah
        steps_canvas_container = customtkinter.CTkFrame(works_container, fg_color="transparent", height=300)
        steps_canvas_container.pack(fill="x", expand=True, padx=20)
        
        # Gambar garis sebagai latar belakang
        try:
            line_img = customtkinter.CTkImage(Image.open(self.get_asset_path("icons", "garis_dashboard.png")), size=(750, 80))
            line_label = customtkinter.CTkLabel(steps_canvas_container, image=line_img, text="")
            line_label.place(relx=0.5, rely=0.4, anchor="center") # Posisikan garis
        except Exception as e:
            logging.warning(f"Gambar 'garis_dashboard.png' tidak ditemukan: {e}")

        # Frame untuk menempatkan kartu di atas gambar garis
        steps_frame = customtkinter.CTkFrame(steps_canvas_container, fg_color="transparent")
        steps_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        steps_frame.grid_columnconfigure((0, 1, 2), weight=1)
        steps_frame.grid_rowconfigure(0, weight=1)

        # Data untuk setiap kartu langkah (sesuai desain gambar)
        steps_data = [
            {"icon": "Icon.png", "title": "Cari barang", "desc": "Cari barang yang ingin kalian ambil sesuai dengan kebutuhan", "color": "#EBF5FF", "highlight": True},
            {"icon": "logo_tengah.png", "title": "Masukkan jumlah dan nama", "desc": "Masukkan jumlah dari barang yang akan diambil dan nama pengambil", "color": "#FFF7E6", "highlight": True},
            {"icon": "Icon_kanan.png", "title": "Kirim", "desc": "Mengirim data untuk mengupdate stok di database Gudang Digital", "color": "#EBF5FF", "highlight": True}
        ]

        for i, data in enumerate(steps_data):
            self.create_step_card(steps_frame, i, data["icon"], data["title"], data["desc"], data["color"], data["highlight"])

    def create_step_card(self, parent, column, icon_name, title, description, color, is_highlighted):
        """Membuat satu kartu untuk langkah-langkah cara kerja dengan desain baru."""
        
        card_fg = "#FFFFFF" if is_highlighted else "transparent"
        card_border_width = 1 if is_highlighted else 0
        
        card_container = customtkinter.CTkFrame(parent, fg_color='transparent')
        card_container.grid(row=0, column=column, sticky='s' if is_highlighted else 'n', padx=10, pady=(20 if is_highlighted else 60))

        card = customtkinter.CTkFrame(card_container, fg_color=card_fg, corner_radius=15, border_width=card_border_width, border_color="#E5E7EB")
        card.pack()
        
        icon_frame = customtkinter.CTkFrame(card, fg_color=color, corner_radius=30, width=64, height=64)
        icon_frame.pack(padx=20, pady=(20, 15))
        icon_frame.grid_propagate(False)
        icon_frame.grid_columnconfigure(0, weight=1)
        icon_frame.grid_rowconfigure(0, weight=1)

        try:
            icon_img = customtkinter.CTkImage(Image.open(self.get_asset_path("icons", icon_name)), size=(32, 32))
            customtkinter.CTkLabel(icon_frame, image=icon_img, text="").grid(row=0, column=0)
        except Exception as e:
            logging.warning(f"Ikon langkah '{icon_name}' tidak ditemukan: {e}")
            customtkinter.CTkLabel(icon_frame, text="?", font=("Inter", 24)).grid(row=0, column=0)
        
        text_frame = customtkinter.CTkFrame(card, fg_color="transparent")
        text_frame.pack(padx=20, pady=(0, 20), fill="x")

        customtkinter.CTkLabel(text_frame, text=title, font=customtkinter.CTkFont(family="Inter", size=18, weight="bold"), text_color="#111827").pack(pady=(0, 8))
        customtkinter.CTkLabel(text_frame, text=description, wraplength=220, justify="center", text_color="#6B5D5D", font=("Inter", 14)).pack()
