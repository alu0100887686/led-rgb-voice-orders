import batch
import pyaudio
import wave
import nn as nn
from tkinter import *
from tkinter import ttk
from tkinter.filedialog import *
from datetime import datetime
import bridge
import threading


CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 3
WAVE_OUTPUT_FILENAME = "input.wav"
DATA_OUTPUT_FILENAME = "output.txt"
DEFAULT_JSON_FILE = '../../data/model/model.json'
DEFAULT_H5_FILE = '../../data/model/weights.h5'
PATH = os.path.abspath('')
DEFAULT_WAV_FOLDER = PATH + '/../../data/training_set'
TRAINING_SET_PATH = PATH + '/../../data/training_set'
VALIDATION_SET_PATH = PATH + '/../../data/validation_set'
TRAINING_DICTIONARY_PATH = TRAINING_SET_PATH + '/training_dictionary.csv'
VALIDATION_DICTIONARY_PATH = VALIDATION_SET_PATH + '/validation_dictionary.csv'
CSV_PATH = TRAINING_DICTIONARY_PATH
COMMANDS = { -1 : '[-1] : Instrucción Desconocida',
             1 : '[1] : LED Encender',
             2 : '[2] : LED Apagar',
             3 : '[3] : LED Cambiar Color',
             4 : '[4] : LED Permutar Colores',
             5 : '[5] : LED Parpadear',
             6 : '[6] : LED Disminuir Frecuencia',
             7 : '[7] : LED Aumentar Frecuencia'
             }


class GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Voice Recognition")
        self.tabControl = ttk.Notebook(root)
        self.tab1 = ttk.Frame(self.tabControl)
        self.tab2 = ttk.Frame(self.tabControl)
        self.tab3 = ttk.Frame(self.tabControl)
        self.tab4 = ttk.Frame(self.tabControl)
        self.tabControl.add(self.tab1, text='Validation')
        self.tabControl.add(self.tab2, text='Training')
        self.tabControl.add(self.tab3, text='Corpus')
        self.tabControl.add(self.tab4, text='Arduino')

        # TAB 1
        self.lf_output = LabelFrame(self.tab1, text="Output")
        self.btn_record = Button(self.tab1, text="Record...", command=self.record)
        self.string_prediction = StringVar(self.root)
        self.opt_menu_prediction = OptionMenu(self.lf_output, self.string_prediction, *COMMANDS.values())

        # TAB 2
        self.lf_train = LabelFrame(self.tab2, text="From Model and Weights")
        self.ent_JSON = Entry(self.lf_train)
        self.btn_JSON = Button(self.lf_train, text="Model...", command=lambda: self.set_text(askopenfilename(),
                                                                                             self.ent_JSON))
        self.ent_weights = Entry(self.lf_train)
        self.btn_weights = Button(self.lf_train, text="Weights...", command=lambda: self.set_text(askopenfilename(),
                                                                                                  self.ent_weights))
        self.btn_train = Button(self.lf_train, text="Train", command=self.train)

        # TAB 3
        self.lf_path = LabelFrame(self.tab3, text="Path")
        self.ent_path = Entry(self.lf_path)
        self.lf_prefix = LabelFrame(self.tab3, text="Filename Prefix")
        self.ent_prefix = Entry(self.lf_prefix)
        self.lf_class = LabelFrame(self.tab3, text="Class")
        self.ent_class = Entry(self.lf_class)

        self.btn_record_train = Button(self.tab3, text="Record...", command=lambda: self.record(True))

        # TAB 4
        #self.lf_output2 = LabelFrame(self.tab4, text="Output")
        self.btn_connect = Button(self.tab4, text="Connect...", command=self.connect)
        self.btn_disconnect = Button(self.tab4, text="Disconnect...", command=self.disconnect)
        #self.string_prediction2 = StringVar(self.root)
        #self.opt_menu_prediction2 = OptionMenu(self.lf_output, self.string_prediction, *COMMANDS.values())
        self.arduino = None

        # MODEL
        self.model = nn.import_model(DEFAULT_JSON_FILE, DEFAULT_H5_FILE)
        self.prediction = -1

        # STATUS BAR
        self.status_bar = Label(self.root, bd=1, relief=SUNKEN, anchor=W)

        self.set_text(DEFAULT_JSON_FILE, self.ent_JSON)
        self.set_text(DEFAULT_H5_FILE, self.ent_weights)
        self.set_text(DEFAULT_WAV_FOLDER, self.ent_path)

    def pack(self):
        self.tabControl.pack(expand=1, fill="both")  # Pack to make visible

        self.lf_output.pack(fill=X)
        self.btn_record.pack()
        self.opt_menu_prediction.pack(fill=X)

        self.lf_train.pack()
        self.ent_JSON.grid(row=0, column=0)
        self.btn_JSON.grid(row=0, column=1)

        self.ent_weights.grid(row=1, column=0)
        self.btn_weights.grid(row=1, column=1)

        self.btn_train.grid(row=2, columnspan=2)

        self.lf_path.pack(fill=X)
        self.ent_path.pack(fill=X)
        self.lf_prefix.pack(fill=X)
        self.ent_prefix.pack(fill=X)
        self.lf_class.pack(fill=X)
        self.ent_class.pack(fill=X)
        self.btn_record_train.pack(fill=X)

        self.status_bar.pack(side=BOTTOM, fill=X)

        self.btn_connect.pack()
        self.btn_disconnect.pack()

    def osx_fix(self):
        # a fix for running on OSX - to center the tab title text vertically
        if self.root.tk.call('tk', 'windowingsystem') == 'aqua':  # only for OSX
            s = ttk.Style()
            # Note: the name is specially for the text in the widgets
            s.configure('TNotebook.Tab', padding=(12, 8, 12, 0))

    def run(self):
        self.osx_fix()
        self.set_status("Program started")
        self.root.mainloop()

    def predict(self):
        self.set_status("Predicting...")
        self.prediction = nn.predict(self.model, WAVE_OUTPUT_FILENAME)
        self.string_prediction.set(COMMANDS[self.prediction])
        self.set_status("Prediction calculated")

    def train(self):
        self.set_status("Loading model from disk...")
        self.model = nn.import_model(self.ent_JSON.get(), self.ent_weights.get())
        self.set_status("Model loaded from disk")

    def connect(self):
        self.set_status("Connecting to Arduino UNO...")
        self.arduino = bridge.Arduino()
        if(self.arduino.arduino == None):
            self.set_status("Error connecting to Arduino UNO...")
        self.arduino.loop()

    def disconnect(self):
        if(self.arduino != None):
            self.arduino.disconnect()


    def record(self, training=False):
        self.set_status("Recording...")
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

        frames = []

        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()
        self.set_status("Finished Recording")
        filename = ''
        if training:
            date = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            filename = DEFAULT_WAV_FOLDER + self.ent_prefix.get() + date + ".wav"
        else:
            filename = WAVE_OUTPUT_FILENAME
        wf = wave.open(filename, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        if training:
            self.set_status('Saved at ' + self.ent_prefix.get() + date + ".wav")
            f = open(CSV_PATH, "a+")
            f.write(self.ent_prefix.get() + date + ".wav; " + self.ent_class.get() + '\n')
            f.close()
        else:
            self.predict()

    def set_text(self, text, entry):
        entry.delete(0, END)
        entry.insert(0, text)
        return

    def set_status(self, status):
        self.status_bar.config(text=status)


win = Tk()
gui = GUI(win)
gui.pack()
gui.run()
