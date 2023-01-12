# -----------------------------------------------------------
# AUTHOR:           Jacob Jameson
# Last Updated:     01/12/2023
# PURPOSE:          Append new drugs to raw data
# -----------------------------------------------------------


# Required packages -----------------------------------------

import numpy as np
import pandas as pd
import os


def append_data(raw_data, new_data):
    '''
    Appends new data (if there is any) to raw data.
    '''
    return raw_data.append(new_data, ignore_index=True)


def write_excel(filename,sheetname,dataframe):
    with pd.ExcelWriter(filename, engine='openpyxl', mode='a') as writer: 
        workBook = writer.book
        try:
            workBook.remove(workBook[sheetname])
        except:
            print("Worksheet does not exist")
        finally:
            dataframe.to_excel(writer, sheet_name=sheetname,index=False)
            writer.save()


def go():
    new = './data/new data/new data.xlsx'
    raw = './data/raw data/raw data.xlsx'
    
    raw_data =  pd.read_excel(raw, sheet_name = 'raw data')
    conversions =  pd.read_excel(raw, sheet_name = 'conversions')
    new_data =  pd.read_excel(new, sheet_name = 'new data')
    
    if len(new_data) != 0:
        raw_data = pd.concat([raw_data, new_data]).reset_index(drop=True)
        
        df = pd.DataFrame(columns=list(new_data.columns))
        df.to_excel(new, sheet_name = 'new data', index=False)
    
        with pd.ExcelWriter(raw) as writer:
            
            raw_data.to_excel(writer, sheet_name="raw data", index=False)
            conversions.to_excel(writer, sheet_name="conversions", index=False)
            print('raw data has been updated!')
            

        print('-----------------------------------------------/n')
        print('You have updated the data')
        print('-----------------------------------------------/n')
    
    else:
        print('-----------------------------------------------/n')
        print('ERROR: There was no data uploaded to add./n')
        print('Make sure you have added data to new data.xlsx.')
        print('-----------------------------------------------/n')
        
        
if __name__ == "__main__":
    go()
