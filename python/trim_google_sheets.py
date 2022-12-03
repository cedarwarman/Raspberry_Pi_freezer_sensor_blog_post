#!/usr/bin/env python3

import os
import glob
import argparse
import pandas as pd
from gspread_pandas import Spread

### Setting up arguments
parser = argparse.ArgumentParser(description='Trim sheets to most recent x days')
parser.add_argument('-p',
                    '--path',
                    type=str,
                    default='../url/',
                    help='Path to Google Sheet URL code file')
args = parser.parse_args()

### Make URL dictionary
def make_url_dict(dir_path):
    url_dict = {}
    for file_path in glob.glob(dir_path + '*'):
        with open(file_path, 'r') as url_file:
            # Getting the file name
            file_string = os.path.basename(file_path)
            file_string = os.path.splitext(file_string)[0]
            nest_dict = {}
            for line in url_file:
                # Adding values to the nested dictionary
                (key, value) = line.split()
                nest_dict[key] = value
            # Adding the nested dictionary to the main dictionary
            url_dict[file_string] = nest_dict
    return(url_dict)

### Trim sheet
def trim_sheet(days, sheet_id):
    # Setting dates
    current_date = pd.Timestamp('today').floor('D')
    start_date = current_date - pd.Timedelta(days, unit='D')
    print(current_date)
    print(start_date)

    # Opening a spreadsheet
    input_sheet = Spread(sheet_id)

    # Converting to dataframe
    df = input_sheet.sheet_to_df(index=None)
    print(df)

    # Converting date column to datetime type
    df.loc[:,'date'] = pd.to_datetime(df.loc[:,'date'], format='%Y-%m-%d')

    # Subsetting dataframe to past x days
    df = df[(df['date'] > start_date) & (df['date'] <= current_date)]
    print(df)

    # Converting back to string for upload (the apostrophe is for google sheets
    # to not convert it back to a date, because this breaks the R script).
    df.loc[:,'date'] = "'" + df.loc[:,'date'].dt.strftime('%Y-%m-%d')

    # Adding apostrophe to time for google sheets

    df.loc[:,'time'] = "'" + df.loc[:,'time']

    print(df.dtypes)

    # Uploading the new sheet
    input_sheet.df_to_sheet(df, 
        index=False, 
        replace=True)


### Main
def main():
    url_dict = make_url_dict(args.path)
    #print(url_dict)
    for nest_dict in url_dict.values():
        print(nest_dict)
        for key, sheet_id in nest_dict.items():
            print("Key is: " + key)
            if key == 'week':
                print(key)
                print(sheet_id)
                trim_sheet(7, sheet_id)
            elif key == 'month':
                print(key)
                print(sheet_id)
                trim_sheet(30, sheet_id)
            else:
                print("pass")
                pass

if __name__ == "__main__":
    main()

