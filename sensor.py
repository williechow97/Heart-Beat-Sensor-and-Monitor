import serial
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.animation as animation
import csv
from datetime import datetime, time
#import openpyxl as pxl
import os.path
from os import path
from scipy import signal


print('Initializing Variables...')
#file saving variables 
raw_data=[] #create array to hold raw data from Arduino
time_data=[] #create array to hold seconds count
#file_name_excel="testData.xlsx" #create name for our excel file
                                #ASIDE: pxl only works for xlsx not xls
file_name_csv='' #create name for csv file

#plotting variables
fig=plt.figure(figsize=(15,5))
ax=fig.add_subplot(1,1,1)
xs=[] #create array to hold time count for plotting PPG
ys=[] #create array to hold data from Arduino for plotting PPG

#Getting Time for title of Plot and Excel Sheet
time_now=datetime.now().strftime("%B-%d-%Y %H:%M:%S")  #format current time in Mon-Day-Year Hour:Minute:Sec
print(time_now)
print('Begin reading and plotting data...')
    
#Initializing communication with Arudino
arduino=serial.Serial('COM3',9600)  #telling python where arduino is...change to match port of Arduino
raw_Data=arduino.readline() #first data is garbage, so read and discard

'''
Func: animate()
Param: self, list, list
Descrip: Function that when called reads input from the arduino, decodes the input, and plots input data in real time
'''
def animate(self, xs, ys):
    plot_data=arduino.readline().decode('ascii').rstrip('\r\n')    #getting data from arduino
    xs.append(str(datetime.now().time())) #creating x-axis label as the time in Year-Month-Day Hours:Minutes:Seconds as a float
    ys.append(float(plot_data))

    #adding data to excel arrays
    raw_data.append(float(ys[-1]))
    time_data.append((xs[-1]))    
        
    #limit x and y lists to 20 items
    xs=xs[-20:]
    ys=ys[-20:]
    
    #plot x and y list
    ax.clear()
    ax.plot(xs,ys)
    
    #format plot
    plt.xticks(rotation=45, fontsize=8) #horizontal alightment: ha="right"
    ax.xaxis.set_major_locator(ticker.LinearLocator(8)) #set x-axis ticks to always display 8 value
    plt.yticks(fontsize=10)
    plt.ylim([int(min(ys))-1,int(max(ys))+1]) #set limits of y-axis
    plt.subplots_adjust(bottom=0.25) #pad the bottom of the plot 
    plt.title(time_now, fontsize=10) #create plot title
    plt.xlabel('Time(sec)',fontsize=10) 

def store_to_csv():
    file_name_csv=datetime.now().date() #set the name of the CSV file to be the date in YEAR-MONTH-DAY format
    df=pd.DataFrame({'raw_data':raw_data, 'time_data':time_data}) #create data frame to hold raw_data and time(seconds) 
    if not path.exists(str(file_name_csv)): # file does not exist, first time running program
        df.to_csv(str(file_name_csv), index=False) #store data frame into CSV file
        print('Success! Data transferred to CSV')
    else: #file exist (i.e using program in the same day) so append to existing CSV file
        df.to_csv(str(file_name_csv), mode='a', index=False) #mode='a' allows user to append to CSV file    
        print('Success! Data transferred to CSV')

'''
def store_to_excel():
    #Storing Data in Excel
    df=pd.DataFrame({'raw_data':raw_data, 'time_data':time_data}) #create data frame to hold raw_data and time(seconds) 
    try:
        if not path.exists(file_name): # file does not exist, first time running program
            df.to_excel(file_name, sheet_name=time_now.replace(':','_'), index=False)    #Create and write to excel sheet
            print('Success! Data transferred to Excel')
        else:
            # file exist append new sheet to excel file
            excel_book=pxl.load_workbook(file_name) #load the excel file
            with pd.ExcelWriter(file_name, engine='openpyxl') as writer: #context manager used to open and close file to release memory
                                                                         #creates a representation of a workbook
                writer.book=excel_book #binds the loaded workbook to our representation of a workbook
                writer.sheets={ #binds title and sheet of workbook to our representation of a workbook 
                    worksheet.title: worksheet
                    for worksheet in excel_book.worksheets
                }
                df.to_excel(writer, sheet_name=time_now.replace(':','_'), index=False)    #write to representation of workbook
                writer.save() #save workbook by writting over original workbook
                print('Success! Data transferred to Excel')
    except PermissionError:
        print('File is opened, cannot write to file') 
''' 
def main():
    '''
    call define function animate() to plot data in real time using FuncAnimation()
    Param: figure of plot, reference of function animate(), parameters for animate(), sampling rate
    '''    
    ani=animation.FuncAnimation(fig, animate, fargs=(xs,ys))#, interval=1000) 
    plt.show()
    print("Finished plotting, begin to save data to excel...")
    # storing data in csv
    store_to_csv()
    
if __name__ == "__main__":
    main()
