import os
import re
from typing import List
#import pandas as pd
#import modin.pandas as pd
#import modin.config as modin_cfg
#modin_cfg.Engine.put("dask")
import dask.dataframe as pd

main_directory = r"/mnt/h/My Drive/ovejas_pict2015/exportado_2019"



def get_sorted_files(subdir_path: str) -> List[str]:
    """
    Get a list of all .txt files in a directory, sorted by Y and Z values.

    Parameters:
    subdir_path (str): The path to the directory.

    Returns:
    List[str]: A list of file names.
    """
    # regex pattern to match the file names and extract X, Y, Z values
    pattern = re.compile(r'collar_(\d+)_(\d+)_continuous_export_split#(\d+)_(\d+).txt')

    # get list of .txt file names in the directory
    file_names = [name for name in os.listdir(subdir_path) if name.endswith('.txt')]

    # extract Y and Z values from the file names
    file_data = [(name, int(pattern.match(name).group(2)), int(pattern.match(name).group(3))) for name in file_names if pattern.match(name)]

    # sort the file names by Y and Z values
    sorted_files = [name for name, y, z in sorted(file_data, key=lambda x: (x[1], x[2]))]

    return sorted_files


def find_missing_pairs(sorted_files: List[str], collar_number: int) -> List[str]:
    """
    Find missing (Z, Z-1) pairs in a list of sorted file names.

    Parameters:
    sorted_files (List[str]): A list of file names sorted by Y and Z values.
    collar_number (int): The sheep collar number.

    Returns:
    List[str]: A list of missing pairs.
    """

    # regex pattern to match the file names and extract X, Y, Z values
    pattern = re.compile(r'collar_(\d+)_(\d+)_continuous_export_split#(\d+)_(\d+).txt')

    missing_pairs = []

    # iterate over the sorted file names
    for i in range(1, len(sorted_files)):
        # extract Y and Z values from the current and previous file names
        y_prev, z_prev, _ = map(int, pattern.match(sorted_files[i-1]).groups()[1:])
        y_curr, z_curr, _ = map(int, pattern.match(sorted_files[i]).groups()[1:])

        # check if the current file is in the same Y group as the previous file
        if y_prev == y_curr:
            # check if there's a missing pair
            if z_curr - z_prev > 1:
                # add the missing pairs to the list
                missing_pairs.extend([f'collar_{collar_number}_{y_curr}_continuous_export_split#{z}_{z-1}.txt' for z in range(z_prev + 1, z_curr)])

    return missing_pairs


def find_missing_rows(file1: str, file2: str, id_column: str = 'Total Event no.') -> bool:
    """
    Check if there are missing rows between two sequential files.

    Parameters:
    file1 (str): The path to the first file.
    file2 (str): The path to the second file.
    id_column (str): The name of the column that contains the identifier.

    Returns:
    bool: True if there are missing rows, False otherwise.
    """
    # read the files as dataframes
    try: 
        df1 = pd.read_csv(file1, usecols=[id_column])
        df2 = pd.read_csv(file2, usecols=[id_column])
    except: 
        return f"The column '{id_column}' does not exist in one or both of the files {file1} and {file2}"


    #----------------------------------- old slow code ------------------
    #df1 = pd.read_csv(file1, engine="pyarrow")
    #df2 = pd.read_csv(file2, engine="pyarrow")

    ## check if the id_column exists in both dataframes
    #if id_column not in df1.columns or id_column not in df2.columns:
        #return f"The column '{id_column}' does not exist in one or both of the files {file1} and {file2}"
    # --------------------------------------------------------------------

    # get the last row's value of the id_column in the first file
    last_value_file1 = df1[id_column].iloc[-1]

    # get the first row's value of the id_column in the second file
    first_value_file2 = df2[id_column].iloc[0]

    # check if the values are sequential
    if last_value_file1 + 1 != first_value_file2:
        return f"Missing rows between {file1} and {file2}"
    else:
        return ""




#os.path.join(main_directory, subdir, sorted_files[0])
# This file does not have the event.number column: `pd.read_csv(os.path.join(main_directory, '2', sorted_files[0])).columns`
#pd.read_csv(os.path.join(main_directory, '1', 'collar_1_1_continuous_export_split#1_0.txt')).columns[0].split('\t')[0]

if __name__ == "__main__":
    print("Getting the missing files in the main directory and its subdirectories.")
    # open the output file
    with open('missing_files_results.txt', 'w') as f:
        # iterate over the subdirectories in the main directory
        for subdir in os.listdir(main_directory):
            if subdir != "README":
                subdir_path = os.path.join(main_directory, subdir)
                if os.path.isdir(subdir_path):
                    # get the collar number from the subdirectory name
                    collar_number = int(subdir)
                    # get the sorted file names in the subdirectory
                    sorted_files = get_sorted_files(subdir_path)
                    # find the missing pairs in the sorted file names
                    missing_pairs = find_missing_pairs(sorted_files, collar_number)
                    # write results to the file and print them
                    if missing_pairs:
                        output = f"The following files are missing from collar {collar_number}:"
                        print(output)
                        f.write(output + "\n")
                        for file in missing_pairs:
                            output = f"\t{file}"
                            print(output)
                            f.write(output + "\n")
                    else:
                        output = f"No files are missing from collar {collar_number}."
                        print(output)
                        f.write(output + "\n")    

    print("Getting the missing rows of sequential files (i.e., same Y values, consecutive Z values) in the main directory and its subdirectories.")
    with open('missing_rows_results.txt', 'w') as f:
        # define the regex pattern to match the file names. 
        pattern = re.compile(r'collar_(\d+)_(\d+)_continuous_export_split#(\d+)_(\d+).txt')
        # iterate over the subdirectories in the main directory
        for subdir in os.listdir(main_directory):
            if subdir != "README":
                subdir_path = os.path.join(main_directory, subdir)
                if os.path.isdir(subdir_path):
                    # get the collar number from the subdirectory name
                    collar_number = int(subdir)
                    # get the sorted file names in the subdirectory
                    sorted_files = get_sorted_files(subdir_path)
                        # iterate over the sorted file names
                    for i in range(1, len(sorted_files)):
                        # extract Y and Z values from the current and previous file names
                        y_prev, z_prev, _ = map(int, pattern.match(sorted_files[i-1]).groups()[1:])
                        y_curr, z_curr, _ = map(int, pattern.match(sorted_files[i]).groups()[1:])

                        # check if the current file is in the same Y group as the previous file and Z values are sequential
                        if y_prev == y_curr and z_curr - z_prev == 1:
                            # get the full paths to the current and previous files
                            file1 = os.path.join(subdir_path, sorted_files[i-1])
                            file2 = os.path.join(subdir_path, sorted_files[i])

                            # check for missing rows
                            result = find_missing_rows(file1, file2, 'Total Event no.')
                            if result: 
                                print(result)
                                f.write(result + "\n")










pd.read_csv()