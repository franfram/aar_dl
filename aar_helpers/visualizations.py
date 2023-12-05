import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.graph_objs as go
from plotly.subplots import make_subplots



def plot_confusion_matrix(model, x_val, y_val, label_names):
    # Predict on test data
    y_pred = model.predict(x_val)

    # convert predictions from probs to class labels
    y_pred_classes = np.argmax(y_pred, axis=-1)
    y_true_classes = np.argmax(y_val, axis=-1)

    # Reshape the predictions and true values
    y_pred_flat = y_pred_classes.flatten()
    y_true_flat = y_true_classes.flatten()


    # Compute confusion matrix. Unnormalized
    cm = confusion_matrix(y_true_flat, y_pred_flat)

    # Compute confusion matrix. Normalized
    cm_normalized = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]

    #cm.shape

    # Create the confusion matrix plot
    plt.figure(figsize=(10, 10))
    sns.heatmap(cm_normalized, annot=True, fmt=".2f", cmap="Blues", 
                xticklabels=label_names, yticklabels=label_names)  # Set custom labels
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.title('Confusion Matrix')
    plt.show()


def plot_loss(fit):

    history = fit.history
    train_loss = history['loss']
    val_loss = history['val_loss']
    train_acc = history['accuracy']  # Or 'acc' based on your TensorFlow version
    val_acc = history['val_accuracy']  # Or 'val_acc' based on your TensorFlow version
    epochs = list(range(1, len(train_loss) + 1))

    # Create subplots: one row, two columns
    fig = make_subplots(rows=1, cols=2, subplot_titles=('Training and Validation Loss', 'Training and Validation Accuracy'))

    # Define hover template
    hovertemplate = 'Epoch: %{x}<br>Value: %{y:.4f}<extra></extra>'

    # First subplot for loss
    fig.add_trace(go.Scatter(x=epochs, y=train_loss, mode='lines+markers', name='Training Loss', 
                            marker_color='red', hovertemplate=hovertemplate), row=1, col=1)
    fig.add_trace(go.Scatter(x=epochs, y=val_loss, mode='lines+markers', name='Validation Loss', 
                            marker_color='green', hovertemplate=hovertemplate), row=1, col=1)

    # Second subplot for accuracy
    fig.add_trace(go.Scatter(x=epochs, y=train_acc, mode='lines+markers', name='Training Accuracy', 
                            marker_color='red', hovertemplate=hovertemplate), row=1, col=2)
    fig.add_trace(go.Scatter(x=epochs, y=val_acc, mode='lines+markers', name='Validation Accuracy', 
                            marker_color='green', hovertemplate=hovertemplate), row=1, col=2)

    # Update xaxis properties
    # fig.update_xaxes(title_text='Epochs', tickmode='linear', row=1, col=1)
    # fig.update_xaxes(title_text='Epochs', tickmode='linear', row=1, col=2)

    # Update yaxis properties
    fig.update_yaxes(title_text='Loss', row=1, col=1)
    fig.update_yaxes(title_text='Accuracy', row=1, col=2)

    # Update layout and show plot
    fig.update_layout(title_text='Training and Validation Metrics', showlegend=True)
    fig.show()
    


def plot_class_distribution(y_train): 
    # Flatten the timestep and one-hot dimensions of your labels
    y_train_flat = y_train.reshape(-1, y_train.shape[-1])

    # Convert one-hot encoded labels to integers
    y_train_integers = np.argmax(y_train_flat, axis=1)

    # Plot distribution of classes
    hist_weights = np.ones_like(y_train_integers) / len(y_train_integers)

    fig = plt.figure()
    hist = plt.hist(y_train_integers, weights=hist_weights)

    return hist
