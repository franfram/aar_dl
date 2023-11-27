import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Union
from itertools import product



# def filter_and_merge_behaviours(df: pd.DataFrame, behaviours_to_keep: list) -> pd.DataFrame:
def filter_data_and_merge_behaviours(df: pd.DataFrame) -> pd.DataFrame:
    """
    This function takes a DataFrame and:
    1. Unifies values in the `sheep_name` column
    2. Filters out the extreme values of `pitch.angle` and `roll.angle` based on the IQR method. 
    3. Replaces NaN values in the `behaviour` column with the label `Unknown`. 
    4. Computes behaviours according to https://arxiv.org/pdf/2105.11490.pdf, i.e., the possible behaviours are  (i)Inactive (when the animal is still: resting or vigilant), (ii) Walk (normal walking speed with the head raised), (iii) Fast Walk (when the animal runs or moves fast) and (iv) Foraging (when the animal eats or looks for food. This can involve some walking but it is slow and with the head down). But we add the modification of `fast_walk` and `walk` are now `Walking`. 
    
    Parameters:
    - df: A pandas DataFrame containing a 'behaviours' column
    
    Returns:
    - A modified DataFrame. 
    """

    # Replace 'fast_walk' with 'walk' in the 'behaviours' column
    # Replace 'ov*b' with 'ov*'
    df['sheep_name'] = df['sheep_name'].replace('ov1b', 'ov1.')
    df['sheep_name'] = df['sheep_name'].replace('ov6b', 'ov6.')


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
    


    # Replace NaN values in the `behaviour` column with the label `Unknown`
    df['behaviours'] = df['behaviours'].fillna('Unknown')

    # Compute behaviours according to https://arxiv.org/pdf/2105.11490.pdf but with a Mod of `fast_walk` and `walk` are now `walking`
    ## Inactive
    df['behaviours'] = df['behaviours'].replace('resting', 'Inactive')
    df['behaviours'] = df['behaviours'].replace('vigilance', 'Inactive')

    ## Walking
    df['behaviours'] = df['behaviours'].replace('fast_walk', 'Walking')
    df['behaviours'] = df['behaviours'].replace('walk', 'Walking')

    ## Foraging
    df['behaviours'] = df['behaviours'].replace('eating', 'Foraging')
    df['behaviours'] = df['behaviours'].replace('search', 'Foraging')

    return df





# Function to extract consecutive segments
def extract_consecutive_segments(df: pd.DataFrame, allowed_behaviours: List[str], sheep_name: str, month: int, behaviour_threshold: int=51, segment_size: int=256, sequence_length: int=5) -> List[pd.DataFrame]:
    """
        Extracts sequences of consecutive segments of continuous data for a **specified sheep and month**,
    ensuring each segment in the sequence has at least a certain percentage of the same behaviour.
    Adds a new column indicating the majority behaviour in each segment.
    
    Parameters:
        - df: The DataFrame containing the sheep movement data.
        - allowed_behaviours: The behaviours that are allowed in the sequences of segments, e.g. ['walk', 'eating', 'resting'].
        - sheep_name: The name of the sheep to filter the data.
        - month: The month to filter the data.
        - behaviour_threshold: The minimum percentage of rows with the same behaviour in each segment.
        - segment_size: The number of rows in each segment (default is 256 for 6.4s of data at 40Hz).
        - sequence_length: The number of consecutive segments in each sequence.
        
    Returns:
        - A list of DataFrames, each containing a sequence of consecutive segments of data for the specified
          sheep and month with the behaviour meeting the threshold, and a new column for the majority behaviour.
    """

    try: 
        value = allowed_behaviours
    except NameError:
        print("`allowed_behaviours` is not defined, please pass it as an argument")
    

    # Filter the DataFrame based on the sheep_name and month. Filtering by the month is important to keep the temporal order, but not for differentiating between months like with sheep
    filtered_df = df[(df['sheep_name'] == sheep_name) & (df['month'] == month)].reset_index(drop=True)

    sequences = []
    i = 0
    
    while i < len(filtered_df) - segment_size * sequence_length:
        sequence = filtered_df.iloc[i : i + segment_size * sequence_length].copy()  
        
        # Split the sequence into segments and validate each segment
        segments = [sequence.iloc[j*segment_size : (j+1)*segment_size].copy() for j in range(sequence_length)]
        valid_sequence = all(
            segment['behaviours'].value_counts(normalize=True).iloc[0] * 100 >= behaviour_threshold
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
            i += segment_size  # Move by one segment and try again
    
    return sequences






def extract_all_segments(df: pd.DataFrame, behaviour_threshold: List = [51], segment_size: List = [32, 64, 128, 256], sequence_length: List = [5, 10, 15, 20]) -> Dict[str, Dict[str, Dict[str, Union[int, List[pd.DataFrame]]]]]:
    """
    UPDATE: extend to combinations of behaviour_threshold, segment_size, and sequence_length

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
              print(f"sheep: {sheep}")
              print(f"month: {month}")
              

              sequences.extend(extract_consecutive_segments(df, sheep, month, behaviour_threshold, segment_size, sequence_length))

              all_segments[sheep] = {
                  'sequences': sequences, 
                  'behaviour_threshold': behaviour_threshold,
                  'segment_size': segment_size,
                  'sequence_length': sequence_length
              }
    
    
        if full_data.get(segments_key) == None:
            full_data.update({segments_key: all_segments})
            full_data.update({segments_key_NoAcc: all_segments})
        else:
            print("There might be a problem")
    

    return full_data
