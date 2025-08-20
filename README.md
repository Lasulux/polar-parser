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

#### **Detailed overview of the filtering**

##### activity_hr_table

The activity heart rate data contains detailed heart rate measurements taken throughout your daily activities (excluding formal training sessions). This filtering process cleans and organizes this data to make it more useful for analysis.

**What happens to your data:**

1. **Time Formatting**: The system combines separate date and time columns into a single, easy-to-read timestamp that shows exactly when each heart rate measurement was taken.

2. **Date Range Filtering**: Only heart rate data from the specified time period is kept. Data older than January 1, 2020 is automatically removed to ensure data quality.

3. **Training Time Filtering**: Depending on your chosen filter setting:
   - **Training only**: Keeps only heart rate data recorded during your scheduled training sessions
   - **Non-training only**: Keeps only heart rate data from your regular daily activities (excludes training sessions)
   - **All data**: Includes both training and non-training heart rate measurements

4. **Data Quality Cleaning**: Any heart rate readings of zero (which indicate sensor errors or no contact) are removed to ensure accurate statistics.

5. **Statistical Calculations**: The system calculates comprehensive summary statistics:
   - **Overall statistics**: Your average, median, minimum, maximum, and standard deviation of heart rate across all the data
   - **Daily statistics**: The same statistics calculated separately for each day, plus daily heart rate count and range

6. **Data Quality Assessment**: Advanced data coverage indicators are added:
   - **Hours covered per day**: How many different hours of the day have heart rate measurements
   - **Coverage percentage**: What percentage of each day (0-100%) has heart rate data
   - **First and last reading times**: When heart rate monitoring started and ended each day
   - **Daily quality rating**: Automatic classification as "poor" (<50% coverage), "fair" (50-80%), or "good" (>80%)

7. **Enhanced Information**: Additional helpful details are added:
   - **Heart rate range**: Difference between your highest and lowest readings each day
   - **Peak timing**: The exact time when your maximum heart rate occurred each day
   - **Measurement count**: How many heart rate readings were recorded each day

##### activity_summary_table

The activity summary data contains daily totals of your overall physical activity, including calories burned and total steps taken each day. This filtering process ensures you get clean, meaningful daily activity summaries.

**What happens to your data:**

1. **Date Range Filtering**: Only activity data from the specified time period is kept. Data older than January 1, 2020 is automatically removed to ensure data quality.

2. **Training Time Filtering**: Depending on your chosen filter setting:
   - **Training only**: Keeps only activity data recorded during your scheduled training sessions
   - **Non-training only**: Keeps only activity data from your regular daily activities (excludes training sessions)
   - **All data**: Includes both training and non-training activity measurements

3. **Data Quality Cleaning**: Days where both calories burned and total steps are zero (indicating no meaningful activity or device not worn) are removed to ensure accurate statistics.

4. **Statistical Calculations**: The system calculates comprehensive summary statistics for both calories and steps, excluding zero values:
   - **Overall calorie statistics**: Your average, median, minimum, maximum, and standard deviation of daily calories burned across all the data
   - **Overall step statistics**: Your average, median, minimum, maximum, and standard deviation of daily steps taken across all the data

##### step_series_table

The step series data contains detailed step counts recorded throughout the day in regular intervals (usually every few minutes). This filtering process transforms this high-frequency data into meaningful daily summaries.

**What happens to your data:**

1. **Time Validation**: Any records with missing or invalid time stamps are removed to ensure data integrity.

2. **Time Formatting**: The system combines separate date and time columns into a single timestamp for accurate chronological ordering.

3. **Date Range Filtering**: Only step data from the specified time period is kept. Data older than January 1, 2020 is automatically removed to ensure data quality.

4. **Training Time Filtering**: Depending on your chosen filter setting:
   - **Training only**: Keeps only step data recorded during your scheduled training sessions
   - **Non-training only**: Keeps only step data from your regular daily activities (excludes training sessions)
   - **All data**: Includes both training and non-training step measurements

5. **Data Quality Cleaning**: Any step counts of zero (indicating no movement or sensor inactivity) are removed to focus on actual activity periods.

6. **Daily Aggregation**: The detailed step measurements are summarized into meaningful daily statistics:
   - **Daily step statistics**: Average, median, minimum, maximum, standard deviation, total steps, and count of measurements per day
   - **Overall step statistics**: The same comprehensive statistics calculated across all your data for comparison

##### training_hr_samples_table

The training heart rate samples contain detailed heart rate measurements recorded during your formal training sessions. This filtering process organizes this data into hourly summaries while preserving both session-level and daily patterns.

**What happens to your data:**

1. **Date Range Filtering**: Only training heart rate data from the specified time period is kept. Data older than January 1, 2020 is automatically removed to ensure data quality.

2. **Training Time Filtering**: Depending on your chosen filter setting:
   - **Training only**: Keeps only heart rate data from your scheduled training sessions
   - **Non-training only**: Keeps only heart rate data from non-training periods (though this is rare for this data type)
   - **All data**: Includes all training heart rate measurements

3. **Data Quality Cleaning**: Any heart rate readings of zero (indicating sensor errors or no contact) are removed to ensure accurate statistics.

4. **Time Organization**: The system separates date and hour information for structured analysis.

5. **Hourly Aggregation**: Heart rate data is summarized into hourly blocks for detailed pattern analysis:
   - **Hourly statistics**: Average, median, minimum, maximum, standard deviation, and count of heart rate measurements for each hour
   - **Daily statistics**: The same comprehensive statistics calculated for each complete training day
   - **Overall statistics**: Summary statistics across all your training sessions for comparison

##### training_summary_table

The training summary data contains high-level information about each of your training sessions, including start/stop times, duration, and performance metrics. This filtering process organizes and enhances this session information.

**What happens to your data:**

1. **Date Range Filtering**: Only training sessions from the specified time period are kept. Sessions older than January 1, 2020 are automatically removed to ensure data quality.

2. **Training Time Filtering**: Depending on your chosen filter setting:
   - **Training only**: Keeps all training session data (this is the default for this data type)
   - **Non-training only**: Would exclude training sessions (rarely used for this data type)
   - **All data**: Includes all training session information

3. **Time Structure Enhancement**: Training start and stop times are separated into:
   - **Start date and time**: When each training session began
   - **Stop date and time**: When each training session ended
   - **Day of week**: What day of the week each training session occurred

##### nightly_recovery_breathing_data_table

The nightly recovery breathing data contains detailed breathing rate measurements recorded during your sleep. This filtering process transforms continuous breathing monitoring into meaningful nightly and hourly summaries.

**What happens to your data:**

1. **Date Range Filtering**: Only breathing data from the specified time period is kept. Data older than January 1, 2020 is automatically removed to ensure data quality.

2. **Training Time Filtering**: Depending on your chosen filter setting:
   - **Training only**: Keeps only breathing data from nights around training days
   - **Non-training only**: Keeps only breathing data from recovery nights (non-training days)
   - **All data**: Includes breathing data from all nights

3. **Data Quality Cleaning**: Breathing rate measurements are filtered to keep only realistic values (between 0 and 50 breaths per minute) to remove sensor errors or anomalous readings.

4. **Time Organization**: The system organizes data by night and hour for structured sleep analysis.

5. **Hourly and Nightly Aggregation**: Breathing data is summarized at multiple time scales for comprehensive sleep analysis:
   - **Hourly statistics**: Average, median, minimum, maximum, standard deviation, and count of breathing rate for each hour of sleep
   - **Nightly statistics**: The same comprehensive statistics calculated for each complete night
   - **Overall statistics**: Summary statistics across all your nights for comparison
   - **Nightly breathing range**: The difference between your highest and lowest breathing rates each night

##### nightly_recovery_hrv_data_table

The nightly recovery heart rate variability (HRV) data contains detailed measurements of the variation in time between your heartbeats during sleep. This filtering process organizes this important recovery metric into meaningful summaries.

**What happens to your data:**

1. **Date Range Filtering**: Only HRV data from the specified time period is kept. Data older than January 1, 2020 is automatically removed to ensure data quality.

2. **Training Time Filtering**: Depending on your chosen filter setting:
   - **Training only**: Keeps only HRV data from nights around training days
   - **Non-training only**: Keeps only HRV data from recovery nights (non-training days)
   - **All data**: Includes HRV data from all nights

3. **Data Quality Cleaning**: HRV measurements are filtered to keep only realistic values (between 0 and 200 milliseconds) to remove sensor errors or anomalous readings.

4. **Time Organization**: The system organizes data by night and hour for structured recovery analysis.

5. **Hourly and Nightly Aggregation**: HRV data is summarized at multiple time scales for comprehensive recovery analysis:
   - **Hourly statistics**: Average, median, minimum, maximum, standard deviation, and count of HRV for each hour of sleep
   - **Nightly statistics**: The same comprehensive statistics calculated for each complete night
   - **Overall statistics**: Summary statistics across all your nights for comparison
   - **Nightly HRV range**: The difference between your highest and lowest HRV readings each night

---

## **New Fields Added by Filtering**

The filtering process adds comprehensive statistical and quality assessment fields to each data type. Here's a complete reference of the new fields:

### **Activity Heart Rate Data (`activity_hr_table`)**

**Overall Statistics (across all data):**
- `heartRate_mean_overall`: Average heart rate across all measurements
- `heartRate_median_overall`: Median heart rate across all measurements  
- `heartRate_min_overall`: Minimum heart rate recorded
- `heartRate_max_overall`: Maximum heart rate recorded
- `heartRate_std_overall`: Standard deviation of heart rate measurements

**Daily Statistics (calculated per day):**
- `heartRate_mean_daily`: Average heart rate for each day
- `heartRate_median_daily`: Median heart rate for each day
- `heartRate_min_daily`: Minimum heart rate for each day
- `heartRate_max_daily`: Maximum heart rate for each day
- `heartRate_std_daily`: Standard deviation of heart rate for each day
- `heartRate_count_daily`: Number of heart rate measurements per day
- `heartRate_range_daily`: Daily heart rate range (max - min)

**Data Quality Indicators:**
- `heartRate_hours_covered_daily`: Number of hours with data per day (0-24)
- `heartRate_first_reading_hour_daily`: Hour when first reading occurred each day
- `heartRate_last_reading_hour_daily`: Hour when last reading occurred each day
- `heartRate_coverage_percentage_daily`: Percentage of day covered by data (0-100%)
- `heartRate_daily_quality`: Quality rating ("poor", "fair", "good") based on coverage
- `heartRate_max_timeOfDay_daily`: Exact time when maximum heart rate occurred each day

### **Activity Summary Data (`activity_summary_table`)**

**Overall Statistics:**
- `calories_mean_overall`: Average daily calories across all data
- `calories_median_overall`: Median daily calories across all data
- `calories_min_overall`: Minimum daily calories recorded
- `calories_max_overall`: Maximum daily calories recorded
- `calories_std_overall`: Standard deviation of daily calories
- `step_total_mean_overall`: Average daily steps across all data
- `step_total_median_overall`: Median daily steps across all data
- `step_total_min_overall`: Minimum daily steps recorded
- `step_total_max_overall`: Maximum daily steps recorded
- `step_total_std_overall`: Standard deviation of daily steps

### **Step Series Data (`step_series_table`)**

**Daily Statistics (aggregated from step measurements):**
- `step_count_mean_daily`: Average step count per measurement for each day
- `step_count_median_daily`: Median step count per measurement for each day
- `step_count_min_daily`: Minimum step count measurement for each day
- `step_count_max_daily`: Maximum step count measurement for each day
- `step_count_std_daily`: Standard deviation of step measurements for each day
- `step_count_sum_daily`: Total steps for each day
- `step_count_count_daily`: Number of step measurements per day

**Overall Statistics:**
- `step_count_mean_overall`: Average step count across all measurements
- `step_count_median_overall`: Median step count across all measurements
- `step_count_min_overall`: Minimum step count measurement
- `step_count_max_overall`: Maximum step count measurement
- `step_count_std_overall`: Standard deviation of all step measurements
- `step_count_sum_overall`: Total steps across all data
- `step_count_count_overall`: Total number of step measurements

### **Training Heart Rate Samples (`training_hr_samples_table`)**

**Hourly Statistics (data aggregated by hour):**
- `heartRate_mean_hourly`: Average heart rate for each hour
- `heartRate_median_hourly`: Median heart rate for each hour
- `heartRate_min_hourly`: Minimum heart rate for each hour
- `heartRate_max_hourly`: Maximum heart rate for each hour
- `heartRate_std_hourly`: Standard deviation of heart rate for each hour
- `heartRate_count_hourly`: Number of measurements per hour

**Daily Statistics:**
- `heartRate_mean_daily`: Average heart rate for each training day
- `heartRate_median_daily`: Median heart rate for each training day
- `heartRate_min_daily`: Minimum heart rate for each training day
- `heartRate_max_daily`: Maximum heart rate for each training day
- `heartRate_std_daily`: Standard deviation of heart rate for each training day
- `heartRate_count_daily`: Number of measurements per training day

**Overall Statistics:**
- `heartRate_mean_overall`: Average heart rate across all training sessions
- `heartRate_median_overall`: Median heart rate across all training sessions
- `heartRate_min_overall`: Minimum heart rate across all training sessions
- `heartRate_max_overall`: Maximum heart rate across all training sessions
- `heartRate_std_overall`: Standard deviation across all training sessions

### **Training Summary Data (`training_summary_table`)**

**Enhanced Time Information:**
- `start_date`: Training session start date
- `start_time`: Training session start time
- `stop_date`: Training session stop date
- `stop_time`: Training session stop time
- `start_day_name`: Day of the week for training session start

### **Nightly Recovery Breathing Data (`nightly_recovery_breathing_data_table`)**

**Hourly Statistics (per night and hour):**
- `breathing_rate_mean_hourly`: Average breathing rate for each hour
- `breathing_rate_median_hourly`: Median breathing rate for each hour
- `breathing_rate_min_hourly`: Minimum breathing rate for each hour
- `breathing_rate_max_hourly`: Maximum breathing rate for each hour
- `breathing_rate_std_hourly`: Standard deviation of breathing rate for each hour
- `breathing_rate_count_hourly`: Number of measurements per hour

**Nightly Statistics:**
- `breathing_rate_mean_daily`: Average breathing rate for each night
- `breathing_rate_median_daily`: Median breathing rate for each night
- `breathing_rate_min_daily`: Minimum breathing rate for each night
- `breathing_rate_max_daily`: Maximum breathing rate for each night
- `breathing_rate_std_daily`: Standard deviation of breathing rate for each night
- `breathing_rate_count_daily`: Number of measurements per night
- `breathing_rate_range_daily`: Breathing rate range for each night (max - min)

**Overall Statistics:**
- `breathing_rate_mean_overall`: Average breathing rate across all nights
- `breathing_rate_median_overall`: Median breathing rate across all nights
- `breathing_rate_min_overall`: Minimum breathing rate across all nights
- `breathing_rate_max_overall`: Maximum breathing rate across all nights
- `breathing_rate_std_overall`: Standard deviation across all nights

### **Nightly Recovery HRV Data (`nightly_recovery_hrv_data_table`)**

**Hourly Statistics (per night and hour):**
- `hrv_value_mean_hourly`: Average HRV for each hour
- `hrv_value_median_hourly`: Median HRV for each hour
- `hrv_value_min_hourly`: Minimum HRV for each hour
- `hrv_value_max_hourly`: Maximum HRV for each hour
- `hrv_value_std_hourly`: Standard deviation of HRV for each hour
- `hrv_value_count_hourly`: Number of measurements per hour

**Nightly Statistics:**
- `hrv_value_mean_daily`: Average HRV for each night
- `hrv_value_median_daily`: Median HRV for each night
- `hrv_value_min_daily`: Minimum HRV for each night
- `hrv_value_max_daily`: Maximum HRV for each night
- `hrv_value_std_daily`: Standard deviation of HRV for each night
- `hrv_value_count_daily`: Number of measurements per night
- `hrv_value_range_daily`: HRV range for each night (max - min)

**Overall Statistics:**
- `hrv_value_mean_overall`: Average HRV across all nights
- `hrv_value_median_overall`: Median HRV across all nights
- `hrv_value_min_overall`: Minimum HRV across all nights
- `hrv_value_max_overall`: Maximum HRV across all nights
- `hrv_value_std_overall`: Standard deviation across all nights

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

