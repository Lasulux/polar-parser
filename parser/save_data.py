import os


def save_data_files(folder_name: str, data_dict: dict, output_dir: str, save_format: str):
    """
    Saves multiple pandas DataFrames to files (Excel, CSV, or both) in the specified folder.

    Args:
        folder_name (str): Name of the folder where files will be saved.
        data_dict (dict): Dictionary with filename (without extension) as key and DataFrame as value.
        output_dir (str): Base output directory where user folders will be created.
        save_format (str): 'excel', 'csv', or 'both'
    """
    full_path = os.path.join(output_dir, folder_name)
    os.makedirs(full_path, exist_ok=True)

    for filename, df in data_dict.items():
        if save_format in ("excel", "both"):
            try:
                excel_path = os.path.join(full_path, f"{filename}.xlsx")
                df.to_excel(excel_path, index=False)
            except Exception as e:
                print(f"Error saving {filename}.xlsx to {full_path}: {e}")

        if save_format in ("csv", "both"):
            try:
                csv_path = os.path.join(full_path, f"{filename}.csv")
                df.to_csv(csv_path, index=False)
            except Exception as e:
                print(f"Error saving {filename}.csv to {full_path}: {e}")
