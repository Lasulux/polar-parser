import re
import os
import pandas as pd
from tqdm.auto import tqdm
from TrainingParser import TrainingParser
from ActivityParser import ActivityParser
from save_data import save_data_files

# Process json files containing data exported from Polar website

zip_data_directory = "../input"
output_dir = "../output"
save_format = "csv"  # save files in excel, csv, both or None (saving files as .csv is much faster)

training_parser = TrainingParser(folder_of_zip_files=zip_data_directory, zip_file_pattern="polar-user-data-export*")
training_summary = training_parser.training_summary
training_hr_df = training_parser.training_hr_df

activity_parser = ActivityParser(folder_of_zip_files=zip_data_directory, zip_file_pattern="polar-user-data-export*")
activity_summary = activity_parser.activity_summary
step_series = activity_parser.step_series_df
acitivty_hr = activity_parser.hr_247_df

users = activity_summary["username"].unique()
if save_format is not None:
    for user in tqdm(users):
        # Filter data for the current user
        user_training_summary = training_summary[training_summary["username"] == user]
        user_training_hr_df = training_hr_df[training_hr_df["username"] == user]
        user_activity_summary = activity_summary[activity_summary["username"] == user]
        user_step_series = step_series[step_series["username"] == user]
        user_activity_hr = acitivty_hr[acitivty_hr["username"] == user]

        # Extract folder name using regex: numbers between '.' and '@'
        match = re.search(r"\.(\d+)@", user)
        if not match:
            tqdm.write(f"Could not extract folder name for user: {user}")
            continue
        folder_name = match.group(1)

        # Save data in Excel
        data_to_save = {
            "training_summary": user_training_summary,
            "training_hr_samples": user_training_hr_df,
            "activity_summary": user_activity_summary,
            "step_series": user_step_series,
            "activity_hr": user_activity_hr,
        }
        save_data_files(folder_name, data_to_save, output_dir, save_format=save_format)
        tqdm.write(f"\n Saved Excel files for user: {user} in folder: {os.path.join(output_dir, folder_name)}")
