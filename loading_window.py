import tkinter as tk
from tkinter import ttk
import threading
import time

class LoadingWindow:
    def __init__(self, root, message="Preloading Files...", width=300, height=100):
        self.root = root
        self.message = message
        self.width = width
        self.height = height
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)  # Handle window close event
        self.create_widgets()
        self.center_window()
        self.is_running = True

    def create_widgets(self):
        self.root.title("Loading")
        self.root.geometry(f"{self.width}x{self.height}")
        self.label = ttk.Label(self.root, text=self.message, anchor="center", font=("Arial", 14))
        self.label.pack(expand=True, padx=20, pady=20)

    def center_window(self):
        self.root.update_idletasks()  # Ensure all widgets are rendered before centering
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (self.width // 2)
        y = (screen_height // 2) - (self.height // 2)
        self.root.geometry(f"{self.width}x{self.height}+{x}+{y}")

    def on_close(self):
        self.is_running = False  # Set a flag to indicate the window is closing
        self.root.quit()  # Stop the main loop

    def close(self):
        if self.is_running:
            self.is_running = False
            self.root.quit()  # Stop the main loop
            self.root.destroy()  # Close the window

def preload_files(base_dir):
    preload_root = tk.Tk()  # Initialize the root for the loading window
    loading_window = LoadingWindow(preload_root)  # Create the loading window

    def run_preload():
        time.sleep(5)  # Simulating a delay for the task
        preload_root.after(0, loading_window.close)  # Close the loading window in the main thread

    # Start the preload process in a separate thread
    preload_thread = threading.Thread(target=run_preload)
    preload_thread.start()

    preload_root.mainloop()  # Start the main loop to display the window

    preload_thread.join()  # Wait for the thread to finish before moving on

    # Return the result if needed (this is a placeholder)
    return "Simulated File Search Result"

# Example usage
file_searcher = preload_files("/path/to/directory")
print(file_searcher)  # Output the result
