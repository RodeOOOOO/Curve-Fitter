import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use a non-GUI backend suitable for background processing
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import time

class Plotting:
    def __init__(self, base_dir, filter_name):
        self.base_dir = base_dir
        self.filter_dir = os.path.join(self.base_dir, filter_name)  # Add the filter parameter layer
        os.makedirs(self.filter_dir, exist_ok=True)

        self.overall_visuals_dir = os.path.join(self.filter_dir, "overall", "overall_visuals")
        os.makedirs(self.overall_visuals_dir, exist_ok=True)
        self.overall_org_dir = os.path.join(self.filter_dir, "overall", "overall_org")
        os.makedirs(self.overall_org_dir, exist_ok=True)
        self.individual_visuals_dir = os.path.join(self.filter_dir, "individual")
        os.makedirs(self.individual_visuals_dir, exist_ok=True)

    def safe_exp(self, x):
        # Clamp the values to avoid overflow in exp
        return np.exp(np.clip(x, -500, 500))

    def sigmoid(self, x, L, x0, k, b):
        # Use the safe exponential to avoid overflow
        return L / (1 + self.safe_exp(-k * (x - x0))) + b

    def compute_and_plot_individual(self, uwa_data_by_concentration):
        all_fits = []
        plt.figure()

        for concentration, data_list in uwa_data_by_concentration.items():
            # Create directory for individual concentration plots
            concentration_dir = os.path.join(self.individual_visuals_dir, str(concentration))
            os.makedirs(concentration_dir, exist_ok=True)

            all_x_data = np.array([])
            all_y_data = np.array([])

            # Create a figure for the individual concentration plot
            plt.figure()

            for data in data_list:
                x_data = data["Time from Start (sec)"]
                y_data = data["UWA_BaselineCorr_2"]

                all_x_data = np.concatenate((all_x_data, x_data))
                all_y_data = np.concatenate((all_y_data, y_data))

                # Plot data for the individual concentration
                plt.plot(x_data, y_data, alpha=0.5)

            # Fit sigmoid to the combined data
            try:
                p0 = [max(all_y_data), np.median(all_x_data), 1, min(all_y_data)]
                popt, _ = curve_fit(self.sigmoid, all_x_data, all_y_data, p0, method='trf', maxfev=10000)
                x_fit = np.linspace(min(all_x_data), max(all_x_data), 1000)
                y_fit = self.sigmoid(x_fit, *popt)
                plt.plot(x_fit, y_fit, linestyle='--', color='#FF69B4')

                # Add vertical line for the minimum of the second derivative
                second_derivative = np.gradient(np.gradient(y_fit, x_fit), x_fit)
                min_index = np.argmin(second_derivative)
                plt.axvline(x=x_fit[min_index], color='#FF69B4', linestyle='--')

                all_fits.append((concentration, x_fit, y_fit))
            except Exception as e:
                print(f"Failed to fit sigmoid for concentration {concentration}: {e}")

            plt.xlabel("Time from Start (sec)")
            plt.ylabel("UWA_BaselineCorr_2")
            plt.title(f"UWA_BaselineCorr_2 for Concentration {concentration}")
            plt.grid(True)

            # Save individual plot
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            plot_path = os.path.join(concentration_dir, f"uwa_BaselineCorr_2_plot_{concentration}_{timestamp}.png")
            plt.savefig(plot_path)
            plt.close()

        # Sort the fits by concentration to ensure an ordinal relationship
        all_fits.sort(key=lambda x: x[0])  # Sort by concentration

        # Grouped plot
        plt.figure()
        for concentration, x_fit, y_fit in all_fits:
            line, = plt.plot(x_fit, y_fit, label=f'Sigmoid Fit {concentration}')

            # Add vertical line for minimum second derivative on the grouped plot
            second_derivative = np.gradient(np.gradient(y_fit, x_fit), x_fit)
            min_index = np.argmin(second_derivative)
            plt.axvline(x=x_fit[min_index], color=line.get_color(), linestyle='--')

        plt.legend(fontsize='x-small')
        plt.xlabel("Time from Start (sec)")
        plt.ylabel("UWA_BaselineCorr_2")
        plt.title("Grouped UWA_BaselineCorr_2 for All Concentrations")
        plt.grid(True)

        grouped_plot_path = os.path.join(self.overall_visuals_dir, f"grouped_uwa_BaselineCorr_2_plot_{timestamp}.png")
        plt.savefig(grouped_plot_path)
        plt.close()

        filenames_dict = {}
        max_length = 0  # Track the maximum length of the lists

        for concentration, data_list in uwa_data_by_concentration.items():
            filenames = [os.path.basename(data["File Name"].iloc[0]) for data in data_list]
            filenames_dict[concentration] = filenames
            if len(filenames) > max_length:
                max_length = len(filenames)

        # Ensure all lists have the same length by padding with None
        for concentration in filenames_dict:
            while len(filenames_dict[concentration]) < max_length:
                filenames_dict[concentration].append(None)

        filenames_df = pd.DataFrame(filenames_dict)
        csv_path = os.path.join(self.overall_org_dir, f"filenames_by_concentration_{timestamp}.csv")
        filenames_df.to_csv(csv_path, index=False)
        print(f"Filenames for concentrations saved to {csv_path}")