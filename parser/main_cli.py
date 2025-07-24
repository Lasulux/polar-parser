#!/usr/bin/env python3

import argparse
import re
import os
import pandas as pd
from tqdm.auto import tqdm
from TrainingParser import TrainingParser
from ActivityParser import ActivityParser
from SleepParser import SleepParser
from save_data import save_data_files
from datetime import datetime


def process_polar_data(zip_data_directory, output_dir, save_format, start_date=None, end_date=None):
    tqdm.write(f"Processing data from: {zip_data_directory}")

    training_parser = TrainingParser(
        folder_of_zip_files=zip_data_directory,
        zip_file_pattern="polar-user-data-export*",
        start_date=start_date,
        end_date=end_date,
    )
    tqdm.write(f"End of training parser. Found {len(training_parser.training_JSON_files)} training session files.")
    training_summary = training_parser.training_summary
    training_hr_df = training_parser.training_hr_df

    activity_parser = ActivityParser(
        folder_of_zip_files=zip_data_directory,
        zip_file_pattern="polar-user-data-export*",
        start_date=start_date,
        end_date=end_date,
    )
    tqdm.write(f"End of activity parser. Found {str(activity_parser.activity_summary.size)} activity files.")
    activity_summary = activity_parser.activity_summary
    step_series = activity_parser.step_series_df
    activity_hr = activity_parser.hr_247_df

    sleep_parser = SleepParser(
        folder_of_zip_files=zip_data_directory,
        zip_file_pattern="polar-user-data-export*",
        start_date=start_date,
        end_date=end_date,
    )
    sleep_wake_samples = sleep_parser.sleep_wake_samples
    sleep_scores = sleep_parser.sleep_scores
    sleep_result = sleep_parser.sleep_result
    hypnogram = sleep_parser.hypnogram
    nightly_recovery_hrv_data = sleep_parser.nightly_recovery_hrv_data
    nightly_recovery_breathing_data = sleep_parser.nightly_recovery_breathing_data
    nightly_recovery_summary = sleep_parser.nightly_recovery_summary

    users = activity_summary["username"].unique()
    if save_format is not None:
        for user in tqdm(users, desc="Saving user data"):
            user_training_summary = training_summary[training_summary["username"] == user]
            user_training_hr_df = training_hr_df[training_hr_df["username"] == user]
            user_activity_summary = activity_summary[activity_summary["username"] == user]
            user_step_series = step_series[step_series["username"] == user]
            user_activity_hr = activity_hr[activity_hr["username"] == user]
            user_sleep_wake_samples = sleep_wake_samples[sleep_wake_samples["username"] == user]
            user_sleep_scores = sleep_scores[sleep_scores["username"] == user]
            user_sleep_result = sleep_result[sleep_result["username"] == user]
            user_hypnogram = hypnogram[hypnogram["username"] == user]
            user_nightly_recovery_hrv_data = nightly_recovery_hrv_data[nightly_recovery_hrv_data["username"] == user]
            user_nightly_recovery_breathing_data = nightly_recovery_breathing_data[
                nightly_recovery_breathing_data["username"] == user
            ]
            user_nightly_recovery_summary = nightly_recovery_summary[nightly_recovery_summary["username"] == user]

            match = re.search(r"\.(\d+)@", user)
            if not match:
                tqdm.write(f"Could not extract folder name for user: {user}")
                continue
            folder_name = match.group(1)

            data_to_save = {
                "training_summary": user_training_summary,
                "training_hr_samples": user_training_hr_df,
                "activity_summary": user_activity_summary,
                "step_series": user_step_series,
                "activity_hr": user_activity_hr,
                "sleep_wake_samples": user_sleep_wake_samples,
                "sleep_scores": user_sleep_scores,
                "sleep_result": user_sleep_result,
                "hypnogram": user_hypnogram,
                "nightly_recovery_hrv_data": user_nightly_recovery_hrv_data,
                "nightly_recovery_breathing_data": user_nightly_recovery_breathing_data,
                "nightly_recovery_summary": user_nightly_recovery_summary,
            }
            save_data_files(folder_name, data_to_save, output_dir, save_format=save_format)
            tqdm.write(f"\n Saved files for user: {user} in: {os.path.join(output_dir, folder_name)}")


def main():
    parser = argparse.ArgumentParser(description="Process and export Polar user data.")
    parser.add_argument("--input-dir", type=str, default="../input", help="Path to directory containing zip files")
    parser.add_argument("--output-dir", type=str, default="../output", help="Directory where output will be saved")
    parser.add_argument(
        "--start-date",
        type=str,
        default=None,
        help="Date to start processing data from (YYYY-MM-DD). If not provided, all data will be processed.",
    )
    parser.add_argument(
        "--end-date",
        type=str,
        default=datetime.now().strftime("%Y-%m-%d"),
        help="Date to end processing data (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--save-format",
        type=str,
        choices=["csv", "excel", "both", "none"],
        default="csv",
        help="Save format for the data: csv, excel, both or none",
    )

    args = parser.parse_args()

    save_format = None if args.save_format == "none" else args.save_format

    # Validate start_date and end_date
    try:
        if args.start_date:
            datetime.strptime(args.start_date, "%Y-%m-%d")
        if args.end_date:
            datetime.strptime(args.end_date, "%Y-%m-%d")
    except ValueError as e:
        tqdm.write(f"Error: Invalid date format. Dates must be in YYYY-MM-DD format. {e}")
        exit(1)

    process_polar_data(args.input_dir, args.output_dir, save_format, args.start_date, args.end_date)


if __name__ == "__main__":
    main()
