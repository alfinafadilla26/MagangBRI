# File: ui/notification_popup.py
# Berisi UI untuk pop-up notifikasi stok rendah.

import customtkinter
from datetime import datetime

class NotificationPopup(customtkinter.CTkToplevel):
    def __init__(self, master, low_stock_items, **kwargs):
        super().__init__(master, **kwargs)

        self.low_stock_items = low_stock_items

        # --- Konfigurasi Window ---
        self.title("Notifikasi")
        self.geometry("450x400")
        self.resizable(False, False)
        self.configure(fg_color="#FDFDFD")
        self.grab_set() # Membuat window ini modal

        # --- Layout Utama ---
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        customtkinter.CTkLabel(self, text="Notification", font=("Inter", 24, "bold"), text_color="gray10").grid(row=0, column=0, padx=20, pady=20, sticky="w")

        # Frame untuk daftar notifikasi
        scrollable_frame = customtkinter.CTkScrollableFrame(self, fg_color="transparent", border_width=0)
        scrollable_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        scrollable_frame.grid_columnconfigure(0, weight=1)

        if not self.low_stock_items:
            customtkinter.CTkLabel(scrollable_frame, text="Tidak ada notifikasi.").pack(pady=20)
        else:
            for item in self.low_stock_items:
                self.create_notification_row(scrollable_frame, item)

    def create_notification_row(self, parent, item_data):
        """Membuat satu baris notifikasi."""
        item_name = item_data.get('item_name', 'N/A')
        stock = item_data.get('stock', 0)
        
        row_frame = customtkinter.CTkFrame(parent, fg_color="#FFFFFF", border_width=1, border_color="#E2E8F0", corner_radius=8)
        row_frame.pack(fill="x", pady=5, padx=5)
        row_frame.grid_columnconfigure(1, weight=1)

        # Ikon titik merah
        status_dot = customtkinter.CTkLabel(row_frame, text="●", font=("Arial", 20), text_color="#FF0940") # Merah
        status_dot.grid(row=0, column=0, padx=15, pady=15)

        # Frame untuk teks notifikasi
        text_frame = customtkinter.CTkFrame(row_frame, fg_color="transparent")
        text_frame.grid(row=0, column=1, sticky="w", pady=15)

        message = f"Stok untuk '{item_name}' sudah dibawah 5!"
        customtkinter.CTkLabel(text_frame, text=message, font=("Inter", 14, "bold"), anchor="w").pack(fill="x")
        
        # Tanggal (contoh tanggal saat ini)
        date_str = datetime.now().strftime('%d/%m/%Y %H:%M')
        customtkinter.CTkLabel(text_frame, text=date_str, font=("Inter", 12), text_color="gray50", anchor="w").pack(fill="x")

        # Label stok di kanan
        stock_label = customtkinter.CTkLabel(row_frame, text=f"{stock} Stok", font=("Inter", 14), text_color="gray50")
        stock_label.grid(row=0, column=2, padx=20)
