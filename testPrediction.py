import aar_helpers as ad
import numpy as np
import pandas as pd
import tensorflow as tf
from pyprojroot.here import here
#from tensorflow.keras.models import Sequential
#from tensorflow.keras.layers import Conv1D, MaxPooling1D, Flatten, Dense
#from tensorflow.keras.utils import plot_model

from tensorflow.keras import layers
from tensorflow.keras import metrics
from tensorflow.keras.models import Model
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras.models import load_model
from tensorflow.keras.optimizers import *
from tensorflow.keras.callbacks import ModelCheckpoint

from tensorflow import keras
from tensorflow.keras import backend as K

from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.utils import class_weight
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.graph_objs as go
from plotly.subplots import make_subplots

tf.random.set_seed(42)


# Define behaviour classes to be used in training    
replacements = {
    'resting': 'Inactive',
    'vigilance': 'Inactive',
    'fast_walk': 'Walking',
    'walk': 'Walking',
    'eating': 'Foraging',
    #'search': 'Foraging'
    #'search': 'Walking'
}


data_path = here('data/clean_sheep_data_2019.csv')
#features = ['acc_x', 'acc_y', 'acc_z', 'mag_x', 'mag_y', 'mag_z', 'pitch.angle', 'roll.angle']
#features = ['acc_x', 'acc_y', 'acc_z', 'pitch.angle', 'roll.angle']
features = ['acc_x', 'acc_y', 'acc_z', 'pitch.angle']
allowed_behaviours=['Inactive', 'Walking', 'Foraging']

# Number of segments in a sequence
sequence_length = 10
# Length of segment. Since data is 40Hz, a segment_size of 64 equals 1 minute. 
segment_size = 128
# Threshold to determine the behaviour of a segment (e.g., a segment of 1 minute has 64 records of behaviour. behaviour_threshold=51 means that at least 51% of the records have to be of the same class, and that class will be the segment's behaviour class)
behaviour_threshold = 51
 
move_window_by = 'fraction'

x_data, y_data, behaviour_mapping, full_data = ad.data_pipeline(
    data_path=data_path, 
    features=features, 
    sequence_length=sequence_length,
    segment_size=segment_size, 
    behaviour_threshold=behaviour_threshold, 
    move_window_by=move_window_by, 
    replacements=replacements
)


x_data, y_data = ad.load_training_data(segment_size=segment_size, sequence_length=sequence_length, behaviour_threshold=behaviour_threshold)
n_features = x_data.shape[2]
n_classes = y_data.shape[2]

x_train, x_val, y_train, y_val = train_test_split(x_data, y_data, test_size=0.2, random_state=42, shuffle=False)




label_names = list(behaviour_mapping.keys())

class_weights_dict = ad.compute_class_weights(y_train)


lr=1e-6
epochs=300
patience=50


earlystop_callback = tf.keras.callbacks.EarlyStopping(
    #monitor='val_accuracy', min_delta=0.0001, patience=20
    monitor='val_loss', min_delta=0.0001, patience=patience
)

## F1-Score based callback
#earlystop_callback = tf.keras.callbacks.EarlyStopping(
    #monitor='val_auc',
    #mode='max',  # We want to maximize F1-score
    #patience=10,
    #restore_best_weights=True
#)

checkpoint = ModelCheckpoint('model-{epoch:03d}.keras', verbose=1, monitor='val_loss', save_best_only=False, mode='auto')

#class SaveBestModel(tf.keras.callbacks.Callback):
    #def __init__(self, save_best_metric='val_auc', this_max=True):
        #super(SaveBestModel, self).__init__()
        #self.save_best_metric = save_best_metric
        #self.this_max = this_max
        #self.best_weights = None
        #self.best_value = -float('inf') if this_max else float('inf')

    #def on_epoch_end(self, epoch, logs=None):
        #current_value = logs.get(self.save_best_metric)
        #if current_value is None:
            #return
        #if (self.this_max and current_value > self.best_value) or (not self.this_max and current_value < self.best_value):
            #self.best_value = current_value
            #self.best_weights = self.model.get_weights()

    #def on_train_end(self, logs=None):
        #self.model.set_weights(self.best_weights)

#save_best_model_callback = SaveBestModel(save_best_metric='val_auc', this_max=True)





model = ad.make_model(segment_size=segment_size, sequence_length=sequence_length, nfeatures=n_features, nclasses=n_classes, cnn_only=False, dropout_rate=0)



"""
DEFINE CUSTOM LOSS FUNCTION

"""
# Define custom loss function in order to apply class weights manually to each time step. 
def weighted_categorical_crossentropy(class_weights):
    def loss(y_true, y_pred):
        # Flatten the time dimension
        y_true_flat = tf.reshape(y_true, [-1, y_true.shape[-1]])
        y_pred_flat = tf.reshape(y_pred, [-1, y_pred.shape[-1]])

        # Convert one-hot to class indices
        y_true_int = tf.argmax(y_true_flat, axis=-1)

        # Get class weights for each sample
        weights = tf.gather(tf.constant(list(class_weights.values()), dtype=tf.float32), y_true_int)

        # Compute categorical crossentropy
        cce = tf.keras.losses.categorical_crossentropy(y_true_flat, y_pred_flat)

        # Apply weights
        weighted_cce = cce * weights

        return tf.reduce_mean(weighted_cce)

    return loss

model.compile(optimizer='adam', 
              loss=weighted_categorical_crossentropy(class_weights_dict),
              metrics=['accuracy'])

#model.compile(
    #optimizer='adam', 
    #loss=weighted_categorical_crossentropy(class_weights_dict),
    #metrics=[
        #metrics.CategoricalAccuracy(name='accuracy'),
        #metrics.Precision(name='precision'),
        #metrics.Recall(name='recall'),
        #metrics.AUC(name='auc'),
    #]
#)


#model.compile(optimizer='adam', 
              #loss=weighted_categorical_crossentropy(class_weights_dict),
              #metrics=['accuracy', f1_score, precision, recall])


#model.compile(
    ##optimizer=tf.keras.optimizers.Adam(learning_rate=lr),
    #optimizer=tf.keras.optimizers.Adadelta(), 
    ##loss='categorical_crossentropy',
    #loss=tf.keras.losses.CategoricalCrossentropy(),
    ##loss=tf.keras.losses.CategoricalFocalCrossentropy(gamma=10),
    ##loss=tf.keras.losses.CategoricalFocalCrossentropy(),
    #metrics=['accuracy']
    ##metrics=[
        ##metrics.CategoricalAccuracy(name='accuracy'),
        ##metrics.Precision(name='precision'),
        ##metrics.Recall(name='recall'),
        ##metrics.AUC(name='auc'),
    ##], 
    ##metrics=['accuracy', 'f1_score']
    ##metrics=['precision']
    ##metrics=['accuracy', 'precision']#, 'recall']# 'AUC', 'AUPRC'] #Accuracy is not an useful metric here?
    ##metrics=tf.keras.metrics.CategoricalAccuracy(name='categorical_accuracy')
#)

fit = model.fit(
    x=x_train, 
    y=y_train,  
    batch_size=64, 
    epochs=epochs, 
    validation_data=(x_val, y_val),
    callbacks=[earlystop_callback],
    #callbacks=[earlystop_callback, save_best_model_callback],
)


ad.plot_loss(fit)
ad.plot_confusion_matrix(model, x_val, y_val, label_names)

##model = load_model(f"./")

