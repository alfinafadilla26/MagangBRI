# File: ui/history_frame.py
# Berisi UI untuk halaman Riwayat Transaksi.

import customtkinter
from tkinter import ttk, messagebox, filedialog
from PIL import Image
import os
import database as db
import logging
from tkcalendar import Calendar
from datetime import datetime
import pandas as pd

class HistoryFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.configure(fg_color="#FDFDFD")
        
        # Konfigurasi grid utama
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.create_widgets()
        self.style_treeview()

    def get_asset_path(self, *paths):
        """Helper untuk mendapatkan path absolut ke folder assets."""
        return os.path.join(db.get_base_path(), "assets", *paths)

    def open_calendar(self, entry_widget):
        """Membuka jendela pop-up kalender untuk memilih tanggal."""
        if hasattr(self, 'cal_win') and self.cal_win.winfo_exists():
            self.cal_win.focus()
            return

        self.cal_win = customtkinter.CTkToplevel(self)
        self.cal_win.title("Pilih Tanggal")
        self.cal_win.geometry("300x250")
        self.cal_win.resizable(False, False)
        self.cal_win.grab_set()

        cal = Calendar(self.cal_win, selectmode='day', date_pattern='yyyy-mm-dd',
                       background="#297AB9", foreground='white', headersbackground="#297AB9")
        cal.pack(pady=10, fill="both", expand=True)

        def set_date():
            selected_date = cal.get_date()
            entry_widget.delete(0, 'end')
            entry_widget.insert(0, selected_date)
            self.cal_win.destroy()

        select_button = customtkinter.CTkButton(self.cal_win, text="Pilih", command=set_date)
        select_button.pack(pady=10)

    def style_treeview(self):
        """Menerapkan style kustom agar Treeview cocok dengan tema CTk."""
        style = ttk.Style(self)
        style.theme_use("default")
        
        style.configure("Treeview.Heading",
                        background="#F9FAFB",
                        foreground="#6B7280",
                        font=("Inter", 14, "bold"),
                        relief="flat", borderwidth=0)
        style.map("Treeview.Heading", background=[('active', '#F3F4F6')])

        style.configure("Treeview",
                        background="white",
                        foreground="#111827",
                        rowheight=40,
                        fieldbackground="white",
                        bordercolor="#E5E7EB",
                        borderwidth=1,
                        font=("Inter", 14))
        style.map("Treeview", background=[('selected', '#EFF6FF')], foreground=[('selected', '#1E40AF')])
        
        style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nsew'})])
        

    def create_widgets(self):
        """Membuat semua widget UI awal untuk halaman ini."""
        top_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        top_frame.grid(row=0, column=0, sticky="ew", padx=30, pady=20)
        top_frame.grid_columnconfigure(0, weight=1)

        customtkinter.CTkLabel(top_frame, text="Riwayat", font=("Inter", 28, "bold"), text_color="gray10").grid(row=0, column=0, sticky="w")

        filter_container = customtkinter.CTkFrame(top_frame, fg_color="transparent")
        filter_container.grid(row=0, column=1, sticky="e")

        self.start_date_entry = customtkinter.CTkEntry(filter_container, placeholder_text="Mulai Dari...", width=140, height=40)
        self.start_date_entry.pack(side="left", padx=(0, 10))
        self.start_date_entry.bind("<Button-1>", lambda e: self.open_calendar(self.start_date_entry))

        self.end_date_entry = customtkinter.CTkEntry(filter_container, placeholder_text="Sampai Dengan...", width=140, height=40)
        self.end_date_entry.pack(side="left", padx=(0, 20))
        self.end_date_entry.bind("<Button-1>", lambda e: self.open_calendar(self.end_date_entry))
        
        apply_button = customtkinter.CTkButton(filter_container, text="Filter", command=self.refresh_history_table, height=40)
        apply_button.pack(side="left", padx=(0, 10))
        
        reset_button = customtkinter.CTkButton(filter_container, text="Reset", command=self.reset_filters, height=40, fg_color="#E5E7EB", text_color="#374151", hover_color="#D1D5DB")
        reset_button.pack(side="left", padx=(0, 10))

        export_button = customtkinter.CTkButton(filter_container, text="Export ke Excel", command=self.export_to_excel, height=40)
        export_button.pack(side="left")

        # --- Area Tabel Riwayat ---
        table_container = customtkinter.CTkFrame(self, fg_color="transparent")
        table_container.grid(row=1, column=0, sticky="nsew", padx=30, pady=(0, 20))
        table_container.grid_columnconfigure(0, weight=1)
        table_container.grid_rowconfigure(0, weight=1)

        columns = ('nama_barang', 'jumlah', 'status', 'waktu', 'nama_pengguna')
        self.history_table = ttk.Treeview(table_container, columns=columns, show='headings', style="Treeview")

        # Definisi Kolom
        self.history_table.heading('nama_barang', text='Nama Barang')
        self.history_table.heading('jumlah', text='Jumlah')
        self.history_table.heading('status', text='Status')
        self.history_table.heading('waktu', text='Waktu')
        self.history_table.heading('nama_pengguna', text='Nama Pengguna')

        # Lebar Kolom
        self.history_table.column('nama_barang', width=350, anchor='w')
        self.history_table.column('jumlah', width=100, anchor='center')
        self.history_table.column('status', width=120, anchor='center')
        self.history_table.column('waktu', width=200, anchor='w')
        self.history_table.column('nama_pengguna', width=200, anchor='w')

        self.history_table.grid(row=0, column=0, sticky="nsew")

        # Scrollbar
        scrollbar = customtkinter.CTkScrollbar(table_container, command=self.history_table.yview)
        scrollbar.grid(row=0, column=1, sticky='ns')
        self.history_table.configure(yscrollcommand=scrollbar.set)

    def reset_filters(self):
        """Membersihkan semua filter dan menampilkan kembali seluruh riwayat."""
        self.start_date_entry.delete(0, 'end')
        self.end_date_entry.delete(0, 'end')
        self.refresh_history_table()

    def refresh_history_table(self):
        """Mengambil data histori, bisa dengan filter tanggal, dan menampilkannya."""
        start_date_str = self.start_date_entry.get()
        end_date_str = self.end_date_entry.get()

        for row in self.history_table.get_children():
            self.history_table.delete(row)
        
        try:
            if start_date_str and end_date_str:
                history_logs = db.get_history_by_date_range(start_date_str, end_date_str)
            else:
                history_logs = db.get_history()
            
            if not history_logs:
                self.history_table.insert("", "end", values=("Tidak ada riwayat untuk ditampilkan.", "", "", "", ""))
                return
            
            for log in history_logs:
                # Unpacking data yang aman
                date_taken = log[0] if len(log) > 0 else None
                item_name = log[1] if len(log) > 1 else "N/A"
                quantity = log[2] if len(log) > 2 else 0
                taker_name = log[3] if len(log) > 3 else "N/A"
                status = log[4] if len(log) > 4 else "N/A"
                
                # Format data untuk ditampilkan
                display_name = item_name or "BARANG TELAH DIHAPUS"
                display_time = date_taken.strftime('%d/%m/%Y %H:%M') if date_taken else "N/A"
                display_status = status.capitalize() if status else "N/A"
                
                values_tuple = (display_name, quantity, display_status, display_time, taker_name)
                self.history_table.insert("", "end", values=values_tuple, tags=(display_status,))
        
        except ValueError:
            messagebox.showerror("Format Tanggal Salah", "Gunakan format YYYY-MM-DD.", parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"Terjadi kesalahan saat memuat riwayat: {e}", parent=self)

    def export_to_excel(self):
        """Mengambil data sesuai filter dan mengekspornya ke file Excel."""
        start_date = self.start_date_entry.get()
        end_date = self.end_date_entry.get()

        if not (start_date and end_date):
            messagebox.showerror("Error", "Harap pilih 'Mulai Dari' dan 'Sampai Dengan' untuk mengekspor.")
            return
            
        try:
            data_to_export = db.get_history_by_date_range(start_date, end_date)

            if not data_to_export:
                messagebox.showinfo("Kosong", "Tidak ada data riwayat ditemukan pada rentang tanggal tersebut.")
                return
                
            filename = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel Workbook", "*.xlsx"), ("All Files", ".*")],
                title="Simpan Laporan Histori",
                initialfile=f"Laporan Histori {start_date} sampai {end_date}.xlsx"
            )

            if not filename: return

            # Unpacking data yang aman untuk ekspor
            formatted_data = []
            for log in data_to_export:
                date_taken = log[0] if len(log) > 0 else None
                item_name = log[1] if len(log) > 1 else "N/A"
                quantity = log[2] if len(log) > 2 else 0
                taker_name = log[3] if len(log) > 3 else "N/A"
                status = log[4] if len(log) > 4 else "N/A"
                
                formatted_data.append([
                    date_taken.strftime('%Y-%m-%d %H:%M:%S') if date_taken else "N/A",
                    item_name or "BARANG TELAH DIHAPUS",
                    quantity,
                    taker_name,
                    status.capitalize() if status else "N/A"
                ])
            
            df = pd.DataFrame(formatted_data, columns=["Waktu", "Nama Barang", "Jumlah", "Nama Pengguna", "Status"])
            
            df.to_excel(filename, index=False)
            
            messagebox.showinfo("Berhasil", f"Data berhasil diekspor ke:\n{filename}")
        
        except Exception as e:
            messagebox.showerror("Ekspor Gagal", f"Terjadi error saat mengekspor file:\n{e}")

