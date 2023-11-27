import pandas as pd
import numpy as np



def get_unique_values(df: pd.DataFrame) -> dict:
    """
    Get unique values in each column of a DataFrame.

    Parameters:
    - df (pd.DataFrame): The DataFrame to process.

    Returns:
    - dict: A dictionary with column names as keys and unique values as values.
    """
    unique_values = {col: df[col].unique() for col in df.columns}
    return unique_values











# def filter_and_merge_behaviours(df: pd.DataFrame, behaviours_to_keep: list) -> pd.DataFrame:
def filter_data_and_merge_behaviours(df: pd.DataFrame) -> pd.DataFrame:
    """
    This function takes a DataFrame and:
    1. Merges rows with behaviours 'fast_walk' into 'walk'.
    2. Unifies values in the `sheep_name` column
    3. Filters out the extreme values of `pitch.angle` and `roll.angle` based on the IQR method. 
    
    Parameters:
    - df: A pandas DataFrame containing a 'behaviours' column
    
    Returns:
    - A modified DataFrame. 
    """

    # Replace 'fast_walk' with 'walk' in the 'behaviours' column
    df['behaviours'] = df['behaviours'].replace('fast_walk', 'walk')
    # Replace 'ov*b' with 'ov*'
    df['sheep_name'] = df['sheep_name'].replace('ov1b', 'ov1.')
    df['sheep_name'] = df['sheep_name'].replace('ov6b', 'ov6.')

    "THIS IS WRONG, WE ARE BREAKING THE TEMPORAL STRUCTURE IF WE FILTER AT THE ROW LEVEL. I have to remove this and filter at the segment level" 
    # Filter the DataFrame based on the behaviours_to_keep list
    # df = df[df['behaviours'].isin(behaviours_to_keep)]

    # Compute IQR for pitch.angle and roll.angle
    q1_pitch = df['pitch.angle'].quantile(0.25)
    q3_pitch = df['pitch.angle'].quantile(0.75)
    iqr_pitch = q3_pitch - q1_pitch
    q1_roll = df['roll.angle'].quantile(0.25)
    q3_roll = df['roll.angle'].quantile(0.75)
    iqr_roll = q3_roll - q1_roll

    # Determine bounds for pitch.angle and roll.angle
    lower_bound_pitch = q1_pitch - 1.5 * iqr_pitch
    upper_bound_pitch = q3_pitch + 1.5 * iqr_pitch
    lower_bound_roll = q1_roll - 1.5 * iqr_roll
    upper_bound_roll = q3_roll + 1.5 * iqr_roll

    # Filter out outliers
    df['pitch.angle'] = df[(df['pitch.angle'] >= lower_bound_pitch) & (df['pitch.angle'] <= upper_bound_pitch)]['pitch.angle']
    df['roll.angle'] = df[(df['roll.angle'] >= lower_bound_roll) & (df['roll.angle'] <= upper_bound_roll)]['roll.angle']

    
    # Transform from degrees to radians
    df['pitch.angle'] = np.radians(df['pitch.angle'])
    df['roll.angle'] = np.radians(df['roll.angle'])

    return df

# Example usage: Keeping only 'walk' and 'resting' behaviours in the DataFrame
# behaviours_to_keep = ['eating', 'walk', 'resting']
# filtered_data = filter_and_merge_behaviours(cleaned_data, behaviours_to_keep)
# filtered_data = filter_data_and_merge_behaviours(cleaned_data)