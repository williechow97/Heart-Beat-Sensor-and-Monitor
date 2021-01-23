# Import relevant libraries
import serial
import time
from matplotlib import pyplot as plt
from scipy import signal
import numpy as np
import pandas as pd
from os import path
from datetime import datetime

# Create function to store your data to a .csv file
def store_to_csv(raw_data, raw_time):
    # set the name of the CSV file to be the date in YEAR-MONTH-DAY format
    file_name_csv=datetime.now().date()
    # create data frame to hold raw_data and time(seconds)
    df=pd.DataFrame({'raw_data':raw_data, 'time_data':raw_time})
    # check if file does not exist, first time running program
    if not path.exists(str(file_name_csv)+'.csv'):
        # store data frame into CSV file
        df.to_csv(str(file_name_csv)+'.csv', index=False)
        print('Success! Data transferred to CSV')
    # file exist (i.e using program in the same day) so append to existing CSV file
    else:
        # mode='a' allows user to append to CSV file
        df.to_csv(str(file_name_csv)+'.csv', mode='a', header=None, index=False)    
        print('Success! Data transferred to CSV')
        
# Set up your variables
serial_port = 'COM3'   # serial port your Arduino is connected to
baud_rate = 9600            # baud rate of Arduino sending data
frequency = 25              # in Hertz
signal_length = 30          # in seconds
buffer_len = signal_length*frequency              # number of data points in plot
refresh = 30                # refresh plot after certain amount of data points
data_buffer = []            # data that is being plotted
raw_data = []               # list that holds all data since program start
raw_time = []               # list that holds all timestamps since program start
file_name_csv = str(datetime.now().date())      # name of .csv file that will be produced
counter = 0                 # keeps track of number of data points received
bpm = 0                     # beats per minute
plt.figure(figsize=(8,16))  # configure the size of the plot

# Program start!
# Start serial communication between program and Arduino
print("Starting Program!")
print("Creating serial connection.")
ser = serial.Serial(serial_port, baud_rate, timeout=1)
time.sleep(2)       # Stop program for a couple seconds
ser.flush()         # Flush serial buffers
print("Beginning to read data.")
print("Please wait 30 seconds before plot corrects itself.")
try:
    while True:
        # Read data from Arduino, stop at each newline character, and decode it
        try:
            data = ser.readline().strip().decode()
        # if data is bad, reset loop
        except UnicodeError:
            continue
        if data == '':
            continue
        # FIFO buffer
        if len(data_buffer) == buffer_len:              # only run this code if list length has reached max length
            raw_data.append(data)                       # add data point to list of data for .csv file
            raw_time.append(float(time.time()))         # add timestamp to list of timestamps for .csv file
            data_buffer[:-1] = data_buffer[1:]          # shift list to the left by 1
            data_buffer[-1] = int(data)                 # add data point to last index in list
        else:
            data_buffer.append(int(data))               # only run this code if list length has not reached max length
        if len(data_buffer) >= 2:
            if counter % refresh == 0:                  # Refresh the plot after enough data points have been read
                temp_buffer = data_buffer               # Create temporary buffer for data
                heartbeats = []                         # Create empty list
                nyquist = 0.5 * frequency               # Set the nyquist frequency
                low_freq = 0.15 / nyquist               # Set lower frequency bound for filter
                high_freq = 2.5 / nyquist               # Set higher frequency bound for filter
                # Create coefficients for 3rd order bandpass Butterworth Filter
                b, a = signal.butter(3, [low_freq, high_freq], btype='band')
                # Remove linear trend along axis from data
                temp_buffer = signal.detrend(temp_buffer)
                # Pass data through Butterworth filter
                temp_buffer = signal.lfilter(b, a, temp_buffer)
                # Return the gradient of an array (returns the differential)
                temp_buffer = np.gradient(temp_buffer)
                # Return an array filled with indices of data points with a value above 0
                peaks, _ = signal.find_peaks(temp_buffer, height=0)
                # Check if each peak is really a heartbeat
                for x in peaks:
                    if temp_buffer[x] >= 1.0 and temp_buffer[x] <= 2.5:
                        # Append the index to the list
                        heartbeats.append(x)
                bpm = 2 * len(heartbeats)       # Estimate the BMP based off current data
                plt.cla()                       # Clear plot axis
                plt.subplot(211)                # Create a plotting area for two plots, plot in top box
                plt.tight_layout()              # Format plot area
                plt.title("Raw Data")
                plt.ylabel("Analog Voltage Reading")
                plt.plot(data_buffer)           # Plot original data from Arduino
                plt.subplot(212)                # Plot in bottom box
                plt.tight_layout()
                plt.title("Filtered Data")
                plt.ylabel("Magnitude")
                # Plot the filtered data a legend showing current BPM
                plt.plot(temp_buffer, label="BPM: " + str(bpm))
                # Plot an X on every peak which signifies a heartbeat
                plt.plot(heartbeats, temp_buffer[heartbeats], 'x')
                plt.legend(loc='lower right')   # Place legend in the lower right
                plt.show(block=False)           # Make it so that the plot doesn't need to be closed to update
                plt.pause(0.001)                # Wait a little bit to let plot update
            counter += 1        # Increase with each subsequent data point outside of refresh
except KeyboardInterrupt:       # Create an exception for when CTRL-C is pressed
    print("Finishing program and closing serial port.")
    ser.close()                         # Close serial communication
    store_to_csv(raw_data, raw_time)    # Store data and time in .csv file