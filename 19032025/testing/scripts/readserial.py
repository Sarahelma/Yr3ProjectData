import serial
from datetime import datetime
import csv

# Open a CSV file and set it up to receive comma-delimited input
# 
# step 1: name test file
# eg 50m_250kbps.csv

# eg 50m_1mbps.csv
# eg 50m_2mbps.csv
# we will do this for 0m, 50m, 100m, 150m, 200m, 250m
logging = open('antenna.csv', mode='a', newline='')
writer = csv.writer(logging, delimiter=",", escapechar=' ', quoting=csv.QUOTE_NONE)
#step 2 : click run, run without debug, allow to run for 15 seconds.
#step 3 : click stop button (red square) and go to data analysis.py
# go to line 54 and change name accordingly then click run
# do the same (step 1-3) for each test file
# if you need to check data sanity go to testgraphs.py
# change line 5 to filename and run

 
# Open the serial port connected to the Teensy
teensy = serial.Serial(port='COM8', baudrate=115200, timeout=0.01)
teensy.flushInput()

# Write a single character encoded in utf-8 to start communication
teensy.write(bytes('x', 'utf-8'))

while True:  
    # Read in data from Serial until \n (new line) received
    ser_bytes = teensy.readline()
    
    if ser_bytes:
        # Convert received bytes to text format
        decoded_bytes = ser_bytes.decode("utf-8").strip()
        print(decoded_bytes)
        
        # Retrieve current time
        current_time = datetime.now().strftime('%H:%M:%S')
        print(current_time)
        
        # If Arduino has sent a string "stop", exit loop
        if decoded_bytes == "stop":
            break
        
        # Write received data to CSV file
        writer.writerow([current_time] + decoded_bytes.split(','))

# Close port and CSV file to exit
teensy.close()
logging.close()
print("logging finished")
