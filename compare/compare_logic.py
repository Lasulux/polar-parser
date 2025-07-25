import re
import os
import pandas as pd
from tqdm.auto import tqdm
from typing import Optional


class Comparer:
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

    def compare_groups(self):
        """
        Compare groups of Polar user data by specified date ranges.
        This function reads filtered master files and compares data across different groups.
        It saves the comparison results in the specified output directory.
        """
        try:
            # Load master file - try both possible names
            master_file_names = ["master_file.csv", "master_daily_data.csv"]
            master_df = None
            master_file_path = None

            for filename in master_file_names:
                potential_path = os.path.join(self.input_dir, filename)
                if os.path.exists(potential_path):
                    master_file_path = potential_path
                    break

            if master_file_path is None:
                tqdm.write(f"ERROR: No master file found. Looked for: {master_file_names}")
                return

            master_df = pd.read_csv(master_file_path)
            master_df["date"] = pd.to_datetime(master_df["date"], errors="coerce")
            master_df = master_df[master_df["date"] >= self.MIN_DATE]

            if master_df.empty:
                tqdm.write("No data available after applying date filter.")
                return

            # if group column does not exist look for grouping file
            if "group" not in master_df.columns:
                group_file_path = os.path.join(self.input_dir, "watch_groups_dance_dttm.csv")
                if not os.path.exists(group_file_path):
                    group_file_path = os.path.join("../input", "watch_groups_dance_dttm.csv")
                    if not os.path.exists(group_file_path):
                        group_file_path = os.path.join("./input", "watch_groups_dance_dttm.csv")
                        if not os.path.exists(group_file_path):
                            tqdm.write(f"ERROR: Group file does not exist: {group_file_path}")
                            return
                group_df = pd.read_csv(group_file_path)

                # add group column to master_df
                if "group" in group_df.columns:
                    master_df["group"] = master_df["user_id"].map(group_df.set_index("user_id")["group"])
            # Group by 'group' column and perform comparisons
            grouped = master_df.groupby("group")
            for group_name, group_data in grouped:
                self._process_group(str(group_name), group_data)

        except Exception as e:
            tqdm.write(f"ERROR: An error occurred during comparison: {e}")

    def _process_group(self, group_name: str, group_data: pd.DataFrame):
        """
        Process and compare data for a specific group.
        This function can be extended to perform various comparisons and analyses.

        Args:
            group_name (str): Name of the group being processed.
            group_data (pd.DataFrame): DataFrame containing data for the group.
        """
        try:
            # Define columns to summarize (excluding date, user_id, group)
            exclude_cols = {"date", "user_id", "group"}
            summary_cols = [col for col in group_data.columns if col not in exclude_cols]

            # Initialize summary statistics dictionary
            summary_stats = {}

            # Basic group information
            summary_stats["group_name"] = [group_name]
            summary_stats["total_records"] = [len(group_data)]
            summary_stats["unique_users"] = [group_data["user_id"].nunique()]
            summary_stats["date_range_start"] = [
                group_data["date"].min().strftime("%Y-%m-%d") if group_data["date"].notna().any() else "N/A"
            ]
            summary_stats["date_range_end"] = [
                group_data["date"].max().strftime("%Y-%m-%d") if group_data["date"].notna().any() else "N/A"
            ]
            summary_stats["total_days"] = [
                (group_data["date"].max() - group_data["date"].min()).days if group_data["date"].notna().any() else 0
            ]

            # Calculate comprehensive statistics for each numeric column
            for col in summary_cols:
                if col in group_data.columns:
                    # Convert to numeric, coercing errors to NaN
                    numeric_data = pd.to_numeric(group_data[col], errors="coerce")

                    # Basic statistics
                    summary_stats[f"{col}_count"] = [numeric_data.count()]
                    summary_stats[f"{col}_missing"] = [numeric_data.isna().sum()]
                    summary_stats[f"{col}_missing_pct"] = [
                        round((numeric_data.isna().sum() / len(numeric_data)) * 100, 2)
                    ]

                    if numeric_data.count() > 0:  # Only calculate if we have valid data
                        summary_stats[f"{col}_mean"] = [round(numeric_data.mean(), 4)]
                        summary_stats[f"{col}_median"] = [round(numeric_data.median(), 4)]
                        summary_stats[f"{col}_std"] = [round(numeric_data.std(), 4)]
                        summary_stats[f"{col}_min"] = [round(numeric_data.min(), 4)]
                        summary_stats[f"{col}_max"] = [round(numeric_data.max(), 4)]
                        summary_stats[f"{col}_q25"] = [round(numeric_data.quantile(0.25), 4)]
                        summary_stats[f"{col}_q75"] = [round(numeric_data.quantile(0.75), 4)]
                        summary_stats[f"{col}_sum"] = [round(numeric_data.sum(), 4)]
                    else:
                        # Fill with NaN if no valid data
                        for stat in ["mean", "median", "std", "min", "max", "q25", "q75", "sum"]:
                            summary_stats[f"{col}_{stat}"] = [None]

            # Create summary DataFrame
            summary_df = pd.DataFrame(summary_stats)

            # Log key statistics
            total_records = summary_stats["total_records"][0]
            unique_users = summary_stats["unique_users"][0]
            tqdm.write(f"Group: {group_name}, Records: {total_records}, Users: {unique_users}")

            # Log some key health metrics if available
            if (
                "activity_hr_mean_daily_mean" in summary_stats
                and summary_stats["activity_hr_mean_daily_mean"][0] is not None
            ):
                avg_hr = summary_stats["activity_hr_mean_daily_mean"][0]
                tqdm.write(f"  Average Daily HR: {avg_hr:.2f}")

            if (
                "activity_steps_daily_mean" in summary_stats
                and summary_stats["activity_steps_daily_mean"][0] is not None
            ):
                avg_steps = summary_stats["activity_steps_daily_mean"][0]
                tqdm.write(f"  Average Daily Steps: {avg_steps:.0f}")

            if "sleepScore_mean" in summary_stats and summary_stats["sleepScore_mean"][0] is not None:
                avg_sleep_score = summary_stats["sleepScore_mean"][0]
                tqdm.write(f"  Average Sleep Score: {avg_sleep_score:.2f}")

            # Save summary statistics to output directory
            summary_file = os.path.join(self.output_dir, f"group_{group_name}_summary.csv")
            summary_df.to_csv(summary_file, index=False)
            tqdm.write(f"Summary statistics saved to: {summary_file}")

            # Also save the raw group data
            raw_data_file = os.path.join(self.output_dir, f"group_{group_name}_raw_data.csv")
            group_data.to_csv(raw_data_file, index=False)
            tqdm.write(f"Raw data saved to: {raw_data_file}")

        except Exception as e:
            tqdm.write(f"ERROR: An error occurred while processing group {group_name}: {e}")
            # Create a minimal error summary if processing fails completely
            try:
                error_summary = pd.DataFrame(
                    {
                        "group_name": [group_name],
                        "error": [str(e)],
                        "total_records": [len(group_data) if group_data is not None else 0],
                    }
                )
                error_file = os.path.join(self.output_dir, f"group_{group_name}_error.csv")
                error_summary.to_csv(error_file, index=False)
                tqdm.write(f"Error summary saved to: {error_file}")
            except Exception as nested_e:
                tqdm.write(f"ERROR: Failed to save error summary: {nested_e}")
