#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
import serial, sys, re, binascii
import serial.tools.list_ports
from scipy.io.wavfile import read
import nn
import pyaudio
import wave
from array import array
import numpy as np


CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 3
WAVE_OUTPUT_FILENAME = "input.wav"

COMMANDS = { -1 : '[-1] : Instrucción Desconocida',
             1 : '[1] : LED Encender',
             2 : '[2] : LED Apagar',
             3 : '[3] : LED Cambiar Color',
             4 : '[4] : LED Permutar Colores',
             5 : '[5] : LED Parpadear',
             6 : '[6] : LED Disminuir Frecuencia',
             7 : '[7] : LED Aumentar Frecuencia',
             8 : '[-1] : Instrucción Desconocida'
             }

class Arduino:

    def __init__(self):
        self.order = COMMANDS[-1]
        self.connect()
        self.model = nn.import_model()
        print("Model imported.")

    def connect(self):
        self.port = self.getSerialPort()
        if(self.port != None):
            self.arduino = serial.Serial(self.port, 9600)
            print("Connected to Arduino UNO.")
        else:
            self.arduino = None

    def disconnect(self):
        if(self.arduino != None):
            self.arduino.close()

    def getSerialPort(self):
        r = ""
        if sys.platform.startswith('linux2'): # Linux serial port
            r = re.compile("/dev/tty[A-Za-z]*")
        elif sys.platform.startswith('win32'): # Windows serial port
            r = re.compile("COM[A-Za-z0-9]*")
        elif sys.platform.startswith('darwin'): # Mac Osx serial port
            r = re.compile("/dev/cu.usbmodem[A-Za-z0-9]*")
        list = serial.tools.list_ports.comports()
        enable = []
        usable = []
        for i in list:
            enable.append(i.device)
        for i in filter(r.match, enable):
            usable.append(i)
        if len(usable) == 0:
            print("Error connecting to Arduino UNO.")
            return None
        return usable[0]

    def loop(self):
        if(self.arduino != None):
            while(True):
                print('Recording...')
                frames = []
                #frames.append(data3)
                p = pyaudio.PyAudio()
                stream = p.open(format=FORMAT, \
                         channels=CHANNELS, \
                         rate=RATE, \
                         input=True, \
                         frames_per_buffer=CHUNK)
                for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                    data = stream.read(CHUNK)
                    frames.append(data)
                #frames = np.delete(frames, len(frames)-1)
                stream.stop_stream()
                stream.close()
                p.terminate()
                print('Finished Recording')
                wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(p.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b''.join(frames))
                wf.close()

                samprate, wavdata = read(WAVE_OUTPUT_FILENAME)
                chunks = np.array_split(wavdata, CHUNK)
                dbs = 20*np.log10(np.amax(chunks))
                print(dbs)
                if dbs > 45:
                    option = nn.predict(self.model, WAVE_OUTPUT_FILENAME)
                    self.order = COMMANDS[option]
                    if option != 8:
                        self.arduino.write(str(option).encode())
            self.disconnect()
            return 1
        else:
            return 0
