import librosa
import numpy as np
import glob
import os
import pandas as pd

PATH = os.path.abspath('')
DEFAULT_WAV_FOLDER = PATH + '/../../data/training_set'
TRAINING_SET_PATH = PATH + '/../../data/training_set'
VALIDATION_SET_PATH = PATH + '/../../data/validation_set'
TRAINING_DICTIONARY_PATH = TRAINING_SET_PATH + '/training_dictionary.csv'
VALIDATION_DICTIONARY_PATH = VALIDATION_SET_PATH + '/validation_dictionary.csv'

def pitch_shift(db, csv):
    date = ""
    csv_content = ""
    dictionary = pd.read_csv(csv, sep=';', header=None).values
    basename = ""
    newname = ""
    label = -1
    for i in range(len(dictionary)):
        basename = dictionary[i][0]
        label = int(dictionary[i][1])
        for i in range (-6, 6):
            if i != 0:
                newname = basename.replace(".wav", "") + "_pitched_" + str(i) + "_steps.wav"
                y, sr = librosa.load(db + "/" + basename, sr=16000) # y is a numpy array of the wav file, sr = sample rate
                y_shifted = librosa.effects.pitch_shift(y, sr, n_steps=i) # shifted by i half steps
                librosa.output.write_wav(path = db + "/" + newname, y_shifted, sr)
                csv_content += newname + ";" + str(label) + "\n"
    f = open(csv, "a+")
    f.write(csv_content)
    f.close()

    pitch_shift(TRAINING_SET_PATH, TRAINING_DICTIONARY_PATH)
