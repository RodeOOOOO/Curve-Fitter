import pandas as pd
import time

class DataProcessor:
    def __init__(self, testing_file):
        self.testing_file = testing_file

    def load_and_filter_data(self, filter_params):
        print("Loading and filtering data...")
        start_time = time.time()

        # Load the Testing Database sheet
        df = pd.read_excel(self.testing_file, sheet_name="Testing Database")
        print(f"Initial DataFrame row count: {len(df)}")

        # Apply filters one by one and print the row count
        receptor_filtered_df = df[df["Receptor"].str.strip().str.lower() == filter_params["receptor"].lower()]
        print(f"After applying receptor filter (Receptor: {filter_params['receptor']}), row count: {len(receptor_filtered_df)}")

        testing_code_filtered_df = receptor_filtered_df[receptor_filtered_df["Testing Code"] == filter_params["testing_code"]]
        print(f"After applying testing code filter (Testing Code: {filter_params['testing_code']}), row count: {len(testing_code_filtered_df)}")

        coating_code_filtered_df = testing_code_filtered_df[testing_code_filtered_df["Coating Code"] == filter_params["coating_code"]]
        print(f"After applying coating code filter (Coating Code: {filter_params['coating_code']}), row count: {len(coating_code_filtered_df)}")

        target_analyte_filtered_df = coating_code_filtered_df[coating_code_filtered_df["Target Analyte"] == filter_params["target_analyte"]]
        print(f"After applying target analyte filter (Target Analyte: {filter_params['target_analyte']}), row count: {len(target_analyte_filtered_df)}")

        run_result_classification_filtered_df = target_analyte_filtered_df[
            target_analyte_filtered_df["Run Result Classification"].isin(filter_params["run_result_classification"]) |
            target_analyte_filtered_df["Run Result Classification"].isnull()
        ]
        print(f"After applying run result classification filter (Run Result Classification: {filter_params['run_result_classification']}), row count: {len(run_result_classification_filtered_df)}")

        # Extract the desired columns into a new DataFrame
        final_df = run_result_classification_filtered_df[["Log Filename", "Analyte Concentration"]].dropna()
        print(f"Final DataFrame row count: {len(final_df)}")

        # Clean the log filenames
        final_df["Cleaned Log Filename"] = final_df["Log Filename"].apply(self.clean_log_filename)

        end_time = time.time()
        print(f"Data loaded and filtered in {end_time - start_time:.2f} seconds.")
        return final_df

    def clean_log_filename(self, log_filename):
        cleaned_name = log_filename.replace("_dlog", "")
        return f"{cleaned_name}_dlog_recalc.xlsx"

    def extract_filtered_data(self, file_path):
        print(f"Extracting data from file: {file_path}")
        try:
            df = pd.read_excel(file_path)
            filtered_df = df[(df["Time from Start (sec)"] >= 0) & (df["Time from Start (sec)"] < 600)]
            print(f"Filtered data has {len(filtered_df)} rows")
            filtered_df["File Name"] = file_path  # Add file name to the DataFrame
            return filtered_df[["Time from Start (sec)", "UWA_BaselineCorr_2", "File Name"]]
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            return pd.DataFrame()
