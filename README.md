# Polar Data Parser CLI

This project provides a command-line interface (CLI) for processing, filtering, and comparing Polar user data from `.zip` files. The CLI extracts training sessions, activities, heart rate data, and sleep data, processes and filters the data, and enables comparison between different groups or time periods.

---

## **Features**
- **Parsing**: Parses `.zip` files containing Polar user data and extracts training sessions, activities, heart rate data, and sleep data.
- **Filtering**: Filters and processes parsed data with options for training-only, non-training, or all data.
- **Comparing**: Compares different groups of filtered data across specified date ranges.
- **Multiple Output Formats**: Saves processed data in CSV, Excel, or both formats.
- **Date Range Filtering**: Allows filtering data by date range.
- **Master File Generation**: Creates combined master files from individual user data.

---

## **Requirements**
- Python 3.8 or higher
- Required Python libraries:
  - `pandas`
  - `tqdm`
  - `openpyxl`
  - `isodate`

Install the dependencies using:
```bash
pip install -r requirements.txt
```

---

## **Usage**

### **Run the CLI**
To run the CLI, use the following command:
```bash
python main_cli.py [OPTIONS]
```

### **Options**
| Option           | Type   | Default           | Description                                                                 |
|-------------------|--------|-------------------|-----------------------------------------------------------------------------|
| `--input-dir`     | `str`  | `../input`        | Path to the directory containing `.zip` files.                              |
| `--output-dir`    | `str`  | `../output`       | Path to the directory where output files will be saved.                     |
| `--start-date`    | `str`  | `None`            | Start date for processing data (format: `YYYY-MM-DD`).                      |
| `--end-date`      | `str`  | Current date      | End date for processing data (format: `YYYY-MM-DD`).                        |
| `--save-format`   | `str`  | `csv`             | Format for saving data: `csv`, `excel`, `both`, or `none`.                  |

---

### **Examples**

#### **1. Process All Data with Default Settings**
```bash
python main_cli.py
```
- Input directory: `../input`
- Output directory: `../output`
- Saves data in CSV format.

#### **2. Specify Input and Output Directories**
```bash
python main_cli.py --input-dir "m:/TTK/input" --output-dir "m:/TTK/output"
```

#### **3. Process Data for a Specific Date Range**
```bash
python main_cli.py --start-date "2025-01-01" --end-date "2025-03-31"
```

#### **4. Save Data in Both CSV and Excel Formats**
```bash
python main_cli.py --save-format "both"
```

#### **5. Skip Saving Data**
```bash
python main_cli.py --save-format "none"
```

#### **6. Run from venv with custom directories, when in main working directory**
```bash
.venv/bin/python ./parser/main_cli.py --input-dir "./raw/zip" --output-dir "./parser_output"
```

---

## **Output**
- Processed data is saved in the specified output directory.
- Each user's data is saved in a separate folder, named based on their user ID.
- Files include:
  - `training_summary.csv` or `.xlsx`
  - `training_hr_samples.csv` or `.xlsx`
  - `activity_summary.csv` or `.xlsx`
  - `step_series.csv` or `.xlsx`
  - `activity_hr.csv` or `.xlsx`
  - `sleep_wake_samples.csv` or `.xlsx`
  - `sleep_scores.csv` or `.xlsx`
  - `sleep_result.csv` or `.xlsx`
  - `hypnogram.csv` or `.xlsx`
  - `nightly_recovery_hrv_data.csv` or `.xlsx`
  - `nightly_recovery_breathing_data.csv` or `.xlsx`
  - `nightly_recovery_summary.csv` or `.xlsx`

---

---

## **Additional Processing Tools**

### **Data Filtering**

After parsing the raw Polar data, you can filter and process the data using the filtering tool located in the `filter/` directory.

#### **Run the Filter CLI**
```bash
python filter/main_cli.py [OPTIONS]
```

#### **Filter Options**
| Option                      | Type   | Default                  | Description                                                                 |
|-----------------------------|--------|--------------------------|-----------------------------------------------------------------------------|
| `--input-dir`               | `str`  | `./parser_output`        | Path to directory containing parsed data files.                             |
| `--output-dir`              | `str`  | `./filter_output/training` | Directory where filtered output will be saved.                           |
| `--overwrite`               | `bool` | `True`                   | Overwrite existing output files with new ones.                             |
| `--master`                  | `bool` | `True`                   | Create a master file combining all filtered data.                          |
| `--filter-by-training`      | `str`  | `training_only`          | Filter data by training times: `training_only`, `non_training_only`, `all`. |
| `--convert-training-to-days` | `bool` | `True`                   | Convert training times to days for daily summaries.                        |

#### **Filter Examples**

**1. Filter All Data with Default Settings**
```bash
python filter/main_cli.py
```

**2. Filter Only Non-Training Data**
```bash
python filter/main_cli.py --filter-by-training "non_training_only" --output-dir "./filter_output/non_training"
```

**3. Include All Data (Training and Non-Training)**
```bash
python filter/main_cli.py --filter-by-training "all" --output-dir "./filter_output/all"
```

---

### **Data Comparison**

The comparison tool allows you to compare different groups of filtered data, located in the `compare/` directory.

#### **Run the Compare CLI**
```bash
python compare/main_cli.py [OPTIONS]
```

#### **Compare Options**
| Option           | Type   | Default              | Description                                                                 |
|------------------|--------|----------------------|-----------------------------------------------------------------------------|
| `--input-dir`    | `str`  | `./filter_output`    | Path to directory containing filtered master files.                        |
| `--output-dir`   | `str`  | `./compare_output`   | Directory where comparison results will be saved.                          |
| `--overwrite`    | `bool` | `True`               | Overwrite existing output files with new ones.                             |

#### **Compare Examples**

**1. Compare Groups with Default Settings**
```bash
python compare/main_cli.py
```

**2. Specify Custom Input and Output Directories**
```bash
python compare/main_cli.py --input-dir "./filter_output" --output-dir "./custom_compare_output"
```

---

## **Workflow**

The typical workflow for processing Polar data involves three steps:

1. **Parse**: Extract data from `.zip` files using `parser/main_cli.py`
2. **Filter**: Process and filter the parsed data using `filter/main_cli.py`
3. **Compare**: Compare different groups of filtered data using `compare/main_cli.py`

**Complete Example Workflow:**
```bash
# Step 1: Parse raw zip files
python parser/main_cli.py --input-dir "./raw/zip" --output-dir "./parser_output"

# Step 2: Filter training data
python filter/main_cli.py --input-dir "./parser_output" --output-dir "./filter_output/training" --filter-by-training "training_only"

# Step 3: Filter non-training data
python filter/main_cli.py --input-dir "./parser_output" --output-dir "./filter_output/non_training" --filter-by-training "non_training_only"

# Step 4: Filter all data
python filter/main_cli.py --input-dir "./parser_output" --output-dir "./filter_output/all" --filter-by-training "all"

# Step 5: Compare filtered groups
python compare/main_cli.py --input-dir "./filter_output" --output-dir "./compare_output"
```

---

## **Error Handling**
- If the input directory does not exist, the script will raise an error.
- If invalid date formats are provided, the script will display an error message and exit.
- Input and output directories cannot be the same to avoid data loss.

---

## **License**
This project is licensed under the MIT License.
