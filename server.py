from flask import Flask, render_template
import wave
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import numpy as np
from scipy import signal
import scipy.io.wavfile as wav
import sounddevice as sd
import os
from os.path import exists

app = Flask(__name__)

duration = 10  # recording duration in seconds
fs = 44100  # sampling frequency
channels = 1  # number of channels

def record_audio(filename):
    print("Recording started")
    myrecording = sd.rec(int(duration * fs), samplerate=fs,
    channels=channels, dtype='int16')
    sd.wait()  # Wait until recording is finished
    print("Recording stopped")
    wav.write(os.path.join("static", filename), fs, 
    myrecording)  # Save the recording to a file

def waveform():
    obj = wave.open('static/recorded_audio.wav', 'rb')
    sample_freq = obj.getframerate()
    n_samples = obj.getnframes()
    signal_wave = obj.readframes(-1)
    duration = n_samples/sample_freq
    signal_array = np.frombuffer(signal_wave, dtype=np.int16)
    time = np.linspace(0, duration, num=n_samples)

    plt.figure(figsize=(15, 5))
    plt.plot(time, signal_array)
    plt.title('Audio Plot')
    plt.ylabel('signal wave')
    plt.xlabel('time (s)')
    plt.xlim(0, duration)
    plt.savefig('static/waveform.png') # Save the waveform 
    # plot to a file
    plt.close()

def spectrogram():
    obj = wave.open('static/recorded_audio.wav', 'rb')
    sample_freq = obj.getframerate()
    n_samples = obj.getnframes()
    signal_wave = obj.readframes(-1)
    duration = n_samples/sample_freq
    signal_array = np.frombuffer(signal_wave, dtype=np.int16)

    # Compute the spectrogram
    window = signal.get_window('hamming', 1024)
    f, t, Sxx = signal.spectrogram(signal_array, sample_freq, 
    window=window, nperseg=1024, noverlap=512, mode='magnitude')

    # Plot the spectrogram
    plt.figure(figsize=(15, 5))
    plt.pcolormesh(t, f, 20 * np.log10(Sxx), cmap='inferno')
    plt.ylim(0, 22050)  # Limit the y axis to frequencies below
    # 22050 Hz
    plt.xlabel('Time (s)')
    plt.ylabel('Frequency (Hz)')
    plt.title('Spectrogram')
    plt.colorbar()
    plt.savefig('static/spectrogram.png')  # Save the 
    # spectrogram plot to a file
    plt.close()

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/record')
def record():
    path1 = "/home/pi/Desktop/server/static/recorded_audio.wav"
    path2 = "/home/pi/Desktop/server/static/spectrogram.png"
    path3 = "/home/pi/Desktop/server/static/waveform.png"

    if (os.path.exists(path1) or os.path.exists(path2) or 
    os.path.exists(path3)):
        os.remove(path1)
        os.remove(path2)
        os.remove(path3)
    else:
        pass

    record_audio('recorded_audio.wav')
    waveform()
    spectrogram()
    return render_template('recording.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
