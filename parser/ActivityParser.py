from __future__ import annotations

import json
import pandas as pd
from pathlib import Path
from datetime import datetime
import zipfile
from tqdm.auto import tqdm


class ActivityParser:
    def __init__(
        self,
        folder_of_zip_files: str | None = None,
        zip_file_pattern: str = "polar-user-data-export*",
        start_date: str = None,
        end_date: str = None,
    ):
        """Initialize the parser and process activity & 24/7 HR data."""
        self.directory = Path(folder_of_zip_files) if folder_of_zip_files else Path.cwd()
        if not self.directory.exists():
            raise FileNotFoundError(f"The folder '{self.directory}' does not exist.")
        if not self.directory.is_dir():
            raise NotADirectoryError(f"The path '{self.directory}' is not a directory.")

        self.folder_pattern = zip_file_pattern
        self.activity_summary = pd.DataFrame()
        self.step_series_df = pd.DataFrame()
        self.hr_247_df = pd.DataFrame()
        self.username = None
        self.start_date = datetime.strptime(start_date, "%Y-%m-%d") if start_date else None
        self.end_date = datetime.strptime(end_date, "%Y-%m-%d") if end_date else None
        tqdm.write(f"Processing activity data from: {self.directory}")
        self.process_all_files()

    def process_all_files(self):
        """Process all matched ZIP files and extract activity and 24/7 HR data."""
        tqdm.write(f"Looking for files matching pattern: {self.folder_pattern}")
        matching_zips = [str(zip_path) for zip_path in self.directory.glob(self.folder_pattern)]
        tqdm.write(f"Found {len(matching_zips)} matching ZIP files.")
        if not matching_zips:
            tqdm.write("No matching ZIP files found.")
            return

        for zip_path in tqdm(matching_zips, desc="Processing ZIP files"):
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                for filemember in tqdm(zip_ref.namelist(), desc=f"Extracting files from {zip_path}"):
                    if filemember.startswith("account-data") and filemember.endswith(".json"):
                        with zip_ref.open(filemember) as file:
                            content = json.load(file)
                            self.username = content.get("username", {})
                            break
                for filemember in tqdm(zip_ref.namelist(), desc=f"Parsing files in {zip_path}"):
                    if filemember.startswith("activity-") and filemember.endswith(".json"):
                        with zip_ref.open(filemember) as file:
                            data = json.load(file)
                            self.parse_activity_file(data)
                    elif filemember.startswith("247ohr_") and filemember.endswith(".json"):
                        with zip_ref.open(filemember) as file:
                            data = json.load(file)
                            self.parse_247ohr_file(data)

    def parse_activity_file(self, data: dict):
        """Extracts activity summary + steps."""
        try:
            date = data.get("date")
            summary = data.get("summary", {})
            steps = data.get("samples", {}).get("steps", [])

            # Filter by date if start_date and end_date are provided
            if self.start_date or self.end_date:
                date_obj = datetime.strptime(date, "%Y-%m-%d")
                if self.start_date and date_obj < self.start_date:
                    # each activity file contains only one day of data, so we skip the whole file if the date is out of range
                    return
                if self.end_date and date_obj > self.end_date:
                    return

            tqdm.write(f"Parsing activity data for date: {date}")
            activity_entry = {
                "username": self.username,
                "date": date,
                "start": summary.get("startTime"),
                "end": summary.get("endTime"),
                "calories": summary.get("calories"),
                "step_total": summary.get("stepCount"),
            }

            self.activity_summary = pd.concat(
                [self.activity_summary, pd.DataFrame([activity_entry])], ignore_index=True
            )

            # Time series step data (many per day)
            if steps:
                tqdm.write(f"Processing step data for date: {date}")
                step_df = pd.DataFrame(steps)
                step_df["username"] = self.username
                step_df["date"] = date  # associate samples with their day
                # date has been filtered at this point, so we can use it directly
                # # reorder
                # step_df = step_df[
                #     ["username", "date"] + [col for col in step_df.columns if col not in ["username", "date"]]
                # ]
                self.step_series_df = pd.concat([self.step_series_df, step_df], ignore_index=True)

        except Exception as e:
            tqdm.write(f"Error parsing activity file: {e}")

    def parse_247ohr_file(self, data: dict):
        """Extracts 24/7 heart rate samples."""
        try:
            for day in tqdm(data.get("deviceDays", []), desc="Processing 24/7 HR data"):
                user_id = day.get("userId")
                date = day.get("date")
                # Filter by date if start_date and end_date are provided
                if self.start_date or self.end_date:
                    date_obj = datetime.strptime(date, "%Y-%m-%d")
                    if self.start_date and date_obj < self.start_date:
                        continue
                    if self.end_date and date_obj > self.end_date:
                        continue
                samples = day.get("samples", [])
                # Filter out empty samples
                if not samples:
                    continue

                tqdm.write(f"Parsing 24/7 HR data for date: {date}")
                day_hr_df = pd.DataFrame(samples)
                day_hr_df["userId"] = user_id
                day_hr_df["date"] = date
                day_hr_df["username"] = self.username
                # Convert seconds from day start to time of day
                day_hr_df["timeOfDay"] = day_hr_df["secondsFromDayStart"].apply(
                    lambda x: (datetime.min + pd.to_timedelta(x, unit="s")).time()
                )

                # reorder columns
                day_hr_df = day_hr_df[
                    ["username", "date", "timeOfDay", "heartRate"]
                    + [col for col in day_hr_df.columns if col not in ["username", "date", "timeOfDay", "heartRate"]]
                ]
                # append to the main dataframe
                self.hr_247_df = pd.concat([self.hr_247_df, day_hr_df], ignore_index=True)

        except Exception as e:
            tqdm.write(f"Error parsing 24/7 HR file: {e}")
