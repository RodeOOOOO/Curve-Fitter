import tkinter as tk
from tkinter import ttk

class ProgressWindow:
    def __init__(self, root, total_files):
        self.root = root
        self.root.title("Processing Files")
        
        self.label = ttk.Label(self.root, text="Processing files, please wait...")
        self.label.pack(padx=20, pady=10)

        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(padx=20, pady=10)
        
        self.progress["maximum"] = total_files
        self.progress["value"] = 0
        
        self.count_label = ttk.Label(self.root, text=f"0/{total_files} files processed")
        self.count_label.pack(padx=20, pady=10)

        self.close_button = ttk.Button(self.root, text="Close Program", command=self.root.quit)
        self.close_button.pack(padx=20, pady=10)
        self.close_button.pack_forget()  # Initially hide the button

        self.center_window()

    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def update_progress(self, value):
        self.progress["value"] = value
        self.count_label.config(text=f"{value}/{self.progress['maximum']} files processed")
        self.root.update_idletasks()

    def processing_complete(self):
        self.label.config(text="Processing complete!")
        self.count_label.config(text="All files have been processed.")
        self.close_button.pack()  # Show the close button

    def close(self):
        self.root.destroy()
