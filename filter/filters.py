import re
import os
import pandas as pd
from tqdm.auto import tqdm
from typing import Optional


class Filter:
    # Minimum date threshold - filter out data earlier than this date
    MIN_DATE = pd.Timestamp("2020-01-01")

    def __init__(self, input_dir: str, output_dir: str, overwrite: bool = False):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.overwrite = overwrite
        # Ensure directories exist
        try:
            if not os.path.exists(self.input_dir):
                tqdm.write(f"ERROR: Input directory does not exist: {self.input_dir}")
            if not os.path.exists(self.output_dir):
                tqdm.write(f"INFO: Creating output directory: {self.output_dir}")
                os.makedirs(self.output_dir)
        except Exception as e:
            tqdm.write(f"ERROR: Error creating directories: {e}")
            raise ValueError(f"Invalid directory paths: {e}")

    def _filter_by_date(self, df: pd.DataFrame, date_column: str) -> pd.DataFrame:
        """
        Filter DataFrame to keep only rows with dates >= MIN_DATE.
        Args:
            df (pd.DataFrame): DataFrame to filter.
            date_column (str): Name of the date column to filter on.
        Returns:
            pd.DataFrame: Filtered DataFrame.
        """
        if date_column not in df.columns:
            return df

        try:
            # Convert date column to datetime if it's not already
            if not pd.api.types.is_datetime64_any_dtype(df[date_column]):
                df[date_column] = pd.to_datetime(df[date_column])
            # Filter out rows earlier than MIN_DATE
            initial_count = len(df)
            df = df[df[date_column] >= self.MIN_DATE].copy()
            filtered_count = len(df)
            if initial_count != filtered_count:
                tqdm.write(
                    f"INFO: Filtered out {initial_count - filtered_count} rows earlier than {self.MIN_DATE.strftime('%Y-%m-%d')} from {date_column}"
                )
            return df
        except Exception as e:
            tqdm.write(f"WARNING: Error filtering by date in column {date_column}: {e}")
            return df

    def read_csv(self, file_path: str) -> pd.DataFrame:
        """
        Read a CSV file into a DataFrame.
        Args:
            file_path (str): Path to the CSV file.
        Returns:
            pd.DataFrame: DataFrame containing the CSV data.
        """
        try:
            df = pd.read_csv(file_path)
            tqdm.write(f"INFO: Successfully read {file_path}")
            return df
        except Exception as e:
            tqdm.write(f"ERROR: Error reading {file_path}: {e}")
            raise ValueError(f"Could not read CSV file: {e}")

    def activity_hr_table(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process activity heart rate data.
        Args:
            df (pd.DataFrame): DataFrame containing activity heart rate data.
        Returns:
            pd.DataFrame: Processed DataFrame with relevant columns.
        """
        # Filter by date first
        df = self._filter_by_date(df, "date")

        # Check if data is already processed (contains aggregated columns)
        if "heartRate_mean_overall" in df.columns:
            # Data is already processed, return as is
            return df

        # Filter out rows where heartRate == 0
        if "heartRate" in df.columns:
            df = df[df["heartRate"] != 0].copy()
            mean_hr = df["heartRate"].mean()
            median_hr = df["heartRate"].median()
            min_hr = df["heartRate"].min()
            max_hr = df["heartRate"].max()
            std_hr = df["heartRate"].std()
            df["heartRate_mean_overall"] = mean_hr
            df["heartRate_median_overall"] = median_hr
            df["heartRate_min_overall"] = min_hr
            df["heartRate_max_overall"] = max_hr
            df["heartRate_std_overall"] = std_hr

            # Calculate daily statistics if 'date' column exists
            if "date" in df.columns:
                # Ensure date column is datetime type
                df["date"] = pd.to_datetime(df["date"])
                date_group = df.groupby(df["date"].dt.date)
                df["heartRate_mean_daily"] = date_group["heartRate"].transform("mean")
                df["heartRate_median_daily"] = date_group["heartRate"].transform("median")
                df["heartRate_min_daily"] = date_group["heartRate"].transform("min")
                df["heartRate_max_daily"] = date_group["heartRate"].transform("max")
                df["heartRate_std_daily"] = date_group["heartRate"].transform("std")
                df["heartRate_count_daily"] = date_group["heartRate"].transform("count")
                df["heartRate_range_daily"] = df["heartRate_max_daily"] - df["heartRate_min_daily"]

                # Add timeOfDay for daily max heartRate
                if "timeOfDay" in df.columns:
                    # Find idx of max heartRate per day
                    idx_max_hr = df.groupby(df["date"].dt.date)["heartRate"].idxmax()
                    # Map date to timeOfDay of max heartRate
                    max_hr_time_map = df.loc[idx_max_hr].set_index(df.loc[idx_max_hr, "date"].dt.date)["timeOfDay"]
                    df["heartRate_max_timeOfDay_daily"] = df["date"].dt.date.map(max_hr_time_map)

        return df

    def activity_summary_table(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process activity summary data.
        Args:
            df (pd.DataFrame): DataFrame containing activity summary data.
        Returns:
            pd.DataFrame: Processed DataFrame with relevant columns.
        """
        # Filter by date first
        df = self._filter_by_date(df, "date")

        # Filter out rows where both calories and step_total are 0
        if "calories" in df.columns and "step_total" in df.columns:
            df = df[~((df["calories"] == 0) & (df["step_total"] == 0))].copy()

            # Calculate overall statistics ignoring 0 values
            calories_nonzero = df.loc[df["calories"] != 0, "calories"]
            step_total_nonzero = df.loc[df["step_total"] != 0, "step_total"]

            df["calories_mean_overall"] = calories_nonzero.mean()
            df["calories_median_overall"] = calories_nonzero.median()
            df["calories_min_overall"] = calories_nonzero.min()
            df["calories_max_overall"] = calories_nonzero.max()
            df["calories_std_overall"] = calories_nonzero.std()

            df["step_total_mean_overall"] = step_total_nonzero.mean()
            df["step_total_median_overall"] = step_total_nonzero.median()
            df["step_total_min_overall"] = step_total_nonzero.min()
            df["step_total_max_overall"] = step_total_nonzero.max()
            df["step_total_std_overall"] = step_total_nonzero.std()

        return df

    def step_series_table(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process step series data.
        Args:
            df (pd.DataFrame): DataFrame containing step series data.
        Returns:
            pd.DataFrame: Processed DataFrame with relevant columns.
        """
        # Filter by date first
        df = self._filter_by_date(df, "date")

        # Check if data is already processed (contains aggregated columns)
        if "step_count_mean_daily" in df.columns:
            # Data is already processed, return as is
            return df

        # filter out rows where step value is 0
        if "value" not in df.columns:
            tqdm.write(
                f"WARNING: Expected 'value' column not found in step series data. Available columns: {df.columns.tolist()}"
            )
            return df

        df = df[df["value"] > 0].copy()

        # Ensure date column is datetime type
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
            # Aggregate statistics per day
            daily = (
                df.groupby(df["date"].dt.date)["value"]
                .agg(
                    step_count_mean_daily="mean",
                    step_count_median_daily="median",
                    step_count_min_daily="min",
                    step_count_max_daily="max",
                    step_count_std_daily="std",
                    step_count_sum_daily="sum",
                    step_count_count_daily="count",
                )
                .reset_index()
                .rename(columns={"date": "date"})
            )
            # Add overall statistics columns
            daily["step_count_mean_overall"] = df["value"].mean()
            daily["step_count_median_overall"] = df["value"].median()
            daily["step_count_min_overall"] = df["value"].min()
            daily["step_count_max_overall"] = df["value"].max()
            daily["step_count_std_overall"] = df["value"].std()
            daily["step_count_sum_overall"] = df["value"].sum()
            daily["step_count_count_overall"] = df["value"].count()

            # value column is not needed in new DataFrame
            df = daily

        return df

    def training_hr_samples_table(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process training heart rate samples data.
        Args:
            df (pd.DataFrame): DataFrame containing training heart rate samples data.
        Returns:
            pd.DataFrame: Processed DataFrame with relevant columns.
        """
        # Filter by date first - need to check dateTime column
        if "dateTime" in df.columns:
            # Create temporary date column for filtering
            df["temp_date"] = pd.to_datetime(df["dateTime"]).dt.date
            df = self._filter_by_date(df, "temp_date")
            df = df.drop("temp_date", axis=1)

        # Check if data is already processed (contains aggregated columns)
        if "heartRate_mean_hourly" in df.columns:
            # Data is already processed, return as is
            return df

        # Filter out rows where heartRate is 0
        if "heartRate" not in df.columns:
            tqdm.write(
                f"WARNING: Expected 'heartRate' column not found in training HR samples data. Available columns: {df.columns.tolist()}"
            )
            return df

        df = df[df["heartRate"] > 0].copy()

        # separate dateTime into date and time columns
        if "dateTime" in df.columns:
            df["date"] = pd.to_datetime(df["dateTime"]).dt.date
            df["hour"] = pd.to_datetime(df["dateTime"]).dt.hour

        # Aggregate into hourly rows if date and hour columns exist
        if "date" in df.columns and "hour" in df.columns:
            # Hourly aggregation
            hourly = (
                df.groupby(["date", "hour"])["heartRate"]
                .agg(
                    heartRate_mean_hourly="mean",
                    heartRate_median_hourly="median",
                    heartRate_min_hourly="min",
                    heartRate_max_hourly="max",
                    heartRate_std_hourly="std",
                    heartRate_count_hourly="count",
                )
                .reset_index()
            )
            # Add overall statistics columns
            hourly["heartRate_mean_overall"] = df["heartRate"].mean()
            hourly["heartRate_median_overall"] = df["heartRate"].median()
            hourly["heartRate_min_overall"] = df["heartRate"].min()
            hourly["heartRate_max_overall"] = df["heartRate"].max()
            hourly["heartRate_std_overall"] = df["heartRate"].std()

            # Add daily statistics columns
            daily_stats = df.groupby("date")["heartRate"].agg(
                heartRate_mean_daily="mean",
                heartRate_median_daily="median",
                heartRate_min_daily="min",
                heartRate_max_daily="max",
                heartRate_std_daily="std",
                heartRate_count_daily="count",
            )
            # Map daily stats to hourly rows
            for col in daily_stats.columns:
                hourly[col] = hourly["date"].map(daily_stats[col])

            df = hourly

        return df

    def training_summary_table(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process training summary data.
        Args:
            df (pd.DataFrame): DataFrame containing training summary data.
        Returns:
            pd.DataFrame: Processed DataFrame with relevant columns.
        """
        # Filter by date first - check for start column
        if "start" in df.columns:
            # Create temporary date column for filtering
            df["temp_date"] = pd.to_datetime(df["start"]).dt.date
            df = self._filter_by_date(df, "temp_date")
            df = df.drop("temp_date", axis=1)

        # Separate start and stop datetime columns to date and time
        if "start" in df.columns:
            df["start_date"] = pd.to_datetime(df["start"]).dt.date
            df["start_time"] = pd.to_datetime(df["start"]).dt.time
        if "stop" in df.columns:
            df["stop_date"] = pd.to_datetime(df["stop"]).dt.date
            df["stop_time"] = pd.to_datetime(df["stop"]).dt.time

        # Add start day name
        if "start_date" in df.columns:
            df["start_day_name"] = pd.to_datetime(df["start_date"]).dt.day_name()

        # Aggregate training summary statistics
        # summary = df.agg(
        #     training_duration_total=("duration", "sum"),
        #     training_count=("duration", "count"),
        #     training_distance_total=("distance", "sum"),
        #     training_calories_total=("calories", "sum"),
        # ).reset_index()

        return df

    def nightly_recovery_breathing_data_table(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process nightly recovery breathing data.
        Args:
            df (pd.DataFrame): DataFrame containing nightly recovery breathing data.
        Returns:
            pd.DataFrame: Processed DataFrame with relevant columns.
        """
        # Filter by date first - check for date or datetime column
        if "date" in df.columns:
            df = self._filter_by_date(df, "date")
        elif "datetime" in df.columns:
            # Create temporary date column for filtering
            df["temp_date"] = pd.to_datetime(df["datetime"]).dt.date
            df = self._filter_by_date(df, "temp_date")
            df = df.drop("temp_date", axis=1)

        # Filter out rows where breathing_rate is 0 or unreasonably low/high
        if "breathing_rate" in df.columns:
            df = df[
                (df["breathing_rate"] > 0) & (df["breathing_rate"] < 50)
            ].copy()  # Reasonable breathing rate range #TODO: Adjust range based on domain knowledge

            if df.empty:
                return df

            # Separate datetime into date and hour columns for aggregation
            if "datetime" in df.columns:
                df["datetime"] = pd.to_datetime(df["datetime"])
                df["date_only"] = df["datetime"].dt.date
                df["hour"] = df["datetime"].dt.hour

            if "date" in df.columns:
                df.rename(columns={"date": "date_of_night"}, inplace=True)

            # Aggregate into hourly rows if date and hour columns exist
            if "date_of_night" in df.columns and "hour" in df.columns:
                # Hourly aggregation per night
                hourly = (
                    df.groupby(["date_of_night", "hour"])["breathing_rate"]
                    .agg(
                        breathing_rate_mean_hourly="mean",
                        breathing_rate_median_hourly="median",
                        breathing_rate_min_hourly="min",
                        breathing_rate_max_hourly="max",
                        breathing_rate_std_hourly="std",
                        breathing_rate_count_hourly="count",
                    )
                    .reset_index()
                )

                # Add overall statistics columns
                hourly["breathing_rate_mean_overall"] = df["breathing_rate"].mean()
                hourly["breathing_rate_median_overall"] = df["breathing_rate"].median()
                hourly["breathing_rate_min_overall"] = df["breathing_rate"].min()
                hourly["breathing_rate_max_overall"] = df["breathing_rate"].max()
                hourly["breathing_rate_std_overall"] = df["breathing_rate"].std()

                # Add daily statistics columns
                daily_stats = df.groupby("date_of_night")["breathing_rate"].agg(
                    breathing_rate_mean_daily="mean",
                    breathing_rate_median_daily="median",
                    breathing_rate_min_daily="min",
                    breathing_rate_max_daily="max",
                    breathing_rate_std_daily="std",
                    breathing_rate_count_daily="count",
                )
                # Map daily stats to hourly rows
                for col in daily_stats.columns:
                    hourly[col] = hourly["date_of_night"].map(daily_stats[col])

                # Add daily range (max - min)
                hourly["breathing_rate_range_daily"] = (
                    hourly["breathing_rate_max_daily"] - hourly["breathing_rate_min_daily"]
                )

                df = hourly
            else:
                # If no datetime column, just add overall statistics
                mean_br = df["breathing_rate"].mean()
                median_br = df["breathing_rate"].median()
                min_br = df["breathing_rate"].min()
                max_br = df["breathing_rate"].max()
                std_br = df["breathing_rate"].std()

                df["breathing_rate_mean_overall"] = mean_br
                df["breathing_rate_median_overall"] = median_br
                df["breathing_rate_min_overall"] = min_br
                df["breathing_rate_max_overall"] = max_br
                df["breathing_rate_std_overall"] = std_br

        return df

    def nightly_recovery_hrv_data_table(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process nightly recovery HRV data.
        Args:
            df (pd.DataFrame): DataFrame containing nightly recovery HRV data.
        Returns:
            pd.DataFrame: Processed DataFrame with relevant columns.
        """
        # Filter by date first - check for date or datetime column
        if "date" in df.columns:
            df = self._filter_by_date(df, "date")
        elif "datetime" in df.columns:
            # Create temporary date column for filtering
            df["temp_date"] = pd.to_datetime(df["datetime"]).dt.date
            df = self._filter_by_date(df, "temp_date")
            df = df.drop("temp_date", axis=1)

        # Filter out rows where hrv_value is 0 or unreasonably low/high
        if "hrv_value" in df.columns:
            df = df[
                (df["hrv_value"] > 0) & (df["hrv_value"] < 200)
            ].copy()  # Reasonable HRV range in milliseconds #TODO: Adjust range based on domain knowledge

            if df.empty:
                return df

            # Separate datetime into date and hour columns for aggregation
            if "datetime" in df.columns:
                df["datetime"] = pd.to_datetime(df["datetime"])
                df["date_only"] = df["datetime"].dt.date
                df["hour"] = df["datetime"].dt.hour

            if "date" in df.columns:
                df.rename(columns={"date": "date_of_night"}, inplace=True)

            # Aggregate into hourly rows if date and hour columns exist
            if "date_of_night" in df.columns and "hour" in df.columns:
                # Hourly aggregation per night
                hourly = (
                    df.groupby(["date_of_night", "hour"])["hrv_value"]
                    .agg(
                        hrv_value_mean_hourly="mean",
                        hrv_value_median_hourly="median",
                        hrv_value_min_hourly="min",
                        hrv_value_max_hourly="max",
                        hrv_value_std_hourly="std",
                        hrv_value_count_hourly="count",
                    )
                    .reset_index()
                )

                # Add overall statistics columns
                hourly["hrv_value_mean_overall"] = df["hrv_value"].mean()
                hourly["hrv_value_median_overall"] = df["hrv_value"].median()
                hourly["hrv_value_min_overall"] = df["hrv_value"].min()
                hourly["hrv_value_max_overall"] = df["hrv_value"].max()
                hourly["hrv_value_std_overall"] = df["hrv_value"].std()

                # Add daily statistics columns
                daily_stats = df.groupby("date_of_night")["hrv_value"].agg(
                    hrv_value_mean_daily="mean",
                    hrv_value_median_daily="median",
                    hrv_value_min_daily="min",
                    hrv_value_max_daily="max",
                    hrv_value_std_daily="std",
                    hrv_value_count_daily="count",
                )
                # Map daily stats to hourly rows
                for col in daily_stats.columns:
                    hourly[col] = hourly["date_of_night"].map(daily_stats[col])

                # Add daily range (max - min)
                hourly["hrv_value_range_daily"] = hourly["hrv_value_max_daily"] - hourly["hrv_value_min_daily"]

                df = hourly
            else:
                # If no datetime column, just add overall statistics
                mean_hrv = df["hrv_value"].mean()
                median_hrv = df["hrv_value"].median()
                min_hrv = df["hrv_value"].min()
                max_hrv = df["hrv_value"].max()
                std_hrv = df["hrv_value"].std()

                df["hrv_value_mean_overall"] = mean_hrv
                df["hrv_value_median_overall"] = median_hrv
                df["hrv_value_min_overall"] = min_hrv
                df["hrv_value_max_overall"] = max_hrv
                df["hrv_value_std_overall"] = std_hrv

        return df

    #################################################
    #              Master File Creation             #
    #################################################

    def create_master_file(self):
        """
        Create a master file combining all processed data at the daily user level.
        This creates a comprehensive dataset where each row represents one user-day
        with aggregated statistics from all available data sources.
        """
        tqdm.write("INFO: Creating master file with combined daily user data...")

        # Dictionary to store dataframes for each data type
        dataframes = {}

        # Get all items from output directory
        items = os.listdir(self.output_dir)
        folders = [item for item in items if os.path.isdir(os.path.join(self.output_dir, item))]

        if not folders:
            tqdm.write("WARNING: No user folders found in output directory. Looking for direct CSV files.")
            folders = ["."]  # Process files in root output directory
        else:
            tqdm.write(f"INFO: Found {len(folders)} user folders: {folders[:5]}...")  # Show first 5

        # Process each user folder
        for folder in tqdm(folders, desc="Processing user data"):
            if folder == ".":
                folder_path = self.output_dir
                user_id = "unknown"
            else:
                folder_path = os.path.join(self.output_dir, folder)
                user_id = folder

            tqdm.write(f"INFO: Processing user {user_id}...")

            # Get all CSV files in the folder
            csv_files = [f for f in os.listdir(folder_path) if f.endswith(".csv")]

            for csv_file in csv_files:
                csv_file_path = os.path.join(folder_path, csv_file)

                try:
                    df = pd.read_csv(csv_file_path)
                    if df.empty:
                        tqdm.write(f"WARNING: Empty file {csv_file} for user {user_id}")
                        continue

                    # Add user_id column if not present
                    if "user_id" not in df.columns:
                        df["user_id"] = user_id

                    # Process different file types for daily aggregation
                    daily_df = self._process_for_master(df, csv_file, user_id)

                    if daily_df is not None and not daily_df.empty:
                        # Store in dataframes dictionary
                        file_type = csv_file.replace(".csv", "")
                        if file_type not in dataframes:
                            dataframes[file_type] = []
                        dataframes[file_type].append(daily_df)

                except Exception as e:
                    tqdm.write(f"ERROR: Failed to process {csv_file} for user {user_id}: {e}")
                    continue

        # Combine all data types
        master_df = self._combine_daily_data(dataframes)

        if master_df is not None and not master_df.empty:
            # Save master file
            master_file_path = os.path.join(self.output_dir, "master_daily_data.csv")
            # if os.path.exists(master_file_path) and not self.overwrite:
            #     tqdm.write(f"WARNING: Master file {master_file_path} already exists. Skipping.")
            #     return

            master_df.to_csv(master_file_path, index=False)
            tqdm.write(f"INFO: Master file created successfully: {master_file_path}")
            tqdm.write(f"INFO: Master file contains {len(master_df)} rows and {len(master_df.columns)} columns")
        else:
            tqdm.write("ERROR: No data to create master file")

    def _process_for_master(self, df: pd.DataFrame, csv_file: str, user_id: str) -> Optional[pd.DataFrame]:
        """
        Process individual file data for master file creation.
        Returns daily aggregated data for each file type.
        """
        # Extract date information and prepare for daily aggregation
        date_col = None

        # Find the appropriate date column
        if "date" in df.columns:
            date_col = "date"
        elif "start_date" in df.columns:
            date_col = "start_date"
        elif "date_of_night" in df.columns:
            date_col = "date_of_night"
        elif "night" in df.columns:
            date_col = "night"
        elif "start" in df.columns:
            # Extract date from datetime
            df["date"] = pd.to_datetime(df["start"]).dt.date
            date_col = "date"

        if date_col is None:
            tqdm.write(f"WARNING: No date column found in {csv_file} for user {user_id}")
            return None

        # Convert date column to datetime if needed
        try:
            df[date_col] = pd.to_datetime(df[date_col]).dt.date
        except:
            pass

        # Process based on file type
        if "activity_summary" in csv_file:
            # Activity summary is already daily
            daily_df = df.copy()
            # Select relevant columns and rename for master
            cols_to_keep = [date_col, "user_id", "calories", "step_total"]
            if "calories_mean_overall" in df.columns:
                cols_to_keep.extend(["calories_mean_overall", "step_total_mean_overall"])
            daily_df = daily_df[cols_to_keep].copy()
            daily_df.rename(
                columns={
                    "calories": "activity_calories_daily",
                    "step_total": "activity_steps_daily",
                    "calories_mean_overall": "activity_calories_mean_overall",
                    "step_total_mean_overall": "activity_steps_mean_overall",
                },
                inplace=True,
            )

        elif "step_series" in csv_file:
            # Step series is already daily aggregated
            daily_df = df.copy()
            daily_df.rename(
                columns={
                    "step_count_sum_daily": "step_series_total_daily",
                    "step_count_mean_daily": "step_series_mean_daily",
                },
                inplace=True,
            )

        elif "sleep_scores" in csv_file:
            # Sleep scores are already daily
            daily_df = df.copy()
            cols_to_keep = [date_col, "user_id", "sleepScore", "continuityScore", "efficiencyScore"]
            if all(col in df.columns for col in cols_to_keep):
                daily_df = daily_df[cols_to_keep].copy()

        elif "training_summary" in csv_file:
            # Aggregate training data by day
            if df.empty:
                return None
            grouped = (
                df.groupby([date_col, "user_id"])
                .agg({"duration_sec": ["sum", "count", "mean"], "calories": ["sum", "mean"], "hr_avg": "mean"})
                .reset_index()
            )
            # Flatten column names
            grouped.columns = [f"{col[0]}_{col[1]}" if col[1] else col[0] for col in grouped.columns]
            daily_df = grouped
            daily_df.rename(
                columns={
                    "duration_sec_sum": "training_duration_total_daily",
                    "duration_sec_count": "training_sessions_daily",
                    "duration_sec_mean": "training_duration_mean_daily",
                    "calories_sum": "training_calories_total_daily",
                    "calories_mean": "training_calories_mean_daily",
                    "hr_avg_mean": "training_hr_avg_daily",
                },
                inplace=True,
            )

        elif "activity_hr" in csv_file or "training_hr_samples" in csv_file:
            # Aggregate heart rate data by day
            if "heartRate_mean_daily" in df.columns:
                # Data is already aggregated daily
                daily_df = (
                    df.groupby([date_col, "user_id"])
                    .agg(
                        {
                            "heartRate_mean_daily": "first",
                            "heartRate_max_daily": "first",
                            "heartRate_min_daily": "first",
                            "heartRate_std_daily": "first",
                        }
                    )
                    .reset_index()
                )
                prefix = "activity_hr" if "activity_hr" in csv_file else "training_hr"
                daily_df.rename(
                    columns={
                        "heartRate_mean_daily": f"{prefix}_mean_daily",
                        "heartRate_max_daily": f"{prefix}_max_daily",
                        "heartRate_min_daily": f"{prefix}_min_daily",
                        "heartRate_std_daily": f"{prefix}_std_daily",
                    },
                    inplace=True,
                )
            else:
                return None

        elif "nightly_recovery" in csv_file:
            # Recovery data - aggregate by night
            if "breathing_rate_mean_daily" in df.columns:
                daily_df = (
                    df.groupby([date_col, "user_id"])
                    .agg({"breathing_rate_mean_daily": "first", "breathing_rate_std_daily": "first"})
                    .reset_index()
                )
            elif "hrv_value_mean_daily" in df.columns:
                daily_df = (
                    df.groupby([date_col, "user_id"])
                    .agg({"hrv_value_mean_daily": "first", "hrv_value_std_daily": "first"})
                    .reset_index()
                )
            else:
                return None

        else:
            # For other file types, return None or basic processing
            tqdm.write(f"INFO: No specific master processing for {csv_file}")
            return None

        # Ensure we have the date column properly named
        if date_col != "date":
            daily_df.rename(columns={date_col: "date"}, inplace=True)

        return daily_df

    def _combine_daily_data(self, dataframes: dict) -> Optional[pd.DataFrame]:
        """
        Combine all daily dataframes into a single master dataframe.
        """
        if not dataframes:
            tqdm.write("ERROR: No dataframes to combine")
            return None

        # Start with the first available dataframe as base
        master_df = None

        for file_type, df_list in dataframes.items():
            if not df_list:
                continue

            # Combine all dataframes of this type
            combined_df = pd.concat(df_list, ignore_index=True)

            if master_df is None:
                master_df = combined_df
            else:
                # Merge on date and user_id
                master_df = pd.merge(
                    master_df, combined_df, on=["date", "user_id"], how="outer", suffixes=("", f"_{file_type}")
                )

        if master_df is not None:
            # Sort by user_id and date
            master_df = master_df.sort_values(["user_id", "date"]).reset_index(drop=True)

            # Convert date back to string for better readability
            master_df["date"] = pd.to_datetime(master_df["date"]).dt.strftime("%Y-%m-%d")

            tqdm.write(
                f"INFO: Combined data for {master_df['user_id'].nunique()} users across {master_df['date'].nunique()} unique dates"
            )

        return master_df

    #################################################
    #                  Run Method                   #
    #################################################

    def run(self):
        """
        Run the filtering process.
        Reads input files, processes them, and saves the output.
        """
        # Get all items from input directory
        items = os.listdir(self.input_dir)

        # Check for folders
        folders = [item for item in items if os.path.isdir(os.path.join(self.input_dir, item))]
        if folders:
            tqdm.write(f"INFO: Found {len(folders)} folders in {self.input_dir}: {folders}")
            tqdm.write(f"INFO: Will process files in each folder.")
            csv_files = []
            for folder in folders:
                folder_path = os.path.join(self.input_dir, folder)
                # Get all CSV files in the folder
                csv_files.extend(
                    [
                        os.path.join(folder, f)
                        for f in os.listdir(folder_path)
                        if f.endswith(".csv") and os.path.isfile(os.path.join(folder_path, f))
                    ]
                )
        else:
            tqdm.write(f"WARNING: No folders found in {self.input_dir}. Processing files directly.")
            # Get all CSV files from input directory
            csv_files = [f for f in items if f.endswith(".csv") and os.path.isfile(os.path.join(self.input_dir, f))]

        if not csv_files:
            tqdm.write(f"ERROR: No CSV files found.")
            raise ValueError("No CSV files found in the input directory.")

        # sort csv_files by name
        csv_files.sort()

        # Process each CSV file
        for csv_file in tqdm(csv_files, desc="Processing CSV files"):

            # Check csv file is named correctly (known format)
            if not re.match(
                r".*(activity_hr|activity_summary|step_series|training_hr_samples|training_summary|hypnogram|nightly_recovery_breathing_data|nightly_recovery_hrv_data|nightly_recovery_summary|sleep_result|sleep_scores|sleep_wake_samples)\.csv$",
                csv_file,
            ):
                tqdm.write(
                    f"ERROR: Invalid CSV file name: {csv_file}. "
                    f"Expected format: activity_hr.csv, activity_summary.csv, step_series.csv, training_hr_samples.csv, training_summary.csv, hypnogram.csv, nightly_recovery_breathing_data.csv, nightly_recovery_hrv_data.csv, nightly_recovery_summary.csv, sleep_result.csv, sleep_scores.csv, or sleep_wake_samples.csv. "
                    f" Skipping this file. "
                )
                continue

            # Read the CSV file
            try:
                csv_file_path = os.path.join(self.input_dir, csv_file)
                df = self.read_csv(csv_file_path)
            except Exception as e:
                tqdm.write(f"ERROR: Failed to read {csv_file}: {e}. Skipping this file.")
                continue

            # Process the data
            tqdm.write(f"INFO: Processing {csv_file}...")
            # check if the dataframe is empty
            # check if the csv_file matches known formats and call the appropriate processing function
            processed_df = df
            if df.empty:
                tqdm.write(f"WARNING: DataFrame is empty for {csv_file}. No processing will be done.")
            elif "activity_hr" in csv_file:
                processed_df = self.activity_hr_table(df)
            elif "activity_summary" in csv_file:
                processed_df = self.activity_summary_table(df)
            elif "step_series" in csv_file:
                processed_df = self.step_series_table(df)
            elif "training_hr_samples" in csv_file:
                processed_df = self.training_hr_samples_table(df)
            elif "training_summary" in csv_file:
                processed_df = self.training_summary_table(df)
            elif "hypnogram" in csv_file:
                tqdm.write(f"INFO: Hypnogram file {csv_file} detected. No processing needed.")
            elif "nightly_recovery_breathing_data" in csv_file:
                processed_df = self.nightly_recovery_breathing_data_table(df)
            elif "nightly_recovery_hrv_data" in csv_file:
                processed_df = self.nightly_recovery_hrv_data_table(df)
            elif "nightly_recovery_summary" in csv_file:
                tqdm.write(f"INFO: Nightly recovery summary file {csv_file} detected. No processing needed.")
            elif "sleep_result" in csv_file:
                tqdm.write(f"INFO: Sleep result file {csv_file} detected. No processing needed.")
            elif "sleep_scores" in csv_file:
                tqdm.write(f"INFO: Sleep scores file {csv_file} detected. No processing needed.")
            elif "sleep_wake_samples" in csv_file:
                tqdm.write(f"INFO: Sleep wake samples file {csv_file} detected. No processing needed.")
            else:
                tqdm.write(f"WARNING: No specific processing function for {csv_file}. Skipping this file.")
                continue

            # Save the processed data
            output_path = os.path.join(self.output_dir, csv_file)
            # check if output subfolder is needed for csv file
            if os.path.dirname(csv_file):
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
            # check if the output file already exists
            if os.path.isfile(output_path):
                tqdm.write(f"WARNING: Output file {output_path} already exists.")
                if self.overwrite:
                    tqdm.write(f"WARNING: Overwriting {output_path}.")
                else:
                    tqdm.write(f"WARNING: Skipping {csv_file}.")
                    continue
            processed_df.to_csv(output_path, index=False)
            tqdm.write(f"INFO: Processed and saved {csv_file} to {output_path}")
