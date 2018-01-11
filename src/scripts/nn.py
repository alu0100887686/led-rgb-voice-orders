#!/usr/bin/python
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Flatten
from keras.layers import LSTM
from keras.layers import Dropout
from keras import optimizers
from keras.models import model_from_json
import numpy as np
import batch # some methods to procces audio batchs
import time
import h5py
import sys, os

""" 7 clases:
    1: LED Encender
    2: LED Apagar
    3: LED Cambiar color
    4: LED Permutar colores
    5: LED Parpadear
    6: LED Disminuir frecuencia
    7: LED Aumentar frecuencia
"""

units_first_layer = 512
units_second_layer = 512
units_third_layer = 512
classes = 8
epochs = 30

PATH = os.path.abspath('')
TRAINING_SET_PATH = PATH + '/../../data/training_set'
VALIDATION_SET_PATH = PATH + '/../../data/validation_set'
TRAINING_DICTIONARY_PATH = TRAINING_SET_PATH + '/training_dictionary.csv'
VALIDATION_DICTIONARY_PATH = VALIDATION_SET_PATH + '/validation_dictionary.csv'

JSON_PATH = PATH + '/../../data/model/model.json'
H5_PATH = PATH + '/../../data/model/weights.h5'

TRAINING_FEATURES_DATASET_PATH = TRAINING_SET_PATH + '/training_features.npy'
VALIDATION_FEATURES_DATASET_PATH = VALIDATION_SET_PATH + '/validation_features.npy'
TRAINING_LABELS_DATASET_PATH = TRAINING_SET_PATH + '/training_labels.npy'
VALIDATION_LABELS_DATASET_PATH = VALIDATION_SET_PATH + '/validation_labels.npy'

def generate_model(training_set_path = TRAINING_SET_PATH, validation_set_path = VALIDATION_SET_PATH, \
    training_dictionary_path = TRAINING_DICTIONARY_PATH, validation_dictionary_path = VALIDATION_DICTIONARY_PATH, \
    json_path = JSON_PATH, h5_path = H5_PATH):
    # fix random seed for reproducibility
    np.random.seed(int(time.time()))
    # get training batch
    x_t, y_t = batch.batch(training_set_path, training_dictionary_path)
    # get validation batch
    x_v, y_v = batch.batch(validation_set_path, validation_dictionary_path)
    print("- Training and validation sets imported." +  str(x_t.shape))
    # create model
    model = Sequential()
    model.add(LSTM(units_first_layer, return_sequences=True, stateful=False, batch_input_shape = (None, x_t.shape[1], x_t.shape[2])))
    model.add(LSTM(units_second_layer, return_sequences=True, stateful=False))
    model.add(LSTM(units_third_layer, stateful=False))
    # add dropout to control for overfitting
    model.add(Dropout(.25))
    # squash output onto number of classes in probability space
    model.add(Dense(classes, activation='softmax'))
    # compile the model
    model.compile(loss='categorical_crossentropy', optimizer = 'adam', metrics=['accuracy'])
    # Fit the model
    print(model.fit(x_t, y_t, epochs = epochs, validation_data=(x_v, y_v)))
    # export model
    # serialize model to JSON
    model_json = model.to_json()
    with open(json_path, "w") as json_file:
        json_file.write(model_json)
    # serialize weights to HDF5
    model.save_weights(h5_path)
    print("- Model exported to disk.")
    return model


def import_model(json_path = JSON_PATH, h5_path = H5_PATH):
    # load json and create model
    json_file = open(json_path, 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)
    # load weights into new model
    loaded_model.load_weights(h5_path)
    print("Model loaded from disk.")
    return loaded_model


def predict(model, x_path): # should be specified a model an a audio instance
    x = batch.features(x_path)
    y = model.predict(np.array([x]))
    print (np.argmax(y) + 1)
    print (y)
    if(np.amax(y) < 0.95): # Undefined order
        return -1
    else:
        return np.argmax(y) + 1

def refit(x_t_path = TRAINING_FEATURES_DATASET_PATH, y_t_path = TRAINING_LABELS_DATASET_PATH, \
    x_v_path = VALIDATION_FEATURES_DATASET_PATH, y_v_path = VALIDATION_LABELS_DATASET_PATH, model = None):
    np.random.seed(int(time.time()))
    if model == None:
        model = import_model()
    # get training batch
    x_t, y_t = batch.import_dataset(x_t_path, y_t_path)
    # get validation batch
    x_v, y_v = batch.import_dataset(x_v_path, y_v_path)
    model.compile(loss='categorical_crossentropy', optimizer = 'adam', metrics=['accuracy'])
    model.fit(x_t, y_t, epochs = epochs, validation_data=(x_v, y_v))
    model_json = model.to_json()
    with open(JSON_PATH, "w") as json_file:
        json_file.write(model_json)
    # serialize weights to HDF5
    model.save_weights(H5_PATH)
    print("- Model exported to disk.")
    return model
