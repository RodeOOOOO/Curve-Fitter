import tkinter as tk
from tkinter import ttk, MULTIPLE

class FilterWindow:
    def __init__(self, root, df, filter_params, update_callback):
        self.root = root
        self.df = df
        self.filter_params = filter_params
        self.update_callback = update_callback

        self.create_widgets()
        self.center_window()

    def create_widgets(self):
        # Receptor
        receptor_label = ttk.Label(self.root, text="Receptor")
        receptor_label.grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.receptor_var = tk.StringVar(value=self.filter_params["receptor"])
        receptor_values = sorted(self.df["Receptor"].dropna().unique().tolist())
        self.receptor_menu = ttk.Combobox(self.root, textvariable=self.receptor_var, values=receptor_values)
        self.receptor_menu.grid(row=0, column=1, padx=10, pady=5)

        # Testing Code
        testing_code_label = ttk.Label(self.root, text="Testing Code")
        testing_code_label.grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.testing_code_var = tk.StringVar(value=self.filter_params["testing_code"])
        testing_code_values = sorted(self.df["Testing Code"].dropna().unique().tolist())
        self.testing_code_menu = ttk.Combobox(self.root, textvariable=self.testing_code_var, values=testing_code_values)
        self.testing_code_menu.grid(row=1, column=1, padx=10, pady=5)

        # Coating Code
        coating_code_label = ttk.Label(self.root, text="Coating Code")
        coating_code_label.grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.coating_code_var = tk.StringVar(value=self.filter_params["coating_code"])  # Change from IntVar to StringVar
        coating_code_values = sorted(self.df["Coating Code"].dropna().astype(str).unique().tolist())
        self.coating_code_menu = ttk.Combobox(self.root, textvariable=self.coating_code_var, values=coating_code_values)
        self.coating_code_menu.grid(row=2, column=1, padx=10, pady=5)

        # Target Analyte
        target_analyte_label = ttk.Label(self.root, text="Target Analyte")
        target_analyte_label.grid(row=3, column=0, padx=10, pady=5, sticky="e")
        self.target_analyte_var = tk.StringVar(value=self.filter_params["target_analyte"])
        target_analyte_values = sorted(self.df["Target Analyte"].dropna().unique().tolist())
        self.target_analyte_menu = ttk.Combobox(self.root, textvariable=self.target_analyte_var, values=target_analyte_values)
        self.target_analyte_menu.grid(row=3, column=1, padx=10, pady=5)

        # Run Result Classification
        run_result_classification_label = ttk.Label(self.root, text="Run Result Classification")
        run_result_classification_label.grid(row=4, column=0, padx=10, pady=5, sticky="e")

        # Dynamically populate the listbox with unique values from the Excel sheet
        run_result_classification_values = sorted(self.df["Run Result Classification"].dropna().unique().tolist())
        self.run_result_classification_listbox = tk.Listbox(self.root, selectmode=MULTIPLE)
        for item in run_result_classification_values:
            self.run_result_classification_listbox.insert(tk.END, item)
        self.run_result_classification_listbox.grid(row=4, column=1, padx=10, pady=5)

        # Set default selections
        for idx, val in enumerate(run_result_classification_values):
            if val in self.filter_params["run_result_classification"]:
                self.run_result_classification_listbox.select_set(idx)

        # Update Button
        update_button = ttk.Button(self.root, text="Update Filters", command=self.update_filters)
        update_button.grid(row=5, column=0, columnspan=2, pady=10)

    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def update_filters(self):
        self.filter_params["receptor"] = self.receptor_var.get()
        self.filter_params["testing_code"] = self.testing_code_var.get()
        
        # Handle the coating code as a string to support both integers and strings
        coating_code_value = self.coating_code_var.get()
        try:
            # Try converting to an integer if possible
            self.filter_params["coating_code"] = int(coating_code_value)
        except ValueError:
            # If conversion fails, just store the string value
            self.filter_params["coating_code"] = coating_code_value

        self.filter_params["target_analyte"] = self.target_analyte_var.get()
        selected_run_result_classifications = [
            self.run_result_classification_listbox.get(i) for i in self.run_result_classification_listbox.curselection()
        ]
        self.filter_params["run_result_classification"] = selected_run_result_classifications
        self.root.destroy()  # Close the filter UI after updating
        self.update_callback()
