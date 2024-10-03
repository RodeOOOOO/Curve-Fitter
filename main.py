import tkinter as tk
import threading
import pandas as pd
from file_searcher import FileSearcher
from data_processor import DataProcessor
from filter_window import FilterWindow
from loading_window import LoadingWindow
from progress_window import ProgressWindow
from plotting import Plotting  # Ensure this import is correct
import os
import glob

def preload_files(base_dir):
    # Start the Tkinter root only when needed
    preload_root = tk.Tk()
    loading_window = LoadingWindow(preload_root)
    
    file_searcher = None  # Initialize as None

    def run_preload():
        nonlocal file_searcher
        print("Starting file preloading...")
        file_searcher = FileSearcher(base_dir=base_dir)
        preload_root.after(0, loading_window.close)

    # Start the preload process in a separate thread
    preload_thread = threading.Thread(target=run_preload)
    preload_thread.start()

    # Main loop to keep the window open until the thread finishes
    preload_root.mainloop()

    preload_thread.join()  # Wait for the thread to finish before moving on

    return file_searcher

def process_file(file_path, concentration, data_processor):
    filtered_data = data_processor.extract_filtered_data(file_path)
    if not filtered_data.empty:
        return concentration, filtered_data
    return concentration, pd.DataFrame()

def process_files(data_processor, file_searcher, final_df, base_dir, uwa_data_by_concentration, progress_window, filter_dir_name):
    plotter = Plotting(base_dir, filter_dir_name)  # Initialize the Plotting class with filter_dir_name
    total_files = final_df.shape[0]
    completed = 0
    
    print(f"Total files to process: {total_files}")
    
    for idx, row in final_df.iterrows():
        pattern = row["Cleaned Log Filename"]
        print(f"Searching for files matching pattern: {pattern}")
        
        matched_files = file_searcher.search_files(pattern)
        print(f"Found {len(matched_files)} files matching pattern: {pattern}")
        
        concentration = row["Analyte Concentration"]
        for file_path in matched_files:
            print(f"Processing file: {file_path}")
            concentration, filtered_data = process_file(file_path, concentration, data_processor)
            if not filtered_data.empty:
                if concentration not in uwa_data_by_concentration:
                    uwa_data_by_concentration[concentration] = []
                uwa_data_by_concentration[concentration].append(filtered_data)
            completed += 1
            progress_window.update_progress(completed)
    
    print("All files processed. Computing and plotting results...")
    plotter.compute_and_plot_individual(uwa_data_by_concentration)  # Use the instance to call the method
    progress_window.processing_complete()

def start_processing_in_thread(data_processor, file_searcher, final_df, base_dir, uwa_data_by_concentration, progress_window, filter_dir_name):
    processing_thread = threading.Thread(
        target=process_files,
        args=(data_processor, file_searcher, final_df, base_dir, uwa_data_by_concentration, progress_window, filter_dir_name)
    )
    processing_thread.start()

def resolve_paths():
    # Checking user-specific paths first
    if os.path.exists(r"C:\Users\RodePeters\Box\SALVUS\Test Data"):
        file_path = r"C:\Users\RodePeters\CJB Salvus\Product Development - Internal Library\Assay Development - Internal\Testing Database (Version 1-19-24).xlsx"
        base_dir = r"C:\Users\RodePeters\Box\SALVUS\Test Data"
    elif os.path.exists(r"C:\Users\ScottWitte\Box\SALVUS\Test Data"):
        file_path = r"C:\Users\ScottWitte\CJB Salvus\Product Development - Internal Library\Assay Development - Internal\Testing Database (Version 1-19-24).xlsx"
        base_dir = r"C:\Users\ScottWitte\Box\SALVUS\Test Data"
    elif os.path.exists(r"C:\Users\mmurphy\Box\SALVUS\Test Data"):
        file_path = r"C:\Users\mmurphy\CJB Salvus\Product Development - Internal Library\Assay Development – Internal\Testing Database (Version 1-19-24).xlsx"
        base_dir = r"C:\Users\mmurphy\Box\SALVUS\Test Data"
    elif os.path.exists(r"C:\Users\jpardieck\Box\SALVUS\Test Data"):
        file_path = r"C:\Users\jpardieck\CJB Salvus\Product Development - Internal Library\Assay Development – Internal\Testing Database (Version 1-19-24).xlsx"
        base_dir = r"C:\Users\jpardieck\Box\SALVUS\Test Data"
    else:
        print("Resolving file paths...")
        file_pattern = r"**\CJB Salvus\Product Development - Internal Library\Assay Development - Internal\Testing Database (Version 1-19-24).xlsx"
        base_dir_pattern = r"**\Box\SALVUS\Test Data"
        file_paths = glob.glob(file_pattern, recursive=True)
        base_dirs = glob.glob(base_dir_pattern, recursive=True)
        file_path = file_paths[0] if file_paths else None
        base_dir = base_dirs[0] if base_dirs else None
    
    if not file_path or not base_dir:
        raise FileNotFoundError("Could not resolve file path or base directory.")
    
    print(f"File path resolved: {file_path}")
    print(f"Base directory resolved: {base_dir}")
    
    return file_path, base_dir

def main():
    print("Main process started...")
    file_path, base_dir = resolve_paths()

    print("Loading Excel file...")
    df = pd.read_excel(file_path, sheet_name="Testing Database")

    filter_params = {
        "receptor": "succyl-betacylcodextrin",
        "testing_code": "TC58",
        "coating_code": 122,
        "target_analyte": "PFOA",
        "run_result_classification": ["Low Response", "High Response", "Good", None]
    }

    def update_filters():
        print("Updating filters...")

        # Create a directory name based on the selected filter parameters
        filter_dir_name = f"{filter_params['receptor']}_{filter_params['testing_code']}_{filter_params['coating_code']}_{filter_params['target_analyte']}"
        filter_dir_name = filter_dir_name.replace(" ", "_")  # Ensure the directory name is clean
        
        # Prepend the Visuals folder to the filter-specific directory name
        filter_dir_name = os.path.join(base_dir, "Visuals", filter_dir_name)


        # Load and filter data using the parameters
        final_df = data_processor.load_and_filter_data(filter_params)

        if final_df.empty:
            print("No data found with the given filters.")
            return

        uwa_data_by_concentration = {}

        print("Initializing progress window...")
        progress_root = tk.Tk()
        progress_window = ProgressWindow(progress_root, total_files=final_df.shape[0])
        progress_root.update_idletasks()

        print("Starting processing in a new thread...")
        start_processing_in_thread(data_processor, file_searcher, final_df, base_dir, uwa_data_by_concentration, progress_window, filter_dir_name)
        progress_root.mainloop()

    print("Preloading files...")
    file_searcher = preload_files(base_dir)
    data_processor = DataProcessor(testing_file=file_path)

    print("Starting main Tkinter loop...")
    root = tk.Tk()
    root.title("Filter Configuration")
    
    # Start the filter window and pass the update_filters callback
    app = FilterWindow(root, df, filter_params, update_filters)
    root.mainloop()
    print("Main process completed.")

if __name__ == "__main__":
    main()