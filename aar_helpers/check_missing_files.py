"""
Notes:
given a collar_X_Y_continuous_export_split#Z_Z-1.txt, there's a few problems: 
1. max(Z) is not constant across Y nor X. Is this because the compressed file that generated the collar_X_Y_continuous_export_split#Z_Z-1.txt files changes in size or because it failed to export?
2. Y is not sequential, e.g., sometimes Y={1, 2, 4, 5}, instead of Y={1, 2, 3, 4, 5}. Since the compressed text files (text.txt through text{max(Y)}) are sequential, that means a failure during extraction. 
"""



import os
import re
from typing import List
import argparse

# directory containing the subdirectories
main_directory = r"/mnt/h/My Drive/ovejas_pict2015/exportado_2019"
# name of the text file containing the results
output_file = "missing_files_results.txt"

print()


def check_missing_files(main_directory: str, output_file: str) -> None:
    """
    Check for missing files in the specified directory and its subdirectories.

    Parameters:
    main_directory (str): The main directory to check.
    output_file (str): The file to write the results to.

    Returns:
    None
    """
    # regex pattern to match the file names and extract X, Y, Z values
    pattern = re.compile(r'collar_(\d+)_(\d+)_continuous_export_split#\d+_\d+.txt')

    # open the output file
    with open(output_file, 'w') as f:
        message = "The format of the parsed files is collar_X_Y_continuous_export_split#Z_Z-1.txt \n -------------------------------------- \n"
        f.write(message)
        print(message)

        # iterate over subdirectories in the main directory
        for subdir in os.listdir(main_directory):
            subdir_path = os.path.join(main_directory, subdir)
            if os.path.isdir(subdir_path):
                # get list of .txt file names in the subdirectory
                file_names = [name for name in os.listdir(subdir_path) if name.endswith('.txt')]

                # extract Y values from the file names and find the maximum
                y_values = [int(pattern.match(name).group(2)) for name in file_names if pattern.match(name)]
                max_y = max(y_values, default=0)

                # check for missing Y values
                for y in range(1, max_y + 1):
                    if y not in y_values:
                        message = f'Missing files for X={subdir}, Y={y}. \n That is, text{y}.txt for collar {subdir} has not been exported correctly\n'
                        f.write(message)
                        print(message)

        output_path = os.path.join(os.getcwd(), output_file)
        print(f"Results written to {output_path}")


# usage:
# python check_missing_files.py "/mnt/h/My Drive/ovejas_pict2015/exportado_2019" "missing_files_results.txt"
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Check for missing files inside a directory and its subdirectories. The missing files are due to bad exports from sheep collar data.')
    parser.add_argument('--main_directory', type=str, help='The main directory to check. Defaults to /mnt/h/My Drive/ovejas_pict2015/exportado_2019', default = r"/mnt/h/My Drive/ovejas_pict2015/exportado_2019")
    parser.add_argument('--output_file', type=str, help='The file to write the results to. Defaults to missing_files_results.txt', default = "missing_files_results.txt")
    args = parser.parse_args()

    check_missing_files(main_directory=args.main_directory, output_file=args.output_file)
