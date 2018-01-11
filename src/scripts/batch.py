import scipy.io.wavfile
from scipy.fftpack import dct
import numpy as np
import glob
import os
import pandas as pd
import librosa


N_LED_RULES = 8
AUDIO_SR = 16000
MAX_SHIFT_STEPS = 5
MIN_SHIFT_STEPS = -4

PATH = os.path.abspath('')
DEFAULT_WAV_FOLDER = PATH + '/../../data/training_set'
TRAINING_SET_PATH = PATH + '/../../data/training_set'
VALIDATION_SET_PATH = PATH + '/../../data/validation_set'
TRAINING_DICTIONARY_PATH = TRAINING_SET_PATH + '/training_dictionary.csv'
VALIDATION_DICTIONARY_PATH = VALIDATION_SET_PATH + '/validation_dictionary.csv'

TRAINING_FEATURES_DATASET_PATH = TRAINING_SET_PATH + '/training_features.npy'
VALIDATION_FEATURES_DATASET_PATH = VALIDATION_SET_PATH + '/validation_features.npy'
TRAINING_LABELS_DATASET_PATH = TRAINING_SET_PATH + '/training_labels.npy'
VALIDATION_LABELS_DATASET_PATH = VALIDATION_SET_PATH + '/validation_labels.npy'

def instance(file_path, file_label):
    """
    Build an input instance. [features, label]
    """
    label_to_array = [0] * N_LED_RULES
    label_to_array[int(file_label) - 1] = 1
    return [features(file_path), label_to_array]

def features(file_path):
    """
    Get voice features by mfcc coefficients.
    """
    wave, sr = librosa.load(file_path, mono = True, sr = AUDIO_SR)
    wave = wave[::3]
    mfcc = librosa.feature.mfcc(wave, sr = AUDIO_SR)
    return mfcc

def batch(files_path, csv_path):
    """
    - Return a audio batch proccesed to be a RNN input implemented in Keras.
    - A folder path should be specified. There must be the wav files.
    - We are only working with wav files.
    """
    instances = [os.path.basename(x) for x in glob.glob(files_path + '/*.wav')]
    dictionary = pd.read_csv(csv_path, sep=';', header=None).values
    tmp = []
    x = []
    y = []
    for i in range(len(dictionary)):
        tmp = instance(files_path + '/' + dictionary[i][0], dictionary[i][1])
        x.append(tmp[0])
        y.append(tmp[1])
    x = np.array(x)
    y = np.array(y)
    return x, y

def pitch_shift(files_path, csv_path):
    """
    Generate files shifting the original tone
    """
    date = ""
    csv_content = ""
    dictionary = pd.read_csv(csv_path, sep=';', header=None).values
    basename = ""
    newname = ""
    label = -1
    for i in range(len(dictionary)):
        basename = dictionary[i][0]
        label = int(dictionary[i][1])
        for i in range (MIN_SHIFT_STEPS, MAX_SHIFT_STEPS): # Generate
            if i != 0:
                newname = basename.replace(".wav", "") + "_pitched_" + str(i) + "_steps.wav"
                y, sr = librosa.load(files_path + "/" + basename, sr = AUDIO_SR) # y is a numpy array of the wav file, sr = sample rate
                y_shifted = librosa.effects.pitch_shift(y, sr, n_steps = i) # shifted by i half steps
                librosa.output.write_wav(files_path + "/" + newname, y_shifted, sr)
                csv_content += newname + ";" + str(label) + "\n"
    f = open(csv_path, "a+")
    f.write(csv_content)
    f.close()

def build_dataset(files_path, csv_path, x_file_path, y_file_path):
    """
    Build a dataset from a set of audio files and an associated dictionary.
    """
    x, y = batch(files_path, csv_path) # build arrays
    # export arrays
    np.save(x_file_path, x)
    np.save(y_file_path, y)
    return x, y

def import_dataset(x_file_path, y_file_path):
    """
    Import a dataset from pre-builded features and labels files.
    """
    # import arrays
    x = np.load(x_file_path)
    y = np.load(y_file_path)
    return x, y
