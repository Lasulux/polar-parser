# You can ignore this file


import os
import zipfile
from tqdm.auto import tqdm
import json
import pandas as pd

# Path to the folder containing zip files
zip_folder_path = os.path.join(os.path.dirname(__file__), "zip_folder")

# Ensure the folder exists
if not os.path.exists(zip_folder_path):
    raise FileNotFoundError(f"The folder '{zip_folder_path}' does not exist.")

# Iterate through each file in the folder
zip_files = [file_name for file_name in os.listdir(zip_folder_path) if file_name.endswith(".zip")]

for file_name in tqdm(zip_files, desc="Processing zip files"):
    zip_file_path = os.path.join(zip_folder_path, file_name)
    # Open the zip file
    with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
        tqdm.write(f"Opened zip file: {file_name}")
        # Print filename last 7 characters
        tqdm.write(f"TTK User ID: {file_name[-11:-4]}")
        # List contents of the zip file
        # tqdm.write(zip_ref.namelist())
        # Iterate files in the zip file

        # Initialize activity df
        activity_df = pd.DataFrame()

        for member in zip_ref.namelist():
            # check if file is for activity
            if member.startswith("activity-"):
                # Read JSON file
                with zip_ref.open(member) as file:
                    # Read the JSON content
                    content = json.load(file)
                    # each activity file is a dictionary

                    break
