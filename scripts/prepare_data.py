# -----------------------------------------------------------
# AUTHOR:           Jacob Jameson
# Last Updated:     01/12/2023
# PURPOSE:          Prepare raw data
# -----------------------------------------------------------


# Required packages -----------------------------------------

import numpy as np
import pandas as pd


# Key for currency conversions ------------------------------

def create_dict_key(dataframe):
    '''
    Creates a currency key
    '''
    conversion_key = dict()
    for year in dataframe.columns[1:]:
        values = list(dataframe[year])
        categories = list(dataframe['categories'])
        temp = dict()
        for tup in tuple(zip(categories, values)):
            temp[tup[0]] = tup[1]
        
        conversion_key[year] = temp
            
    return conversion_key


# Adjust all currencies --------------------------------------


def adjustments(raw_data, conversion_key, fy_starts=13):
    '''
    Takes inputs of raw_data and conversion key and
    converts to real money terms.
    
    Inputs:
        raw_data: pandas dataframe of raw data Excel
        raw_data: pandas dataframe of raw data Excel
        
    Outputs:
        adjusted_data: pandas dataframe of adjusted data
    '''
    columns = raw_data.columns[fy_starts:]
    raw_data['Region'] = raw_data['Type']
    
    for index, row in raw_data.iterrows():
        currency = row['Currency']
        for year in columns:
            year_match = int(year[3:])
            infl = conversion_key[year_match]['Inflation Adjustment']
            curr = conversion_key[year_match][currency]
            row[year] = (float(row[year])/curr)*infl
        
        if 'US' in row['Region']:
            row['Region'] = 'US'
        elif 'Total' in row['Region']:
            row['Region'] = 'Total'
        else:
            row['Region'] = 'ExUS'
            
        raw_data.loc[index] = row
        
    clean = raw_data 
    
    return clean

# Split strings -----------------------------------------------


def split_strings(string):
    '''
    '''
    new_string = '{'
    for char in string:
        if char not in ['+', '-', '*']:
            new_string += char
        else:
            new_string += '}'
            new_string += char
            new_string += '{'
            
    new_string += '}'
    
    return new_string



def formulas(dataframe):
    '''
    '''
    dataframe["formula"] = dataframe["formula"].apply(split_strings)
    formula_key = dict()
    for _, row in dataframe.iterrows():
        formula = row['formula']
        key = row['Proper Name']
        if key not in formula_key:
            formula_key[key] = [{row['ID']:formula}]
        else:
            dict_list = formula_key.get(key)
            formula_key[key] = dict_list + [{row['ID']:formula}]
    
    return formula_key



# Summarize by drug -------------------------------------------


def summary(clean_data, fy_starts=13):
    '''
    Get from array 2 to array 3
    '''
    # First simulate the dataframr
    data = []
    names = list(clean_data['Proper Name'].unique())
    for name in names:
        data.append([name, 'US'])
        data.append([name, 'WW'])
        data.append([name, 'ExUS'])
    
    data = pd.DataFrame(data, columns = ['Proper Name', 'Region']) 
    
    # Add with original data to create empty rows
    years = clean_data.columns[fy_starts:]
    clean = clean_data.groupby(['Proper Name', 'Region'], as_index=False)[years].sum()
    
    clean = clean.merge(data, how='right', on=['Proper Name', 'Region'])
    
    # Place holder for summary helper
    
    return clean





