# -----------------------------------------------------------
# AUTHOR:           Jacob Jameson
# Last Updated:     01/12/2023
# PURPOSE:          Prepare raw data
# -----------------------------------------------------------


# Required packages -----------------------------------------

import numpy as np
import pandas as pd
from numpy import nan


# Key for currency conversions ------------------------------

def create_dict_key(dataframe):
    '''
    '''
    conversion_key = dict()
    for year in dataframe.columns[1:]:
        values = list(dataframe[year])
        categories = list(dataframe['categories'])
        temp = dict()
        for tup in tuple(zip(categories, values)):
            temp[tup[0]] = tup[1]
        
        temp['USD'] = 1
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
    columns = list(raw_data.columns[fy_starts:])
    raw_data['Region'] = raw_data['Type']
        
    for index, row in raw_data.iterrows():
        currency = row['Currency']
        for year in columns:
            year_match = int(year[2:])
            infl = conversion_key[year_match]['Inflation Adjustment']
            curr = conversion_key[year_match][currency]
            row[year] = (float(row[year])/curr)*infl
            
        raw_data.loc[index] = row
        
    clean = raw_data
    clean['Source'] = clean['Source'].str.replace(" ", "")
    
    return clean[['Proper Name', 'Source'] + columns]

# Split strings -----------------------------------------------


def split_strings(string):
    '''
    '''
    new_string = '{'
    if string == '':
        return string
    for char in string:
        if char not in ['+', '-', '*']:
            new_string += char
        else:
            new_string += '}'
            new_string += char
            new_string += '{'
    
    new_string += '}'
    return new_string.replace("{0.5}", "0.5" )


def formulas(dataframe):
    '''
    '''
    dataframe["formula"] = dataframe["formula"].apply(split_strings)
    formula_key = dict()
    for _, row in dataframe.iterrows():
        formula = row['formula']
        formula_key[row['ID']] = formula

    return formula_key



# Evaluate formulas -------------------------------------------


def evaluate_helper(clean_dataframe):
    '''
    '''
    holder = dict()
    for index, row in clean_dataframe.iterrows():
        for year in clean_dataframe.columns[2:]:
            if year not in holder:
                holder[year] = {row['Source'] : row[year]}
            else:
                temp = holder.get(year)
                holder[year].update({row['Source'] : row[year]})
                
    return holder

    

def evaluate(eval_map, formula_key):
    '''
    '''
    return_dict = dict()
    for year in eval_map.keys():
        temp = eval_map.get(year)
        temp_dict = dict()
        for ID, formula in formula_key.items():
            if formula != '{Nan}':
                formula = formula.format(**temp)
                if formula != np.nan:
                    result = eval(formula)
                else:
                    result = formula
                temp_dict[ID] = result
            else:
                temp_dict[ID] = 'Nan'
                
        return_dict[year] = temp_dict
        
    return return_dict



def turn_into_dataframe(evaluated_key):
    '''
    '''
    counter = 0 
    for year, values in evaluated_key.items():
        data = []
        for key, amount in values.items():
            data.append([key, amount])
        df_temp = pd.DataFrame(data, columns = ['Product Name', year])
        if counter > 0:
            df = df.merge(df_temp, how='inner', on='Product Name')
        else: 
            df = df_temp

        counter += 1
        
    return df



# Produce Final Data -------------------------------------------


def check_string(x, string_list):
    for string in string_list:
        if string in x:
            return string
    return None



def merge_final_clean(raw_dataframe, evaluated_key):
    '''
    '''
    cols = ['Proper Name', 'Generic Name', 
            'Medicare Spend', 'Original Manufacturer', 
            'Application', 'Approval Date', 'Year']
    
    pnames = list(raw_dataframe['Proper Name'])
    temp = raw_dataframe[cols].drop_duplicates()
    
    evaluated_key["Proper Name"] = evaluated_key["Product Name"].apply(lambda x: check_string(x, pnames))
    
    return temp.merge(evaluated_key, how='left', on='Proper Name')



def reformat_final(dataframe):
    '''
    '''
    data = []
    years = dataframe.columns[8:]
    other_info = dataframe.columns[:8]
    
    for index, row in dataframe.iterrows():
        new_data = list(row[other_info].values)
        for year in years:
            if row[str(year)] != 0:
                new_data.append(row[str(year)])
                
        data.append(new_data)
        
    longest_list = max(data, key=lambda x: len(x))
    num_years = len(longest_list) - 8
    year_cols = [f't{i}' for i in range(num_years)]
    cols = list(other_info) + year_cols
        
    data = pd.DataFrame(data, columns = cols).fillna(np.nan)
            
    return data

# GO --------------------------------------------------------------

def go():
    raw = './data/raw data/raw data.xlsx'
    
    key = pd.read_excel(raw, sheet_name = 'conversions')
    conversion_key = create_dict_key(key)
    
    print('20%')
    df = pd.read_excel(raw, sheet_name = 'raw data')
    clean = adjustments(df, conversion_key)
    print('40%')
    key = pd.read_excel(raw, sheet_name = 'dictionary')
    formula_key = formulas(key)
    eval_map = evaluate_helper(clean)
    print('60%')
    evaluated_key = evaluate(eval_map, formula_key)
    evaluated_key = turn_into_dataframe(evaluated_key)
    print('80%')
    final = merge_final_clean(df, evaluated_key)
    final = reformat_final(data)

    final.to_excel('./data/clean data/clean data.xlsx', index=False)
            
    print('-----------------------------------------------')
    print('You have cleaned the data. You can view in the clean data folder!')
    print('-----------------------------------------------')
    
        
        
if __name__ == "__main__":
    go()


