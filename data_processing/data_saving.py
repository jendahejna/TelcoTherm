import os
import numpy as np
import datetime


class DataSaving:
    def __init__(self, save_directory="saved_grids"):
        self.save_directory = save_directory
        if not os.path.exists(self.save_directory):
            os.makedirs(self.save_directory)
            print("A new directory has been created to save data.")

    def save_grid(self, grid_x, grid_y, grid_z_masked):
        current_time = datetime.datetime.now()
        file_name = f"z_grid_{current_time.strftime('%Y-%m-%d-%H-%M')}.npy"
        grid_path = os.path.join(self.save_directory, file_name)
        np.save(grid_path, grid_z_masked)

        print(f"Grid data has been saved to: {grid_path}")

