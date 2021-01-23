# Sensor
Code that will taken input from a sensor, decode the input data, store the data in an excel/csv file, and plot the data in real time.

Senor.py -- 
  Uses matlibplot's built-in function FuncAnimation to handle the real time plotting
**Problem is data received is too fast as FuncAnimation cannot keep up with the plot

OfficialHeartBeatMonitor.py --
  Improved live plotting of data in real time to kept up with the fast sampling rate of Arduino
  Saves data in csv file
