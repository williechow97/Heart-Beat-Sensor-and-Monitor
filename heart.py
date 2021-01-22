import serial
import time
from matplotlib import pyplot as plt
from scipy import signal
import numpy as np
from datetime import datetime
import pandas as pd
import os.path
from os import path
import keyboard

print("Initializing Variables...")
# initialize read from Arduino
ser = serial.Serial('COM3', 9600, timeout=1) #change 'COM3' to proper port being used
ser.flush()
#filtering parameters
frequency = 50
signal_length = 30
plot_window = 3*frequency
buff_len = signal_length*frequency
plot_refresh = 30   # change to get a more clear plot to find see peaks
data_buffer = []    # array to save data for filtering process
#saving data parameters
raw_data=[] # array to save data to csv file
raw_time=[] #array to save time to csv file 
stored_data=[] #array to house csv of raw_data and raw_time
file_name_csv=''    # name of csv file where data is saved to
file_name_csv=str(datetime.now().date()) #set the name of the CSV file to be the date in YEAR-MONTH-DAY format    

time.sleep(1)
ser.flush()
counter = 0
fig=plt.figure(figsize=(15,5)) #set size of plot (width,length)

def filter_data(data, low, high, order):
    nyquist = 0.5 * frequency
    low_freq = low / nyquist
    high_freq = high / nyquist
    b, a = signal.butter(order, [low_freq, high_freq], btype='band')
    data = signal.detrend(data)
    data = signal.lfilter(b, a, data)
    data = np.gradient(data)
    return data

def store_to_csv(raw_data, raw_time):
    file_name_csv=datetime.now().date() #set the name of the CSV file to be the date in YEAR-MONTH-DAY format
    df=pd.DataFrame({'raw_data':raw_data, 'time_data':raw_time}) #create data frame to hold raw_data and time(seconds) 
    if not path.exists(str(file_name_csv)): # file does not exist, first time running program
        df.to_csv(str(file_name_csv), index=False) #store data frame into CSV file
        print('Success! Data transferred to CSV')
    else: #file exist (i.e using program in the same day) so append to existing CSV file
        df.to_csv(str(file_name_csv), mode='a', header=None, index=False) #mode='a' allows user to append to CSV file    
        print('Success! Data transferred to CSV')
        
def save_file(filename):
    with open(filename, 'a') as file_handle: #'a' stands for append if file already exist, will make new file if it does not exist
        row=str(raw_data[-1])+','+str(raw_time[-1])+'\n' #create string to house data in comma seperate format
        file_handle.write(row) #write to csv file        
            
def plot_live(signal_1):
    plt.cla()
    plt.plot(signal_1)
    plt.show(block=False)
    plt.pause(0.001)

def heartbeat_detection(upper_lim, lower_lim):
    global data_buffer
    window_size = 3 * frequency
    start = 0
    end = window_size
    temp_data = []
    temp_filtered = np.array([], dtype=int)
    peaks = []
    heartbeats = np.asarray([], dtype=int)
    while end < buff_len:
        temp_data = data_buffer[start:end]
        filter_data(0.5, 3.0, 3)
        peaks, _ = signal.find_peaks(temp_data, height=0)
        for x in peaks:
            if temp_data[x] >= lower_lim and temp_data[x] <= upper_lim:
                heartbeats = np.append(heartbeats, start + x)
        temp_filtered = np.concatenate((temp_filtered, temp_data), axis=None)
        start += window_size
        end += window_size
        plot_live(temp_filtered, heartbeats)
    return

try:
    print('Begin getting data...')
    print('Place finger on sensor and wait 10 seconds')
    while True:
        if keyboard.is_pressed('q'): #plotting termination key
            print('Ending Plotting...')
            break
        try:
            data = ser.readline().strip().decode()  #read data from arduino
        except UnicodeError:
            continue
        if data == '':
            continue
        if len(data_buffer) == buff_len:    
            raw_data.append(data_buffer[0]) #adding first element into csv array
            raw_time.append(float(time.time()))    #adding time to csv array...time is in total seconds from epoch time 01/01/1970
            #First-In-First-Out - FIFO
            data_buffer[:-1] = data_buffer[1:]
            data_buffer[-1] = int(data)
        else:
            data_buffer.append(int(data))
        if len(data_buffer) == buff_len:
            if counter % plot_refresh == 0:
                # filtering
                temp_buffer = data_buffer
                temp_buffer=filter_data(temp_buffer,0.15, 2.5, 3)
                # live plotting 
                plot_live(temp_buffer)
                #heartbeat_detection(1.75, 0.25)
            counter += 1               
except KeyboardInterrupt:
    print("finishing program")
    ser.close()
#storing data to csv    
print('Beging saving data...')
store_to_csv(raw_data, raw_time)
