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
    Main CLI function for processing and exporting Polar user data.
    This function sets up command-line argument parsing for the Polar data processing tool.
    It supports flexible input folder structures:
    - Input folder containing input files directly

    \b
        input/
        ├── activity_hr.csv
        ├── activity_summary.csv
        ├── step_series.csv
        ├── training_hr_samples.csv
        └── training_summary.csv

    - Input folder containing numbered subdirectories (subject IDs) with input files in each

    \b
        input/
        ├── 706293/
        │   ├── activity_hr.json
        │   ├── activity_summary.json
        │   ├── step_series.json
        │   ├── training_hr_samples.json
        │   └── training_summary.json
        ├── 918902/
        │   ├── activity_hr.json
        │   ├── activity_summary.json
        │   ├── step_series.json
        │   ├── training_hr_samples.json
        │   └── training_summary.json
        └── ...

    Args:
        Command-line arguments:
        --input-dir: Path to directory containing input files (default: "../input")
        --output-dir: Directory where output will be saved (default: "../output")
        --start-date: Date to start processing data from (YYYY-MM-DD format, optional)
        --end-date: Date to end processing data (YYYY-MM-DD format, default: current date)
        --save-format: Output format - csv, excel, both, or none (default: csv)
    Returns:
        None: Processes data according to specified parameters and saves output files
    """
    parser = argparse.ArgumentParser(description="Filter and summarize Polar user data.")
    parser.add_argument("--input-dir", type=str, default="./input", help="Path to directory containing input files")
    parser.add_argument("--output-dir", type=str, default="./output", help="Directory where output will be saved")
    parser.add_argument(
        "--overwrite",
        type=bool,
        default=True,  # TODO: don't overwrite by default
        help="Overwrite existing output files with new ones in output directory",
    )
    # parser.add_argument(
    #     "--start-date",
    #     type=str,
    #     default=None,
    #     help="Date to start processing data from (YYYY-MM-DD). If not provided, all data will be processed.",
    # )
    # parser.add_argument(
    #     "--end-date",
    #     type=str,
    #     default=datetime.now().strftime("%Y-%m-%d"),
    #     help="Date to end processing data (YYYY-MM-DD)",
    # )
    # parser.add_argument(
    #     "--save-format",
    #     type=str,
    #     choices=["csv", "excel", "both", "none"],
    #     default="csv",
    #     help="Save format for the data: csv, excel, both or none",
    # )

    args = parser.parse_args()

    # do not allow input dir to be the same as output dir to avoid potential data loss
    if os.path.abspath(args.input_dir) == os.path.abspath(args.output_dir):
        logger.error("Input directory cannot be the same as output directory to avoid data loss.")
        raise ValueError("Input directory cannot be the same as output directory to avoid data loss.")

    filter = Filter(input_dir=args.input_dir, output_dir=args.output_dir, overwrite=args.overwrite)
    filter.run()


if __name__ == "__main__":
    main()
