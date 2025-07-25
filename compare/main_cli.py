#!/usr/bin/env python3

import argparse
import re
import os
import pandas as pd
from tqdm.auto import tqdm
from datetime import datetime
from compare_logic import Comparer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """
    Main CLI function for comparing groups of Polar user data by specified date ranges.
    This function sets up command-line argument parsing for the Polar data comparison tool.
    It uses filtered data files created by the filter functions as input
    for comparing different groups.

    Expected input structure with filtered master file:

    \b
        input/
        ├── master_file.csv  # Created by filter functions
        └── watch_groups_dance_dttm.csv # manually created file with groups and dance lesson dates, notes etc.

    Args:
        Command-line arguments:
        --input-dir: Path to directory containing group folders with filtered master files (default: "./input")
        --output-dir: Directory where comparison results will be saved (default: "./output")
        --overwrite: Overwrite existing output files (default: True)

    Returns:
        None: Processes and compares group data from filtered master files and saves comparison output files
    """
    parser = argparse.ArgumentParser(description="Filter and summarize Polar user data.")
    parser.add_argument(
        "--input-dir", type=str, default="./filter_output", help="Path to directory containing input files"
    )
    parser.add_argument(
        "--output-dir", type=str, default="./compare_output", help="Directory where output will be saved"
    )
    parser.add_argument(
        "--overwrite",
        type=bool,
        default=True,  # TODO: don't overwrite by default
        help="Overwrite existing output files with new ones in output directory",
    )

    args = parser.parse_args()

    # do not allow input dir to be the same as output dir to avoid potential data loss
    if os.path.abspath(args.input_dir) == os.path.abspath(args.output_dir):
        logger.error("Input directory cannot be the same as output directory to avoid data loss.")
        raise ValueError("Input directory cannot be the same as output directory to avoid data loss.")

    comparer = Comparer(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        overwrite=args.overwrite,
    )
    comparer.compare_groups()


if __name__ == "__main__":
    main()
