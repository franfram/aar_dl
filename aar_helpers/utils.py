#from google.colab import drive
#from pydrive.auth import GoogleAuth
#from pydrive.drive import GoogleDrive
#from oauth2client.client import GoogleCredentials
import os
import pandas as pd
import shutil

def convert_txt_to_csv_gdrive(gdrive_folder: str) -> None:
    """
    This function converts all .txt files in a Google Drive folder to .csv files.
    It creates new folders with the same name as the original ones but with the suffix "_csv",
    and saves the .csv files in these new folders.

    Args:
    gdrive_folder (str): The path to the Google Drive folder.

    Returns:
    None
    """
    # Authenticate and create the PyDrive client
    #gauth = GoogleAuth()
    #gauth.credentials = GoogleCredentials.get_application_default()
    #drive = GoogleDrive(gauth)

    # Get all folders in the directory
    folders = [f for f in os.listdir(gdrive_folder) if os.path.isdir(os.path.join(gdrive_folder, f))]

    # Iterate over the folders
    for folder in folders:
        print(f"Processing folder: {folder}")
        # Create new folder with suffix "_csv"
        new_folder = folder + "_csv"
        new_folder_path = os.path.join(gdrive_folder, new_folder)
        if os.path.exists(new_folder_path):
            print(f"Folder {new_folder} already exists. Skipping to avoid overwriting.")
            continue
        os.makedirs(new_folder_path, exist_ok=True)

        # Get all .txt files in the original folder
        folder_path = os.path.join(gdrive_folder, folder)
        txt_files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]

        # Iterate over the .txt files
        for txt_file in txt_files:
            print(f"Converting file: {txt_file}")
            try:
                # Load .txt file
                data = pd.read_csv(os.path.join(folder_path, txt_file), sep="\t")  # adjust the separator if needed

                # Save as .csv in the new folder
                csv_file = os.path.splitext(txt_file)[0] + '.csv'  # change .txt to .csv
                csv_file_path = os.path.join(new_folder_path, csv_file)
                if os.path.exists(csv_file_path):
                    print(f"File {csv_file} already exists. Skipping to avoid overwriting.")
                    continue
                data.to_csv(csv_file_path, index=False)
                print(f"Saved {csv_file} in {new_folder_path}")
            except Exception as e:
                print(f"Error processing file {txt_file}: {e}")




def backup_gdrive_folder(gdrive_folder: str) -> None:
    """
    This function creates a backup of a Google Drive folder.

    Args:
    gdrive_folder (str): The path to the Google Drive folder.

    Returns:
    None
    """
    backup_folder = gdrive_folder + "_backup"
    if os.path.exists(backup_folder):
        print(f"Backup folder {backup_folder} already exists. Skipping to avoid overwriting.")
        return
    shutil.copytree(gdrive_folder, backup_folder)
    print(f"Backup of {gdrive_folder} created at {backup_folder}")





def verify_backup(gdrive_folder: str, backup_folder: str, subfolder: str = None) -> None:
    """
    This function verifies that all the files in a specific subfolder of gdrive_folder and backup_folder are the same and their file sizes are the same.

    Args:
    gdrive_folder (str): The path to the Google Drive folder.
    backup_folder (str): The path to the backup folder.
    subfolder (str, optional): The subfolder to check. If not provided, checks the entire gdrive_folder.

    Returns:
    None
    """
    if subfolder:
        gdrive_folder = os.path.join(gdrive_folder, subfolder)
        backup_folder = os.path.join(backup_folder, subfolder)

    for dirpath, dirnames, filenames in os.walk(gdrive_folder):
        for filename in filenames:
            gdrive_file = os.path.join(dirpath, filename)
            backup_file = gdrive_file.replace(gdrive_folder, backup_folder)

            if not os.path.exists(backup_file):
                print(f"File {backup_file} does not exist in backup.")
                continue

            gdrive_file_size = os.path.getsize(gdrive_file)
            backup_file_size = os.path.getsize(backup_file)

            if gdrive_file_size != backup_file_size:
                print(f"File {backup_file} size does not match original file size.")


