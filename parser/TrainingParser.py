from __future__ import annotations

import json
import isodate
import glob
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import zipfile



class TrainingParser:
    def __init__(self, folder_of_zip_files: str | None = None, zip_file_pattern: str = "polar-user-data-export*", start_date: str = None, end_date: str = None):
        """Initialize the parser and find matching files.
        Args:
            folder_of_zip_files (str|None): Path to the folder containing zip files. If None, it will look in the current directory. Default is None. 
            zip_file_pattern (str): Pattern to match folders or zip files.
        """
        if folder_of_zip_files is not None:
            self.directory = Path(folder_of_zip_files)
        else:
            self.directory = Path.cwd()
        if not self.directory.exists():
            raise FileNotFoundError(f"The folder '{self.directory}' does not exist.")
        if not self.directory.is_dir():
            raise NotADirectoryError(f"The path '{self.directory}' is not a directory.")
        
        self.folder_pattern = zip_file_pattern
        self.training_JSON_files = []
        self.training_summary = pd.DataFrame()
        self.training_hr_samples = []
        self.training_hr_df = pd.DataFrame()
        self.start_date = datetime.strptime(start_date, "%Y-%m-%d") if start_date else None
        self.end_date = datetime.strptime(end_date, "%Y-%m-%d") if end_date else None
        self.process_all_files()


    def process_all_files(self) -> list:
        """Finds all training session JSON files in the first matching folder."""
        matching_folders = [str(folder) for folder in self.directory.glob(self.folder_pattern)]
        if not matching_folders:
            print("No matching folders or zip files found at:", self.folder_pattern)
            return []
        for folder in matching_folders:
            # print(f"Found folder: {folder}")
            folder_path = Path(folder)
            with zipfile.ZipFile(folder_path, 'r') as zip_ref:
                for filemember in zip_ref.namelist():
                    if filemember.startswith('account-data') and filemember.endswith('.json'):
                        # print(f"Found account data JSON file: {filemember}")
                        # load json file
                        with zip_ref.open(filemember) as file:
                            # Read the JSON content, get exercises
                            # print(f"Reading JSON file: {filemember}")
                            content = json.load(file)
                            username = content.get("username", {})
                            break
                for filemember in zip_ref.namelist():
                    if filemember.startswith("training-session") and filemember.endswith(".json"):
                        # print(f"Found training session JSON file: {filemember}")
                        # append name to list
                        self.training_JSON_files.append(filemember)
                        # load json file
                        with zip_ref.open(filemember) as file:
                            # Read the JSON content, get exercises
                            # print(f"Reading JSON file: {filemember}")
                            content = json.load(file)
                            exercises = content.get("exercises", {})
                            # parse exercise summary
                            self.parse_exercise_summary(exercises, username)
                            # parse heart rate samples
                            self.parse_hr_samples(exercises, username)
                        

        folder_path = Path(matching_folders[0])  # Use the first matching folder, should be updated to handle multiple folders!!!
        return [f for f in folder_path.glob("training-session*.json")]


    def parse_exercise_summary(self, exercises: list, username:str):
        """Parses exercise summary and appends to the DataFrame."""
        exercise_list = []
        for ex in exercises:
            try:
                start = datetime.fromisoformat(ex["startTime"]) + timedelta(minutes=ex.get("timezoneOffset", 0))
                stop = datetime.fromisoformat(ex["stopTime"]) + timedelta(minutes=ex.get("timezoneOffset", 0))
                duration = isodate.parse_duration(ex.get("duration", "PT0S")).total_seconds()
                
                # Check if the exercise is within the specified date range
                if self.start_date and start < self.start_date:
                    continue
                if self.end_date and stop > self.end_date:
                    continue

                exercise_list.append({
                    "username": username,
                    "start": start,
                    "stop": stop,
                    "duration_sec": duration,
                    "calories": ex.get("kiloCalories", 0),
                    "hr_avg": ex.get("heartRate", {}).get("avg"),
                    "hr_min": ex.get("heartRate", {}).get("min"),
                    "hr_max": ex.get("heartRate", {}).get("max"),
                    "sport": ex.get("sport", "")
                })
            except (KeyError, ValueError, TypeError) as e:
                print(f"Skipping invalid exercise entry: {e}")

        self.training_summary = pd.concat([self.training_summary, pd.DataFrame(exercise_list)], ignore_index=True)


    def parse_hr_samples(self, exercises: list, username: str) -> pd.DataFrame:
        """Parses heart rate samples and returns a DataFrame."""
        hr_samples = []
        for ex in exercises:
        
            try:
                for sample in ex.get("samples", {}).get("heartRate", []):
                    sample_time = datetime.fromisoformat(sample["dateTime"]) + timedelta(minutes=ex.get("timezoneOffset", 0))
                    # Check if the sample is within the specified date range
                    if self.start_date and sample_time < self.start_date:
                        continue
                    if self.end_date and sample_time > self.end_date:
                        continue
                    hr_samples.append({"username": username, "dateTime": sample_time, "heartRate": sample["value"]})
            except (KeyError) as e:
                print(f"Missing heart rate value for timepoint {sample['dateTime']}")
        hr_df = pd.DataFrame(hr_samples)

        if not hr_df.empty:
            self.training_hr_samples.append(hr_df)
            self.training_hr_df = pd.concat([self.training_hr_df, hr_df], ignore_index=True)


