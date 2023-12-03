# CHECK THIS
# https://mkdocstrings.github.io/recipes/

# TUTORIAL ON MKDOCS HERE (for proj and for blog)
#https://www.youtube.com/watch?v=Q-YA_dA8C20&t=967s
#https://www.youtube.com/watch?v=4OjnOc6ftJ8
#import cudf as pd
#import cupy as np
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Union, Any
from itertools import product
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from pyprojroot.here import here


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

def compute_behaviours(
        df: pd.DataFrame, 
        replacements: Dict = {
            'resting': 'Inactive',
            'vigilance': 'Inactive',
            'fast_walk': 'Walking',
            'walk': 'Walking',
            'eating': 'Foraging',
            'search': 'Foraging'
            #'search': 'Walking'
        }
) -> pd.DataFrame:
    """
    Compute behaviours according to a specific rule.

    Parameters:
    - df (pd.DataFrame): The DataFrame to process.

    Returns:
    - pd.DataFrame: The DataFrame with computed behaviours.
    """

    df['behaviours'] = df['behaviours'].replace(replacements)
    return df

def transform_data(
        df: pd.DataFrame, 
        replacements: Dict = {
            'resting': 'Inactive',
            'vigilance': 'Inactive',
            'fast_walk': 'Walking',
            'walk': 'Walking',
            'eating': 'Foraging',
            'search': 'Foraging'
            #'search': 'Walking'
        }
) -> pd.DataFrame:
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
    df = compute_behaviours(df, replacements=replacements)
    return df

# Function to extract consecutive segments
def extract_consecutive_segments(df: pd.DataFrame, allowed_behaviours: List[str], sheep_name: str, month: int, behaviour_threshold: int=51, segment_size: int=256, sequence_length: int=5, move_window_by: str = 'fraction') -> List[pd.DataFrame]:
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

    increments = {'segment': segment_size, 'fraction': round(segment_size / 10), 'row': 1}
    increment = increments.get(move_window_by)
    if increment is None: 
        raise ValueError("Invalid value for `move_window_by`. Must be one of 'segment', 'fraction', or 'row'.")

    while i < len(filtered_df) - segment_size * sequence_length:
        sequence = filtered_df.iloc[i : i + segment_size * sequence_length].copy()  
        
        # Split the sequence into segments and validate each segment
        segments = [sequence.iloc[j*segment_size : (j+1)*segment_size].copy() for j in range(sequence_length)]
        valid_sequence = all(
            #segment['behaviours'].value_counts(normalize=True).iloc[0] * 100 >= behaviour_threshold
            segment['behaviours'].value_counts(normalize=True).index[0] in allowed_behaviours and segment['behaviours'].value_counts(normalize=True).iloc[0] * 100 >= behaviour_threshold
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


def extract_all_segments(df: pd.DataFrame, allowed_behaviours: List[str] = ['Inactive', 'Walking', 'Foraging'], behaviour_threshold: Union[List, int] = [51], segment_size: Union[List, int] = [32, 64, 128, 256], sequence_length: Union[List, int] = [5, 10, 15, 20], move_window_by: str = 'segment') -> Dict[str, Dict[str, Dict[str, Union[int, List[pd.DataFrame]]]]]:
    """
    Extract sequences of segments for all unique sheep in the dataframe, given a combination of `behaviour_threshold`, 
    `segment_size`, and `sequence_length`.
    
    This function iterates over all unique sheep_name values, extracts sequences of segments for each month,
    and then stores the sequences in a structured dictionary.
    
    Parameters:
    - df: DataFrame containing the sheep movement data.
    - allowed_behaviours: The behaviours that are allowed in the sequences of segments, e.g. ['Inactive', 'Walking', 'Foraging'].
    - behaviour_threshold: Minimum percentage of rows with the same behaviour in each segment (default is 90).
    - segment_size: Number of rows in each segment (default is 256 for 6.4s of data at 40Hz).
    - sequence_length: Number of consecutive segments in each sequence (default is 20).
    - move_window_by: The unit to move the window by when extracting segments, either 'segment', 'fraction' or 'row'. Function speeds up when moving by 'segment' compared to 'fraction' or 'row', but number of sequences extracted is (expectedly) lower.
    
    Returns:
    - A dictionary structured as:
    {'BF<behaviour_threshold>_SS<segment_size>_SL<sequence_length>'}: 
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

    # Ensure params are lists
    behaviour_threshold, segment_size, sequence_length = [[p] if isinstance(p, int) else p for p in [behaviour_threshold, segment_size, sequence_length]]

    # Extract sequences of segments
    for behaviour_threshold, segment_size, sequence_length in product(behaviour_threshold, segment_size, sequence_length): 

        segments_key = f"BT{behaviour_threshold}_SS{segment_size}_SL{sequence_length}"
        segments_key_NoAcc = f"BT{behaviour_threshold}_SS{segment_size}_SL{sequence_length}_NoAcc"

        all_segments = {}
        for sheep in df['sheep_name'].unique(): 
            sequences = []
            for month in df['month'].unique(): 
              sequences.extend(extract_consecutive_segments(df, allowed_behaviours=allowed_behaviours, sheep_name=sheep, month=month, behaviour_threshold=behaviour_threshold, segment_size=segment_size, sequence_length=sequence_length, move_window_by=move_window_by))

            all_segments[sheep] = {
                'sequences': sequences, 
                'behaviour_threshold': behaviour_threshold,
                'segment_size': segment_size,
                'sequence_length': sequence_length
            }
    
            
    
        if full_data.get(segments_key) == None:
            full_data.update({segments_key: all_segments})
            #full_data.update({segments_key_NoAcc: all_segments}) # Acc data will be removed downstream
        else:
            print("There might be a problem")

        total_sequences = sum(len(sheep_data['sequences']) for sheep_data in all_segments.values())
        print(f"Total number of sequences for BF{behaviour_threshold}_SS{segment_size}_SL{sequence_length}: {total_sequences}")

    return full_data

def check_for_nans(arr, label):
    if np.isnan(np.array(arr)).any():
        print(f"NaNs detected in {label}")

"MUST THOROUGHLY CHECK THIS FUNCTION TO DETERMINE THE CAUSE OF THE SHAPE MISMATCHES"
"MUST REFACTOR THIS FUNCTION, LOOKS LIKE SH!T"
def prepare_training_data(
    all_segments: Dict[str, Dict[str, Union[int, List[pd.DataFrame]]]], 
    behaviour_threshold: int = 51,
    sequence_length: int = 10, 
    segment_size: int = 64, 
    features: List[str] = ['acc_x', 'acc_y', 'acc_z', 'mag_x', 'mag_y', 'mag_z', 'pitch.angle', 'roll.angle'], 
    nan_strategy: str = 'interpolate', # 'mean, 'median', or 'interpolate'
) -> Tuple[np.ndarray, np.ndarray, Dict]:
    """
    Prepare training data for the Convolutional + Transformer Neural Network model.

    Parameters:
    - all_segments: Dictionary containing the sequences of segments.
    - features: List of feature names to be used.
    - sequence_length: The number of consecutive segments in each sequence.
    - segment_size: The number of rows in each segment.
    - nan_strategy: The strategy to use for handling NaNs in the data.

    Returns:
    - x_train: Features data in the shape (n_sequences, sequence_length * segment_size, n_features).
    - y_train: One-hot encoded behaviours in the shape (n_sequences, sequence_length, n_behaviours).
    - behaviour_mapping: Mapping for the behaviour encoding
    """

    all_segments = all_segments[f"BT{behaviour_threshold}_SS{segment_size}_SL{sequence_length}"]

    # Initialize lists to hold the training data
    x_data = []
    y_data = []

    # Initialize OneHotEncoder for behaviours
    encoder = OneHotEncoder(sparse=False)


    # Collect all behaviour labels for fitting the encoder
    all_behaviours = []

    for sheep_data in all_segments.values():
        for sequence in sheep_data['sequences']:
            all_behaviours.extend(sequence['behaviour_majority_label'].unique())

    # Fit the encoder on all unique behaviours
    encoder.fit(np.array(all_behaviours).reshape(-1, 1))

    # Get the behaviour mapping
    behaviour_mapping = {category: idx for idx, category in enumerate(encoder.categories_[0])}

    # Choose the imputation strategy
    if nan_strategy in ['mean', 'median']:
        imputer = SimpleImputer(strategy=nan_strategy)

    # Choose post imputation strategy
    post_imputer = SimpleImputer(strategy='mean')

    # Extract features and one-hot encode behaviours for each sequence
    for sheep_data in all_segments.values():
        for sequence_idx, sequence in enumerate(sheep_data['sequences']):
            # Check if all features are present
            if not all(feature in sequence.columns for feature in features):
                missing_features = [feature for feature in features if feature not in sequence.columns]
                print(f"Missing features")# {missing_features} in sheep {sequence['sheep_name'].unique()}, sequence {sequence_idx}")
                continue  

            # Extract features
            sequence_features = sequence[features].values

            # Find the indices of NaNs before imputation
            #nan_indices = np.argwhere(np.isnan(sequence_features))


            # POST NAN CHECKING
            # Apply the chosen NaN handling strategy: 
            if nan_strategy in ['mean', 'median']:
                # Check if any columns only contain NaNs
                nan_cols = np.all(np.isnan(sequence_features), axis=0)
                if np.any(nan_cols):
                    print(f"Columns {np.where(nan_cols)} only contain NaNs.")

                # Calculate and print the percentage of NaNs
                nan_percentage = np.isnan(sequence_features).mean() * 100
                print(f"Percentage of NaNs when strategy is mean or median: {nan_percentage}%")


                # Impute NaNs
                sequence_features = imputer.fit_transform(sequence_features)


            elif nan_strategy == 'interpolate':
                # Check where NaNs are 
                sequence_features_check = pd.DataFrame(sequence_features)
                if sequence_features_check.isnull().values.any():
                    print("NaNs detected in sequence_features at:")
                    print(np.where(sequence_features_check.isnull()))

                # Calculate and print the percentage of NaNs
                #nan_percentage = sequence_features.isnull().mean().mean() * 100
                nan_percentage = np.isnan(sequence_features).mean().mean() * 100
                print(f"Percentage of NaNs when strategy is interpolate: {nan_percentage}%")

                # Impute NaNs
                #sequence_features = pd.DataFrame(sequence_features).interpolate(method='linear', axis=0).fillna(method='bfill').fillna(method='ffill').values
                sequence_features = pd.DataFrame(sequence_features).interpolate(method='linear', axis=0).bfill().ffill().values


            # PRE NAN CHECKING
            ## Apply the chosen NaN handling strategy: 
            #if nan_strategy in ['mean', 'median']:
                #sequence_features = imputer.fit_transform(sequence_features)
            #elif nan_strategy == 'interpolate':
                #sequence_features = pd.DataFrame(sequence_features).interpolate(method='linear', axis=0).fillna(method='bfill').fillna(method='ffill').values

           
            # Print the locations of imputed NaNs
            #for nan_idx in nan_indices:
                #feature_idx = nan_idx

            reshaped_features = sequence_features.reshape(sequence_length * segment_size, len(features))
            reshaped_features = post_imputer.fit_transform(reshaped_features)

            # Check the shape of reshaped_features
            if reshaped_features.shape != (sequence_length * segment_size, len(features)):
                print(f"Sequence {sequence_idx} will be dropped due to Shape mismatch in reshaped_features: {reshaped_features.shape} for sheep {sequence['sheep_name'].unique()}, sequence {sequence_idx}.\n ToDo: Try to handle these shape mismatches")
                continue  # Skip this sequence or handle it differently


            x_data.append(reshaped_features)
            check_for_nans(reshaped_features, label="reshaped_features")


            # One-hot encode behaviours
            behaviours = sequence['behaviour_majority_label'].iloc[::segment_size].values.reshape(-1, 1)
            encoded_behaviours = encoder.transform(behaviours)
            y_data.append(encoded_behaviours)
            check_for_nans(encoded_behaviours, label="encoded_behaviours after transformation")

    
    # Convert lists to numpy arrays
    x_data: np.ndarray = np.array(x_data)
    y_data: np.ndarray = np.array(y_data)
    
    return x_data, y_data, behaviour_mapping

def compute_behaviour_distribution(): 
    None

    return


def store_training_data(x_data: np.ndarray, y_data: np.ndarray, behaviour_threshold: int, segment_size: int, sequence_length: int) -> None:
    """
    Store the training data to disk.

    This function saves the feature data (x_data) and the target data (y_data) as numpy binary files (.npy).
    The files are saved in the 'data' directory with names based on the behaviour threshold, segment size, and sequence length.

    Parameters:
    - x_data (np.ndarray): The feature data to be saved.
    - y_data (np.ndarray): The target data to be saved.
    - behaviour_threshold (int): The behaviour threshold used in the data preparation.
    - segment_size (int): The segment size used in the data preparation.
    - sequence_length (int): The sequence length used in the data preparation.

    Returns:
    - None
    """
    x_data_path = here(f'data/x_data_BT{behaviour_threshold}_SS{segment_size}_SL{sequence_length}.npy')
    y_data_path = here(f'data/y_data_BT{behaviour_threshold}_SS{segment_size}_SL{sequence_length}.npy')

    np.save(x_data_path, x_data)
    np.save(y_data_path, y_data)

    print(f"Training data has been stored at data/<x or y>_data_BT{behaviour_threshold}_SS{segment_size}_SL{sequence_length}.npy")
    return None

def load_training_data(behaviour_threshold: int, segment_size: int, sequence_length: int) -> Tuple[np.ndarray, np.ndarray]:
    """
    Load the training data from disk.

    This function loads the feature data (x_data) and the target data (y_data) from numpy binary files (.npy).
    The files are loaded from the 'data' directory with names based on the behaviour threshold, segment size, and sequence length.

    Parameters:
    - behaviour_threshold (int): The behaviour threshold used in the data preparation.
    - segment_size (int): The segment size used in the data preparation.
    - sequence_length (int): The sequence length used in the data preparation.

    Returns:
    - x_data (np.ndarray): The loaded feature data.
    - y_data (np.ndarray): The loaded target data.
    """
    x_data_path = here(f'data/x_data_BT{behaviour_threshold}_SS{segment_size}_SL{sequence_length}.npy')
    y_data_path = here(f'data/y_data_BT{behaviour_threshold}_SS{segment_size}_SL{sequence_length}.npy')

    x_data = np.load(x_data_path)
    y_data = np.load(y_data_path)

    print(f"Training data has been loaded from data/<x or y>_data_BT{behaviour_threshold}_SS{segment_size}_SL{sequence_length}.npy")
    return x_data, y_data




def data_pipeline(
    data_path: str='data/clean_sheep_data_2019.csv', 
    features: List[str] = ['acc_x', 'acc_y', 'acc_z', 'mag_x', 'mag_y', 'mag_z', 'pitch.angle', 'roll.angle'],
    sequence_length: int = 10, 
    segment_size: int = 64,
    behaviour_threshold: int = 51,
    move_window_by: str = 'fraction',
    replacements: Dict = {
        'resting': 'Inactive',
        'vigilance': 'Inactive',
        'fast_walk': 'Walking',
        'walk': 'Walking',
        'eating': 'Foraging',
        #'search': 'Foraging'
        #'search': 'Walking'
    }
    
    ):

    cleaned_data = pd.read_csv(data_path)
    df = transform_data(cleaned_data, replacements=replacements)
    full_data = extract_all_segments(df,  behaviour_threshold=behaviour_threshold, segment_size=segment_size, sequence_length=sequence_length, move_window_by=move_window_by)
    x_data, y_data, behaviour_mapping = prepare_training_data(full_data, features = features, behaviour_threshold=behaviour_threshold, sequence_length=sequence_length, segment_size=segment_size)

    store_training_data(x_data, y_data, behaviour_threshold, segment_size, sequence_length)

    return x_data, y_data, behaviour_mapping, full_data



