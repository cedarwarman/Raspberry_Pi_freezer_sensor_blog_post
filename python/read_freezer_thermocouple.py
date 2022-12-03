#!/usr/bin/env python3

# Data reading adapted from:
# https://learn.adafruit.com/adafruit-max31856-thermocouple-amplifier/python-circuitpython

import os
import time
import glob
import board
import gspread
import digitalio
import adafruit_max31856

# Import LED libraries
import re
import time

from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.virtual import viewport
from luma.core.legacy import text, show_message
from luma.core.legacy.font import proportional, CP437_FONT, TINY_FONT, SINCLAIR_FONT, LCD_FONT

### Open Google Sheet URLs file
# The url file is a tsv file with key value pairs as follows:
# all   Google_spreadsheet_ID
# week  Google_spreadsheet_ID
# month Google_spreadsheet_ID
def open_url_files(dir_path, sensor_list):
    url_dict = {}
    for file_path in glob.glob(dir_path + '*'):
        print("working on " + file_path)
        # Getting the file name
        file_string = os.path.basename(file_path)
        file_string = os.path.splitext(file_string)[0]
        # Checking to see if it's on the sensor_list
        print("file_string: " + file_string)
        #print("sensor_list: " + sensor_list)
        if any(sensor_string in file_string for sensor_string in sensor_list):
            print("Matched string")
            with open(file_path, 'r') as url_file:
                nest_dict = {}
                for line in url_file:
                    # Adding values to the nested dictionary
                    (key, value) = line.split()
                    nest_dict[key] = value
                # Adding the nested dictionary to the main dictionary
                url_dict[file_string] = nest_dict
        else:
            print("no match")
    return(url_dict)

### Append to Google sheet
def append_google_sheet(input_list, sheet_key):
    try:
        # Setting up the service account info
        # (/home/pi/.config/gspread/service_account.json)
        gc = gspread.service_account()

        # Reading the sheet
        sheet = gc.open_by_key(sheet_key).sheet1

        # Writing the data
        append_list = input_list

        sheet.append_row(append_list)
    except Exception as e: print(repr(e))

### Make a sensor
def create_sensor():
    # Create sensor object
    spi = board.SPI()
    
    # Allocate CS pin and set direction
    cs = digitalio.DigitalInOut(board.D5)
    cs.direction = digitalio.Direction.OUTPUT

    # Make it work with type T thermocouple
    tc_type = adafruit_max31856.ThermocoupleType.T
    
    # Create thermocouple object
    thermocouple = adafruit_max31856.MAX31856(spi,cs,tc_type)

    return(thermocouple)
    
    # Print temperature
    #while True:
    #	print(thermocouple.temperature)
    #    time.sleep(1.0)


### Make an LED screen
def create_led_device():
    # create matrix device (CS pin CE1 set in device argument)
    serial = spi(port=0, device=1, gpio=noop())
    device = max7219(serial, cascaded=4, block_orientation=90,
                     rotate=0, blocks_arranged_in_reverse_order=True)
    return(device)

if __name__ == "__main__":
    # Setting up the thermocouple
    thermocouple = create_sensor()

    # Setting up the display
    device = create_led_device()

    # Loading the file with the Google sheet IDs
    sheet_ids = open_url_files('/home/pi/git/Raspberry_Pi_freezer_sensor_blog_post/url/', ['freezer_1'])

    # Showing the temp on the display
    #show_message(device, msg, fill="white", font=proportional(CP437_FONT))

    # Opening message
    msg = "Thermocouple active"
    show_message(device, msg, fill="white", font=proportional(LCD_FONT), scroll_delay=0.05)

    # Temperature loop

    # Flag for uploading the data (only every 5 minutes, flag keeps it from 
    # uploading a bunch of times when the minute is divisible by 5
    uploaded_flag = False

    while True:
        # This comes from copying code from the temp/humidity sensors, 
        # but might be useful if I ever have more than 1 thermocouple
        for sensor_location, sensor_dict in sheet_ids.items():
            # Getting the temp
            temp_string = str(format(thermocouple.temperature, '.4f'))
            print(temp_string)

            # Displaying the temp on the LED matrix
            with canvas(device) as draw:
                text(draw, (0,0), temp_string, fill="white", font=proportional(LCD_FONT))

            # Uploading the data
            if (not (int(time.strftime('%M', time.localtime())) % 3)) and not uploaded_flag:
                read_time = time.localtime()
                upload_list = [time.strftime('%Y-%m-%d', read_time), time.strftime('%H:%M:%S', read_time)[:-2] + "00", temp_string]
                append_google_sheet(upload_list, sensor_dict.get('all'))
                append_google_sheet(upload_list, sensor_dict.get('week'))
                append_google_sheet(upload_list, sensor_dict.get('month'))

                uploaded_flag = True

            # Resets the uplaoded flag if the minute divisible by 3 has passed
            if not ((int(time.strftime('%M', time.localtime())) - 1) % 3):
                uploaded_flag = False

            time.sleep(3)

