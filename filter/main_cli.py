#!/usr/bin/env python3

import argparse
import re
import os
import pandas as pd
from tqdm.auto import tqdm
from datetime import datetime
from filters import Filter
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """
    Main CLI function for filtering and processing Polar user data with master file creation.

    This function sets up command-line argument parsing for the Polar data filtering tool.
    It processes input files, applies filters, and optionally creates a master file combining all data.

    Supports flexible input folder structures:
    - Input folder containing CSV files directly
    - Input folder containing numbered subdirectories (subject IDs) with JSON files in each

    \b
        input/
        ├── activity_hr.csv
        ├── activity_summary.csv
        ├── step_series.csv
        ├── training_hr_samples.csv
        ├── training_summary.csv
        ├── nightly_recovery_breathing_data.csv
        ├── nightly_recovery_hrv_data.csv
        ├── hypnogram.csv
        ├── sleep_result.csv
        ├── sleep_scores.csv
        └── sleep_wake_samples.csv

    Or with subject subdirectories:

    \b
        input/
        ├── 706293/
        │   ├── activity_hr.json
        │   ├── activity_summary.json
        │   └── ...
        ├── 918902/
        │   ├── activity_hr.json
        │   ├── activity_summary.json
        │   └── ...
        └── ...

    Args:
        Command-line arguments:
        --input-dir: Path to directory containing input files (default: "./input")
        --output-dir: Directory where filtered output will be saved (default: "./output")
        --overwrite: Overwrite existing output files (default: True)
        --master: Create a master file combining all filtered data (default: True)

    Returns:
        None: Filters data and saves individual files plus optional master file
    """
    parser = argparse.ArgumentParser(description="Filter and summarize Polar user data.")
    parser.add_argument(
        "--input-dir", type=str, default="../parser_output", help="Path to directory containing input files"
    )
    parser.add_argument(
        "--output-dir", type=str, default="./filter_output", help="Directory where output will be saved"
    )
    parser.add_argument(
        "--overwrite",
        type=bool,
        default=True,  # TODO: don't overwrite by default
        help="Overwrite existing output files with new ones in output directory",
    )
    parser.add_argument(
        "--master",
        type=bool,
        default=True,
        help="Create a master file with all data combined. If False, only individual files will be created.",
    )

    args = parser.parse_args()

    # do not allow input dir to be the same as output dir to avoid potential data loss
    if os.path.abspath(args.input_dir) == os.path.abspath(args.output_dir):
        logger.error("Input directory cannot be the same as output directory to avoid data loss.")
        raise ValueError("Input directory cannot be the same as output directory to avoid data loss.")

    filter = Filter(input_dir=args.input_dir, output_dir=args.output_dir, overwrite=args.overwrite)
    filter.run()

    if args.master:
        logger.info("Creating master file with all data combined.")
        filter.create_master_file()


if __name__ == "__main__":
    main()
