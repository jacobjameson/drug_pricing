# -----------------------------------------------------------
# AUTHOR:           Jacob Jameson
# Last Updated:     02/19/2023
# PURPOSE:          Prepare raw data
# -----------------------------------------------------------


# Required packages -----------------------------------------

import numpy as np
import pandas as pd
from numpy import nan
import sys


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
            if currency == 'Yen':
                row[year] = (float(row[year])/(1000/curr))*infl
            else:
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
        if char not in ['+', '-', '*', '/', '(', ')']:
            new_string += char
        else:
            new_string += '}'
            new_string += char
            new_string += '{'
    
    new_string += '}'
    new_string = new_string.replace("{}", "" )
    
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
                    try:
                        result = eval(formula)
                    except ZeroDivisionError:
                        result = 0
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
    cols_y = ['FY2007', 'FY2008', 'FY2009', 'FY2010', 'FY2011',
       'FY2012', 'FY2013', 'FY2014', 'FY2015', 'FY2016', 'FY2017', 'FY2018',
       'FY2019', 'FY2020', 'FY2021', 'FY2022', 'FY2023', 'FY2024', 'FY2025',
       'FY2026', 'FY2027', 'FY2028', 'FY2029', 'FY2030', 'FY2031', 'FY2032',
       'FY2033', 'FY2034', 'FY2035', 'FY2036', 'FY2037', 'FY2038']
    
    cols = ['Proper Name', 'Generic Name', 
            'Medicare Spend', 'Original Manufacturer', 
            'Application', 'Approval Date', 'Year']
    
    pnames = list(raw_dataframe['Proper Name'])
    temp = raw_dataframe[cols].drop_duplicates()
    
    evaluated_key["Proper Name"] = evaluated_key["Product Name"].apply(lambda x: check_string(x, pnames))
    
    final = temp.merge(evaluated_key, how='left', on='Proper Name')

    for col in cols_y:
        final = final.rename(columns={col: col[2:]})
    
    return final



def reformat_final(dataframe):
    '''
    '''
    data = []
    years = dataframe.columns[8:]
    other_info = dataframe.columns[:8]
    
    for index, row in dataframe.iterrows():
        new_data = list(row[other_info].values)
        for year in years:
            #if row[str(year)] != 0:
                #new_data.append(row[str(year)])
            if int(year) >= row['Year']:
                new_data.append(row[str(year)])
                
        data.append(new_data)
        
    longest_list = max(data, key=lambda x: len(x))
    num_years = len(longest_list) - 8
    year_cols = [f't{i}' for i in range(1, num_years+1)]
    cols = list(other_info) + year_cols
        
    data = pd.DataFrame(data, columns = cols)
    data[year_cols] = data[year_cols].astype(float)
    data['t31'] = np.nan

    return data.fillna(np.nan)



def find_last_valid(row):
    last_valid = row.last_valid_index()
    return (last_valid, row[last_valid])

def pro_rate(dataframe):
    '''
    '''
    last_values = dataframe.apply(find_last_valid, axis=1).tolist()
    
    end_of_year = pd.to_datetime(dataframe['Approval Date'].dt.year.astype(str) + '-12-31')
    days_remaining = (end_of_year - dataframe['Approval Date']).dt.days
    dataframe['percent_remaining'] = (days_remaining / 365)
    dataframe['percent_missing'] = 1 - dataframe['percent_remaining']
    
    for year in range(1,31):
        var = 't' + str(year)
        var1 = 't' + str(year+1)
        dataframe[var] = (dataframe[var]) + (dataframe[var1]*dataframe['percent_missing'])
        dataframe[var1] -= (dataframe[var1]*dataframe['percent_missing'])
    
    for i, (col, val) in enumerate(last_values):
        dataframe.loc[dataframe.index[i], col] = val
    
    return dataframe




def apply_discount(dataframe, discount_rate=0.1):
    '''
    '''
    for year in range(1,31):
        var = 't' + str(year)
        dataframe[var] = dataframe[var]/(1+discount_rate)**(year-0.5)
        
    return dataframe



# Produce Final Data -------------------------------------------


def create_summary(subset, dataframe, approval_years):
    '''
    '''
    dataframe = dataframe[dataframe['Product Name'].str.contains("WW")]
    
    if subset != 'All':
        dataframe = dataframe[dataframe['Application'] == subset]
    if approval_years != ['All']:
        dataframe = dataframe[(approval_years[0] >= dataframe['Year'].astype('int32')) & 
                  (dataframe['Year'].astype('int32') <=  approval_years[1])]
    
    year_cols = [f't{i}' for i in range(1, 21)]
    final = pd.DataFrame(dataframe[year_cols].describe())
    final = final.reset_index().rename(columns={'index': 'stats'})
    temp = pd.DataFrame(dataframe[year_cols].sum()).transpose().assign(stats=['Gross Revenue'])
    final = pd.concat([final, temp])
    
    
    final['sum of annual revenues, years 1-9'] = dataframe[year_cols[:9]].sum().sum()
    final['sum of annual revenues, years 10-13'] = dataframe[year_cols[10:13]].sum().sum()
    final['sum of annual revenues, years 14-20'] = dataframe[year_cols[14:20]].sum().sum()
    final['sum of ALL annual revenues, years 1-20'] = dataframe[year_cols].sum().sum()
    
    return final


def clean_summary(dataframe, approval_years):
    '''
    '''
    
    alldrugs = create_summary('All', dataframe, approval_years)
    nda = create_summary('NDA', dataframe, approval_years)
    bla = create_summary('BLA', dataframe, approval_years)
    
    clean = pd.concat([alldrugs, nda, bla])
    clean = clean.assign(Class=['All']*9 + ['NDA']*9 + ['BLA']*9)
    
    # select the subset of columns to check for duplicates
    cols_to_check = ['sum of annual revenues, years 1-9', 
                     'sum of annual revenues, years 10-13', 
                     'sum of annual revenues, years 14-20', 
                     'sum of ALL annual revenues, years 1-20',
                     'Class']

    # replace duplicate values with blank
    clean.loc[clean.duplicated(cols_to_check), cols_to_check] = np.nan 
    clean = clean.fillna("")
    clean.insert(0, 'Class', clean.pop('Class'))
    
    return clean

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
    final = reformat_final(final)
    final = pro_rate(final)
    final = apply_discount(final, float(sys.argv[1]))

    final.to_excel('./data/clean data/clean data.xlsx', index=False)
            
    print('-----------------------------------------------')
    print('You have cleaned the data. You can view in the clean data folder!')
    print('-----------------------------------------------')
    
    print('-----------------------------------------------')
    print('Producing Summary Statistics')
    print('-----------------------------------------------')
    
    clean = clean_summary(final, ['All'])
    clean.to_excel('./data/clean data/summary stats_discount_' + sys.argv[1] + '.xlsx', index=False)
        
if __name__ == "__main__":
    go()


