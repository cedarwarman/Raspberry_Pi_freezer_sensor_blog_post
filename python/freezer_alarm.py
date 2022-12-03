#!/usr/bin/env python3

import os
from datetime import datetime
import pandas as pd
from gspread_pandas import Spread
import yagmail

### Import sheet
def import_sheet(sheet_id):
    sheet = Spread(sheet_id)
    df = sheet.sheet_to_df(index=None)
    df['temp_c'] = df['temp_c'].astype(float)
    return df

### Import email addresses
def import_email_addresses(sheet_id):
    sheet = Spread(sheet_id)
    df = sheet.sheet_to_df(index=None)
    email_list = df[df.columns[0]].tolist()
    return email_list

### Open log file
def open_log_file():
    log_file_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), 
        "python_data", 
        "freezer_alarm_log.tsv"
    )
    if not os.path.exists(os.path.join(os.getcwd(), "python_data")):
        os.makedirs(os.path.join(os.getcwd(), "python_data"))

    try:
        f = open(log_file_path, 'a+')
        if os.stat(log_file_path).st_size == 0:
                f.write('date_time\tmessage\n')
        return f
    except:
        print("Failed to open log file")

### Append log file
def append_log_file(input_file_handle):
    try:
        input_file_handle.write(
            '{0}\t{1}\n'.format(
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'sent_alarm_email'
            )
        )
    except:
        print("Failed to update log file")

### Get the average temp over the last ten mins
def get_recent_average(input_df):
    tail = input_df.tail(5)
    average = tail['temp_c'].mean()
    return average

### Get the number of minutes since the last sensor reading
def last_read(input_df):
    last_row = input_df.tail(1)
    last_datetime = last_row.iloc[0][0] +  " " + last_row.iloc[0][1]
    last_datetime_string = datetime.strptime(last_datetime, "%Y-%m-%d %H:%M:%S")

    time_difference = datetime.now() - last_datetime_string
    time_diff_mins = time_difference.total_seconds() / 60

    return time_diff_mins

### Get time of last alarm email
def last_alarm():
    log_file = open_log_file()
    log_file.seek(0)
    lines = log_file.readlines()
    if len(lines) > 1:
        last_line = lines[-1].split("\t")
        date_string = last_line[0]
        datetime_string = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
        return datetime_string
    else:
        pass
        

### Send alarm email
def send_email(email_address_input, alarm_type):
    # Requires you to have initialized your username and password in yagmail:
    # yagmail.register('palanivelu.lab.freezer@gmail.com', 'password_here')
    # This stores your credentials in the local systen with Python keyring.
    #yag = yagmail.SMTP('palanivelu.lab.freezer')

    # For cron I just had to write the password in plain text. I think it's ok 
    # since it's an application password that can be revoked.
    yag = yagmail.SMTP('palanivelu.lab.freezer', 'PASSWORD_HERE')

    # Sends different emails for if it's a sensor down alert or a high 
    # temperature alert.
    if alarm_type == "temp":
        contents = [
            "Alert! The freezer has warmed a dangerous amount. See details here:",
            "https://viz.datascience.arizona.edu/freezer/"
        ]
        subject_line = "FREEZER ALARM"
    if alarm_type == "outage":
        contents = [
            "Alert! The freezer sensor is not functioning. See details here:",
            "https://viz.datascience.arizona.edu/freezer/"
        ]
        subject_line = "Freezer sensor down"


    # Sending the emails
    for email in email_address_input:
        print("Sending email to: ", email)
        yag.send(email, subject_line, contents)
        
    print("Sent email")

    # Append to log file that you've sent an email
    log_file = open_log_file()
    append_log_file(log_file)
    log_file.close()
    print("Appended log file")

### Main
def main():
    # Importing the sheet and converting to data frame
    df = import_sheet("1KpIEUuMpRD8q3DDNNUeJ1BqSztl_nAzA8DWtdTHFnVY")

    # Getting the average temp over the last 10 mins (readings every 2 mins)
    recent_average = get_recent_average(df)

    # Time since last sensor reading
    last_read_time = last_read(df)
    print("Minutes since last read: ", last_read_time)

    # Time since last alarm
    last_alarm_time = last_alarm()
    time_difference = datetime.now() - last_alarm_time
    time_diff_mins = time_difference.total_seconds() / 60
    print("Minutes since last alarm: ", time_diff_mins, "\n")

    # If the temp is greater than -65 and it has been longer than 
    # 30 minutes since it last sent an email then it will send an email. 
    if recent_average > -65 and time_diff_mins > 30:
        email_addresses = import_email_addresses("13alVNqXTpBhHDY2qK2oB4yfHmHJhnc47HlDJunqbhlc")
        send_email(email_addresses, "temp")

    # Sending an alert if the sensor is not reporting new data
    if last_read_time > 30 and time_diff_mins > 300:
        email_addresses = import_email_addresses("13alVNqXTpBhHDY2qK2oB4yfHmHJhnc47HlDJunqbhlc")
        send_email(email_addresses, "outage")
        

if __name__ == "__main__":
    main()

