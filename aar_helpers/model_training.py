import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv1D, MaxPooling1D, Flatten, Dense
from tensorflow.keras.utils import plot_model
from tensorflow.keras import layers
from tensorflow.keras.models import Model

from typing import List, Dict, Tuple, Union, Any

from sklearn.utils import class_weight
import matplotlib.pyplot as plt
tf.random.set_seed(42)



def compute_class_weights(y_train: np.ndarray) -> Dict[int, float]:
    """
    Compute class weights for a given training set.

    This function computes the class weights for a given training set, converts the weights to a dictionary,
    and plots the distribution of classes. The function treats each sequence of segments as a sample.

    Parameters:
    y_train (np.ndarray): The training set for which to compute class weights.

    Returns:
    """
    # Flatten the timestep and one-hot dimensions of your labels
    y_train_flat = y_train.reshape(-1, y_train.shape[-1])

    # Convert one-hot encoded labels to integers
    y_train_integers = np.argmax(y_train_flat, axis=1)

    # Calculate class weights
    class_weights = class_weight.compute_class_weight(
        'balanced',
        classes=np.unique(y_train_integers),
        y=y_train_integers)

    # Convert class weights to a dictionary to pass it to Keras
    class_weights_dict = dict(enumerate(class_weights))

    return class_weights_dict



def make_model(segment_size, sequence_length=10, nfeatures=8, nclasses=3, dropout_rate=0.0, cnn_only=False):
    input_shape = (segment_size * sequence_length, nfeatures)
    # Input layer
    inputs = tf.keras.Input(shape=input_shape)

    # CNN layers
    x = layers.Conv1D(filters=64, kernel_size=3, padding='same', activation='relu')(inputs)
    x = layers.MaxPooling1D(2)(x)
    x = layers.Dropout(dropout_rate)(x)  # Dropout layer after MaxPooling

    # Define pool sizes based on segment size. This will allow for different segment sizes
    pool_sizes = {32: [2, 2, 2, 2, 2, 2, 1],
                  64: [2, 2, 2, 2, 2, 1, 1],
                  128: [2, 2, 2, 2, 1, 1, 1],
                  256: [2, 2, 2, 1, 1, 1, 1]}

    for i in range(7):
        x = layers.Conv1D(filters=64, kernel_size=3, padding='same', activation='relu')(x)
        x = layers.MaxPooling1D(pool_sizes[segment_size][i])(x)
        x = layers.Dropout(dropout_rate)(x)  # Dropout layer after each MaxPooling

    if not cnn_only:
        # Transformer layers
        query_value_attention_seq = layers.MultiHeadAttention(num_heads=2, key_dim=2)(x, x)
        # Adding the self attention to the original sequence
        x = layers.Add()([x, query_value_attention_seq])
        # Layer Normalization
        x = layers.LayerNormalization(epsilon=1e-6)(x)
        # Position-wise Feed-Forward Part
        x = layers.Conv1D(filters=128, kernel_size=1, activation='relu')(x)
        x = layers.Conv1D(filters=64, kernel_size=1, activation='relu')(x)
        # Adding the position-wise feedforward to the sequence
        x = layers.Add()([x, query_value_attention_seq])
        # Layer Normalization
        x = layers.LayerNormalization(epsilon=1e-6)(x)
        # Dense layers for final classification - now it gives a prediction for each time step
        x = layers.TimeDistributed(layers.Dense(sequence_length, activation='relu'))(x)
        outputs = layers.TimeDistributed(layers.Dense(nclasses, activation='softmax'))(x)
    else: 
        None
        # add dense or flatten layer to make the cnn alone work. 
    
    # Creating the model
    model = Model(inputs=inputs, outputs=outputs)

    return model