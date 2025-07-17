import re
import os
import pandas as pd
from tqdm import tqdm
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Filter:
    def __init__(self, input_dir: str, output_dir: str, overwrite: bool = False):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.overwrite = overwrite
        # Ensure directories exist
        try:
            if not os.path.exists(self.input_dir):
                logger.error(f"Input directory does not exist: {self.input_dir}")
            if not os.path.exists(self.output_dir):
                logger.info(f"Creating output directory: {self.output_dir}")
                os.makedirs(self.output_dir)
        except Exception as e:
            logger.error(f"Error creating directories: {e}")
            raise ValueError(f"Invalid directory paths: {e}")

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
            logger.info(f"Successfully read {file_path}")
            return df
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            raise ValueError(f"Could not read CSV file: {e}")

    def activity_hr_table(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process activity heart rate data.
        Args:
            df (pd.DataFrame): DataFrame containing activity heart rate data.
        Returns:
            pd.DataFrame: Processed DataFrame with relevant columns.
        """
        # Filter out rows where heartRate == 0
        if "heartRate" in df.columns:
            df = df[df["heartRate"] != 0]
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
        # Filter out rows where both calories and step_total are 0
        if "calories" in df.columns and "step_total" in df.columns:
            df = df[~((df["calories"] == 0) & (df["step_total"] == 0))]

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
        # filter out rows where step value is 0
        df = df[df["value"] > 0]

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
        # Filter out rows where heartRate is 0
        df = df[df["heartRate"] > 0]

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
            logger.info(f"Found {len(folders)} folders in {self.input_dir}: {folders}")
            logger.info(f"Will process files in each folder.")
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
            logger.warning(f"No folders found in {self.input_dir}. Processing files directly.")
            # Get all CSV files from input directory
            csv_files = [f for f in items if f.endswith(".csv") and os.path.isfile(os.path.join(self.input_dir, f))]

        if not csv_files:
            logger.error(f"No CSV files found.")
            raise ValueError("No CSV files found in the input directory.")

        # sort csv_files by name
        csv_files.sort()

        # Process each CSV file
        for csv_file in tqdm(csv_files, desc="Processing CSV files"):

            # Check csv file is named correctly (known format)
            if not re.match(
                r".*(activity_hr|activity_summary|step_series|training_hr_samples|training_summary)\.csv$", csv_file
            ):
                logger.error(
                    f"Invalid CSV file name: {csv_file}. "
                    f"Expected format: activity_hr.csv, activity_summary.csv, step_series.csv, training_hr_samples.csv, or training_summary.csv. "
                    f" Skipping this file. "
                )
                continue

            # Read the CSV file
            try:
                csv_file_path = os.path.join(self.input_dir, csv_file)
                df = self.read_csv(csv_file_path)
            except Exception as e:
                logger.error(f"Failed to read {csv_file}: {e}. Skipping this file.")
                continue

            # Process the data
            logger.info(f"Processing {csv_file}...")
            # check if the dataframe is empty
            # check if the csv_file matches known formats and call the appropriate processing function
            if df.empty:
                logger.warning(f"DataFrame is empty for {csv_file}. No processing will be done.")
                processed_df = df
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
            else:
                logger.warning(f"No specific processing function for {csv_file}. Skipping this file.")
                continue

            # Save the processed data
            output_path = os.path.join(self.output_dir, csv_file)
            # check if output subfolder is needed for csv file
            if os.path.dirname(csv_file):
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
            # check if the output file already exists
            if os.path.isfile(output_path):
                logger.warning(f"Output file {output_path} already exists.")
                if self.overwrite:
                    logger.warning(f"Overwriting {output_path}.")
                else:
                    logger.warning(f"Skipping {csv_file}.")
                    continue
            processed_df.to_csv(output_path, index=False)
            logger.info(f"Processed and saved {csv_file} to {output_path}")
