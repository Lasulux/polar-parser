# Polar Data Parser CLI

This project provides a command-line interface (CLI) for processing and exporting Polar user data from `.zip` files. The CLI extracts training sessions, activities, and heart rate data, and saves the processed data in CSV or Excel formats.

---

## **Features**
- Parses `.zip` files containing Polar user data.
- Extracts training session summaries, activity summaries, and heart rate samples.
- Saves processed data in CSV, Excel, or both formats.
- Allows filtering data by date range.

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

---

## **Error Handling**
- If the input directory does not exist, the script will raise an error.
- If invalid date formats are provided, the script will display an error message and exit.
---

## **License**
This project is licensed under the MIT License.
