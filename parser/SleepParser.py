from __future__ import annotations

import json
import isodate
import glob
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import zipfile
from tqdm import tqdm


class SleepParser:
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
        self.sleep_JSON_files = []
        self.nightly_recovery_summary = pd.DataFrame(columns=['username', 'date', 'night'])
        self.nightly_recovery_hrv_data = pd.DataFrame()
        self.nightly_recovery_breathing_data = pd.DataFrame()
        self.sleep_result = pd.DataFrame(columns=['username', 'date', 'night'])
        self.sleep_scores = pd.DataFrame(columns=['username', 'date', 'night', 'sleepScore'])
        self.sleep_wake_samples = pd.DataFrame(columns=['username', 'datetime', 'state'])
        self.hypnogram = pd.DataFrame(columns=['username', 'date', 'night', 'datetime', 'state'])

        self.start_date = datetime.strptime(start_date, "%Y-%m-%d") if start_date else None
        self.end_date = datetime.strptime(end_date, "%Y-%m-%d") if end_date else None
        self.process_all_files()


    def process_all_files(self) -> list:
        """Finds all sleep JSON files in the first matching folder."""
        matching_folders = [str(folder) for folder in self.directory.glob(self.folder_pattern)]
        if not matching_folders:
            print("No matching folders or zip files found at:", self.folder_pattern)
            return []
        for folder in tqdm(matching_folders, desc="Processing sleep folders"):
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
                    if (filemember.startswith("sleep") or filemember.startswith("nightly")) and filemember.endswith(".json"):
                        # print(f"Found sleep JSON file: {filemember}")
                        # append name to list
                        self.sleep_JSON_files.append(filemember)
                        # load json file
                        with zip_ref.open(filemember) as file:
                            # Read the JSON content, get sleep data
                            # print(f"Reading JSON file: {filemember}")
                            content = json.load(file)
                            if filemember.startswith("sleep_wake"):
                                self.parse_sleep_wake_samples(content, username)
                            elif filemember.startswith("sleep_score"):
                                self.parse_sleep_score(content, username)
                            elif filemember.startswith("sleep_result"):
                                self.parse_sleep_result(content, username)
                            elif filemember.startswith("nightly_recovery_blob"):
                                self.parse_nightly_recovery_blob(content, username)
                            elif filemember.startswith("nightly_recovery"):
                                self.parse_nightly_recovery(content, username)
        # folder_path = Path(matching_folders[0])  # Use the first matching folder, should be updated to handle multiple folders!!!
        # return [f for f in folder_path.glob("sleep*.json") + folder_path.glob("nightly*.json")]


    def parse_sleep_wake_samples(self, content, username: str):
        """Parses sleep wake samples and appends to the DataFrame."""
        sleep_wake_data = []
        
        # Iterate through each night's data
        for night_data in content:
            night_date = night_data.get("night")
            if not night_date:
                continue
                
            # Parse the night date
            try:
                night_datetime = datetime.strptime(night_date, "%Y-%m-%d")
            except ValueError:
                print(f"Warning: Could not parse night date: {night_date}")
                continue
            
            # Check if the night is within the date range filter
            if self.start_date and night_datetime < self.start_date:
                continue
            if self.end_date and night_datetime > self.end_date:
                continue
            
            # Process sleep wake data for this night
            sleep_wake_list = night_data.get("sleepWake", [])
            for sleep_wake_entry in sleep_wake_list:
                sleep_state_changes = sleep_wake_entry.get("sleepStateChanges", {})
                state_change_models = sleep_state_changes.get("sleepWakeStateChangeModels", [])
                
                # Process each state change
                for state_change in state_change_models:
                    millis_in_day = state_change.get("millisInDay")
                    state = state_change.get("state")
                    
                    if millis_in_day is not None and state:
                        # Convert milliseconds in day to datetime
                        # millisInDay is milliseconds from midnight
                        seconds_in_day = millis_in_day / 1000
                        time_delta = timedelta(seconds=seconds_in_day)
                        
                        # Add the time delta to the night date
                        state_change_datetime = night_datetime + time_delta
                        
                        # Add to our data list
                        sleep_wake_data.append({
                            'username': username,
                            'datetime': state_change_datetime,
                            'state': state
                        })
        
        # Create DataFrame from the collected data
        if sleep_wake_data:
            sleep_wake_changes = pd.DataFrame(sleep_wake_data)
            self.sleep_wake_samples = pd.concat([self.sleep_wake_samples, sleep_wake_changes], ignore_index=True)
        else:
            # If no data, create empty DataFrame with correct columns
            sleep_wake_changes = pd.DataFrame(columns=['username', 'datetime', 'state'])
            self.sleep_wake_samples = pd.concat([self.sleep_wake_samples, sleep_wake_changes], ignore_index=True)

    def parse_sleep_score(self, content, username: str):
        """Parses sleep score data and appends to the DataFrame."""
        sleep_score_data = []
        
        # Iterate through each night's data
        for night_data in content:
            night_date = night_data.get("night")
            if not night_date:
                continue
                
            # Parse the night date
            try:
                night_datetime = datetime.strptime(night_date, "%Y-%m-%d")
            except ValueError:
                print(f"Warning: Could not parse night date: {night_date}")
                continue
            
            # Check if the night is within the date range filter
            if self.start_date and night_datetime < self.start_date:
                continue
            if self.end_date and night_datetime > self.end_date:
                continue
            
            # Get sleep score result data (excluding baselines)
            sleep_score_result = night_data.get("sleepScoreResult", {})
            
            if sleep_score_result:
                # Create a row with username and date
                row_data = {
                    'username': username,
                    'date': night_datetime.date(),
                    'night': night_date
                }
                
                # Add all sleep score metrics (excluding baseline data)
                for key, value in sleep_score_result.items():
                    row_data[key] = value
                
                sleep_score_data.append(row_data)
        
        # Create DataFrame from the collected data
        if sleep_score_data:
            sleep_score_df = pd.DataFrame(sleep_score_data)
            self.sleep_scores = pd.concat([self.sleep_scores, sleep_score_df], ignore_index=True)
        else:
            # If no data, create empty DataFrame with basic columns
            empty_df = pd.DataFrame(columns=['username', 'date', 'night'])
            self.sleep_scores = pd.concat([self.sleep_scores, empty_df], ignore_index=True)
    
    def parse_sleep_result(self, content, username: str):
        """Parses sleep result data and appends to the DataFrames sleep result and hypnogram."""
        sleep_result_data = []
        hypnogram_data = []
        
        # Iterate through each night's data
        for night_data in content:
            night_date = night_data.get("night")
            if not night_date:
                continue
                
            # Parse the night date
            try:
                night_datetime = datetime.strptime(night_date, "%Y-%m-%d")
            except ValueError:
                print(f"Warning: Could not parse night date: {night_date}")
                continue
            
            # Check if the night is within the date range filter
            if self.start_date and night_datetime < self.start_date:
                continue
            if self.end_date and night_datetime > self.end_date:
                continue
            
            # Parse evaluation data for sleep result summary
            evaluation = night_data.get("evaluation", {})
            if evaluation:
                # Create a row with username and date
                result_row = {
                    'username': username,
                    'date': night_datetime.date(),
                    'night': night_date
                }
                
                # Add evaluation fields, converting ISO durations to minutes where applicable
                for key, value in evaluation.items():
                    if key in ['sleepSpan', 'asleepDuration'] and isinstance(value, str) and value.startswith('PT'):
                        # Convert ISO 8601 duration to total minutes
                        try:
                            duration = isodate.parse_duration(value)
                            result_row[f"{key}_minutes"] = duration.total_seconds() / 60
                            result_row[key] = value  # Keep original format too
                        except:
                            result_row[key] = value
                    elif key == 'interruptions' and isinstance(value, dict):
                        # Flatten interruptions data
                        for int_key, int_value in value.items():
                            if int_key in ['totalDuration', 'shortDuration', 'longDuration'] and isinstance(int_value, str) and int_value.startswith('PT'):
                                try:
                                    duration = isodate.parse_duration(int_value)
                                    result_row[f"interruptions_{int_key}_minutes"] = duration.total_seconds() / 60
                                    result_row[f"interruptions_{int_key}"] = int_value
                                except:
                                    result_row[f"interruptions_{int_key}"] = int_value
                            else:
                                result_row[f"interruptions_{int_key}"] = int_value
                    elif key == 'analysis' and isinstance(value, dict):
                        # Flatten analysis data
                        for anal_key, anal_value in value.items():
                            result_row[f"analysis_{anal_key}"] = anal_value
                    elif key == 'phaseDurations' and isinstance(value, dict):
                        # Flatten phase durations
                        for phase_key, phase_value in value.items():
                            if phase_key in ['wake', 'rem', 'light', 'deep', 'unknown'] and isinstance(phase_value, str) and phase_value.startswith('PT'):
                                try:
                                    duration = isodate.parse_duration(phase_value)
                                    result_row[f"phaseDurations_{phase_key}_minutes"] = duration.total_seconds() / 60
                                    result_row[f"phaseDurations_{phase_key}"] = phase_value
                                except:
                                    result_row[f"phaseDurations_{phase_key}"] = phase_value
                            else:
                                result_row[f"phaseDurations_{phase_key}"] = phase_value
                    else:
                        result_row[key] = value
                
                sleep_result_data.append(result_row)
            
            # Parse hypnogram data for sleep state changes
            sleep_result = night_data.get("sleepResult", {})
            hypnogram = sleep_result.get("hypnogram", {})
            
            if hypnogram:
                sleep_start_str = hypnogram.get("sleepStart")
                sleep_state_changes = hypnogram.get("sleepStateChanges", [])
                
                # Parse sleep start time
                sleep_start_datetime = None
                if sleep_start_str:
                    try:
                        # Handle ISO 8601 datetime format
                        sleep_start_datetime = datetime.fromisoformat(sleep_start_str.replace('Z', '+00:00'))
                    except:
                        print(f"Warning: Could not parse sleep start time: {sleep_start_str}")
                
                # Process each sleep state change
                for state_change in sleep_state_changes:
                    offset_str = state_change.get("offsetFromStart")
                    state = state_change.get("state")
                    
                    if offset_str and state and sleep_start_datetime:
                        try:
                            # Parse ISO 8601 duration offset
                            offset_duration = isodate.parse_duration(offset_str)
                            state_change_datetime = sleep_start_datetime + offset_duration
                            
                            # Add to hypnogram data
                            hypnogram_data.append({
                                'username': username,
                                'date': night_datetime.date(),
                                'night': night_date,
                                'datetime': state_change_datetime,
                                'state': state,
                                'offset_from_start': offset_str,
                                'offset_minutes': offset_duration.total_seconds() / 60
                            })
                        except Exception as e:
                            print(f"Warning: Could not parse state change offset: {offset_str} - {e}")
        
        # Create DataFrames from the collected data
        if sleep_result_data:
            sleep_result_df = pd.DataFrame(sleep_result_data)
            self.sleep_result = pd.concat([self.sleep_result, sleep_result_df], ignore_index=True)
        
        if hypnogram_data:
            hypnogram_df = pd.DataFrame(hypnogram_data)
            self.hypnogram = pd.concat([self.hypnogram, hypnogram_df], ignore_index=True)
    def parse_nightly_recovery_blob(self, content, username: str):
        """Parses nightly recovery blob data and appends to the DataFrames for hrv and breathing."""
        hrv_data = []
        breathing_data = []
        
        # Iterate through each night's data
        for night_data in content:
            # HRV data is at the root level with a date that needs to be inferred
            # from the startTime of the data
            
            # Process HRV data
            hrv_data_list = night_data.get("hrvData", [])
            for hrv_session in hrv_data_list:
                start_time_str = hrv_session.get("startTime")
                sampling_interval_ms = hrv_session.get("samplingIntervalInMillis")
                samples = hrv_session.get("samples", [])
                
                if start_time_str and sampling_interval_ms and samples:
                    try:
                        # Parse start time (format: "2025-02-27T01:18:47")
                        start_datetime = datetime.fromisoformat(start_time_str)
                        night_date = start_datetime.date()
                        
                        # Check if the night is within the date range filter
                        if self.start_date and start_datetime.date() < self.start_date.date():
                            continue
                        if self.end_date and start_datetime.date() > self.end_date.date():
                            continue
                        
                        # Convert sampling interval from milliseconds to timedelta
                        sampling_interval = timedelta(milliseconds=sampling_interval_ms)
                        
                        # Process each sample with its timestamp
                        for i, sample_value in enumerate(samples):
                            sample_datetime = start_datetime + (sampling_interval * i)
                            
                            hrv_data.append({
                                'username': username,
                                'date': night_date,
                                'datetime': sample_datetime,
                                'hrv_value': sample_value,
                                'sampling_interval_ms': sampling_interval_ms,
                                'sample_index': i
                            })
                    except Exception as e:
                        print(f"Warning: Could not parse HRV data for {start_time_str}: {e}")
            
            # Process breathing rate data
            breathing_data_list = night_data.get("breathingRateData", [])
            for breathing_session in breathing_data_list:
                start_time_str = breathing_session.get("startTime")
                sampling_interval_ms = breathing_session.get("samplingIntervalInMillis")
                samples = breathing_session.get("samples", [])
                
                if start_time_str and sampling_interval_ms and samples:
                    try:
                        # Parse start time (format: "2025-02-27T01:16:17")
                        start_datetime = datetime.fromisoformat(start_time_str)
                        night_date = start_datetime.date()
                        
                        # Check if the night is within the date range filter
                        if self.start_date and start_datetime.date() < self.start_date.date():
                            continue
                        if self.end_date and start_datetime.date() > self.end_date.date():
                            continue
                        
                        # Convert sampling interval from milliseconds to timedelta
                        sampling_interval = timedelta(milliseconds=sampling_interval_ms)
                        
                        # Process each sample with its timestamp
                        for i, sample_value in enumerate(samples):
                            sample_datetime = start_datetime + (sampling_interval * i)
                            
                            breathing_data.append({
                                'username': username,
                                'date': night_date,
                                'datetime': sample_datetime,
                                'breathing_rate': sample_value,
                                'sampling_interval_ms': sampling_interval_ms,
                                'sample_index': i
                            })
                    except Exception as e:
                        print(f"Warning: Could not parse breathing data for {start_time_str}: {e}")
        
        # Create DataFrames from the collected data
        if hrv_data:
            hrv_df = pd.DataFrame(hrv_data)
            self.nightly_recovery_hrv_data = pd.concat([self.nightly_recovery_hrv_data, hrv_df], ignore_index=True)
        
        if breathing_data:
            breathing_df = pd.DataFrame(breathing_data)
            self.nightly_recovery_breathing_data = pd.concat([self.nightly_recovery_breathing_data, breathing_df], ignore_index=True)


    def parse_nightly_recovery(self, content, username: str):
        """Parses nightly recovery data and appends to the DataFrame."""
        recovery_data = []
        
        # Iterate through each night's data
        for night_data in content:
            night_date = night_data.get("night")
            if not night_date:
                continue
                
            # Parse the night date
            try:
                night_datetime = datetime.strptime(night_date, "%Y-%m-%d")
            except ValueError:
                print(f"Warning: Could not parse night date: {night_date}")
                continue
            
            # Check if the night is within the date range filter
            if self.start_date and night_datetime < self.start_date:
                continue
            if self.end_date and night_datetime > self.end_date:
                continue
            
            # Create a row with username and date
            row_data = {
                'username': username,
                'date': night_datetime.date(),
                'night': night_date
            }
            
            # Add all recovery metrics from the JSON
            for key, value in night_data.items():
                if key != "night":  # Skip the night key as we already processed it
                    row_data[key] = value
            
            recovery_data.append(row_data)
        
        # Create DataFrame from the collected data
        if recovery_data:
            recovery_df = pd.DataFrame(recovery_data)
            self.nightly_recovery_summary = pd.concat([self.nightly_recovery_summary, recovery_df], ignore_index=True)
        else:
            # If no data, create empty DataFrame with basic columns
            empty_df = pd.DataFrame(columns=['username', 'date', 'night'])
            self.nightly_recovery_summary = pd.concat([self.nightly_recovery_summary, empty_df], ignore_index=True)
        
