

#import cudf as pd
#import cupy as np
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Union
from itertools import product




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


def replace_sheep_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Replace specific values in the 'sheep_name' column.

    - df (pd.DataFrame): The DataFrame to process.

    Returns:
    - pd.DataFrame: The DataFrame with replaced values in the 'sheep_name' column.
    """
    replacements = {'ov1b': 'ov1.', 'ov6b': 'ov6.'}
    df['sheep_name'] = df['sheep_name'].replace(replacements)
    return df

def filter_outliers(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """
    Filter out outliers in specified columns based on the IQR method.

    Parameters:
    - df (pd.DataFrame): The DataFrame to process.
    - columns (List[str]): The columns to filter.

    Returns:
    - pd.DataFrame: The DataFrame with outliers filtered out.
    """
    for column in columns:
        q1 = df[column].quantile(0.25)
        q3 = df[column].quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        df = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]
    return df

def transform_angles(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """
    Transform specified columns from degrees to radians.

    Parameters:
    - df (pd.DataFrame): The DataFrame to process.
    - columns (List[str]): The columns to transform.

    Returns:
    - pd.DataFrame: The DataFrame with transformed columns.
    """
    df[columns] = np.radians(df[columns])
    return df

def replace_nan_behaviours(df: pd.DataFrame) -> pd.DataFrame:
    """
    Replace NaN values in the 'behaviours' column with the label 'Unknown'.

    Parameters:
    - df (pd.DataFrame): The DataFrame to process.

    Returns:
    - pd.DataFrame: The DataFrame with NaN values replaced.
    """
    df['behaviours'] = df['behaviours'].fillna('Unknown')
    return df

def compute_behaviours(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute behaviours according to a specific rule.

    Parameters:
    - df (pd.DataFrame): The DataFrame to process.

    Returns:
    - pd.DataFrame: The DataFrame with computed behaviours.
    """
    replacements = {
        'resting': 'Inactive',
        'vigilance': 'Inactive',
        'fast_walk': 'Walking',
        'walk': 'Walking',
        'eating': 'Foraging',
        'search': 'Foraging'
    }
    df['behaviours'] = df['behaviours'].replace(replacements)
    return df

def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply a series of transformations to a DataFrame.

    Parameters:
    - df (pd.DataFrame): The DataFrame to process.

    Returns:
    - pd.DataFrame: The transformed DataFrame.
    """
    df = replace_sheep_names(df)
    df = filter_outliers(df, ['pitch.angle', 'roll.angle'])
    df = transform_angles(df, ['pitch.angle', 'roll.angle'])
    df = replace_nan_behaviours(df)
    df = compute_behaviours(df)
    return df





# Function to extract consecutive segments
def extract_consecutive_segments(df: pd.DataFrame, allowed_behaviours: List[str], sheep_name: str, month: int, behaviour_threshold: int=51, segment_size: int=256, sequence_length: int=5, move_window_by: str = 'segment') -> List[pd.DataFrame]:
    """
        Extracts sequences of consecutive segments of continuous data for a **specified sheep and month**,
    ensuring each segment in the sequence has at least a certain percentage of the same behaviour.
    Adds a new column indicating the majority behaviour in each segment.
    
    Parameters:
        - df: The DataFrame containing the sheep movement data.
        - allowed_behaviours: The behaviours that are allowed in the sequences of segments, e.g. ['Inactive', 'Walking', 'Foraging'].
        - sheep_name: The name of the sheep to filter the data.
        - month: The month to filter the data.
        - behaviour_threshold: The minimum percentage of rows with the same behaviour in each segment.
        - segment_size: The number of rows in each segment (default is 256 for 6.4s of data at 40Hz).
        - sequence_length: The number of consecutive segments in each sequence.
        - move_window_by: The unit to move the window by when extracting segments, either 'segment', 'fraction' or 'row'. Function speeds up when moving by 'segment' compared to 'fraction' or 'row', but number of sequences extracted is (expectedly) lower.
        
    Returns:
        - A list of DataFrames, each containing a sequence of consecutive segments of data for the specified
          sheep and month with the behaviour meeting the threshold, and a new column for the majority behaviour.
    """


    # Filter the DataFrame based on the sheep_name and month. Filtering by the month is important to keep the temporal order, but not for differentiating between months like with sheep
    filtered_df = df.query("`sheep_name` == @sheep_name and `month` == @month").reset_index(drop=True)

    sequences = []
    i = 0

    increments = {'segment': segment_size, 'franction': round(segment_size / 10), 'row': 1}
    increment = increments.get(move_window_by)
    if increment is None: 
        raise ValueError("Invalid value for `move_window_by`. Must be one of 'segment', 'fraction', or 'row'.")

    while i < len(filtered_df) - segment_size * sequence_length:
        sequence = filtered_df.iloc[i : i + segment_size * sequence_length].copy()  
        
        # Split the sequence into segments and validate each segment
        segments = [sequence.iloc[j*segment_size : (j+1)*segment_size].copy() for j in range(sequence_length)]
        valid_sequence = all(
            #segment['behaviours'].value_counts(normalize=True).iloc[0] * 100 >= behaviour_threshold
            segment['behaviours'].value_counts(normalize=True).index[0] in allowed_behaviours and segment['behaviours'].value_counts(normalize=True).iloc[0] * 100 >= behaviour_threshold[0]
            for segment in segments
        )
        
        if valid_sequence:
            # Add the majority behaviour label to the segments
            for segment in segments:
                most_common_behaviour = segment['behaviours'].mode()[0]
                segment.loc[:, 'behaviour_majority_label'] = most_common_behaviour
            
            sequences.append(pd.concat(segments, ignore_index=True))
            i += segment_size * sequence_length  # Move to the next non-overlapping sequence
        else:
            i += increment

    return sequences






def extract_all_segments(df: pd.DataFrame, behaviour_threshold: List = [51], segment_size: List = [32, 64, 128, 256], sequence_length: List = [5, 10, 15, 20]) -> Dict[str, Dict[str, Dict[str, Union[int, List[pd.DataFrame]]]]]:
    """
    Extract sequences of segments for all unique sheep in the dataframe, given a combination of `behaviour_threshold`, 
    `segment_size`, and `sequence_length`.
    
    This function iterates over all unique sheep_name values, extracts sequences of segments for each month,
    and then stores the sequences in a structured dictionary.
    
    Parameters:
    - df: DataFrame containing the sheep movement data.
    - behaviour_threshold: Minimum percentage of rows with the same behaviour in each segment (default is 90).
    - segment_size: Number of rows in each segment (default is 256 for 6.4s of data at 40Hz).
    - sequence_length: Number of consecutive segments in each sequence (default is 20).
    
    Returns:
    - A dictionary structured as:
    {'BF<behaviour_threshold>_SS<segment_size>_SL<sequence_length>}: 
        {
            'sheep_name': {
                'sequences': [list of sequences of segments],
                'behaviour_threshold': behaviour_threshold,
                'segment_size': segment_size,
                'sequence_length': sequence_length
            },
            ...
        }
        ... 
    }
    """

    full_data = {}

    for behaviour_threshold, segment_size, sequence_length in product(behaviour_threshold, segment_size, sequence_length): 

        segments_key = f"BT{behaviour_threshold}_SS{segment_size}_SL{sequence_length}"
        segments_key_NoAcc = f"BT{behaviour_threshold}_SS{segment_size}_SL{sequence_length}_NoAcc"

        all_segments = {}
        for sheep in df['sheep_name'].unique(): 
            sequences = []
            for month in df['month'].unique(): 
              #print(f"sheep: {sheep}")
              #print(f"month: {month}")
              

              sequences.extend(extract_consecutive_segments(df, sheep, month, behaviour_threshold, segment_size, sequence_length))

              all_segments[sheep] = {
                  'sequences': sequences, 
                  'behaviour_threshold': behaviour_threshold,
                  'segment_size': segment_size,
                  'sequence_length': sequence_length
              }
    
    
        if full_data.get(segments_key) == None:
            full_data.update({segments_key: all_segments})
            full_data.update({segments_key_NoAcc: all_segments}) # Acc data will be removed downstream
        else:
            print("There might be a problem")

    return full_data


























def data_pipeline():
    None 


    return
