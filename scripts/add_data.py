# -----------------------------------------------------------
# AUTHOR:           Jacob Jameson
# Last Updated:     01/12/2023
# PURPOSE:          Append new drugs to raw data
# -----------------------------------------------------------


# Required packages -----------------------------------------

import numpy as np
import pandas as pd


def append_data(raw_data, new_data):
    '''
    Appends new data (if there is any) to raw data.
    '''
    return raw_data.append(new_data, ignore_index=True)


def go():
    new = '../data/new data/new data.xlsx'
    raw = '../data/raw data/raw data.xlsx'
    
    raw_data =  pd.read_excel(raw, sheet_name = 'raw data')
    new_data =  pd.read_excel(new, sheet_name = 'new data')
    
    if len(new_data) != 0:
        updated = raw_data.append(new_data, ignore_index = True)
        return updated
    
    else:
        print('ERROR: There was no data uploaded to add')