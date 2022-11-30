from cmath import sin
import os, sys
current_dir = os.path.dirname(__file__)
root_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.insert(0, root_dir)

import datetime
import pickle
import pandas as pd
from utils.loggers import Logger
from utils.files_mgmt import load_words, out_dir

logger = Logger("utils_pandas")

COL_FILE_NAME= 'file_name'


def to_1D(series):
    return pd.Series([x for _list in series for x in _list])

def merge_tables_from_excel_files(excel_hash_table: dict, col_file_name=COL_FILE_NAME, drop_sheets_names=None):
    if type(excel_hash_table) is not dict:
        raise TypeError(f"Invalid input excel_hash_table type {type(excel_hash_table)}.")
    
    df = pd.DataFrame()
    excel_file_len = len(excel_hash_table)
    count = 0
    for excel in excel_hash_table.keys():
        count += 1
        logger.debug(f"Parsing {excel} with completion: {count}/{excel_file_len}.")
        try:
            temp_xl = pd.ExcelFile(excel_hash_table[excel])
            for sheet in temp_xl.sheet_names:
                if drop_sheets_names:
                    if sheet not in drop_sheets_names:
                        temp_table = temp_xl.parse(sheet)
                        temp_table[col_file_name] = excel
                        df = pd.concat([df, temp_table])
                        
                else:
                    temp_table = temp_xl.parse(sheet)
                    temp_table[col_file_name] = excel
                    df = pd.concat([df, temp_table])
                        
        except Exception as e:
            logger.error(e)
            
    return df


def fetch_signals_from_merged_table(merged_table: pd.DataFrame, 
                                    invalid_signal_words=None, 
                                    signal_re=r'[a-zA-Z][a-zA-Z][a-zA-Z][a-zA-Z][a-zA-Z]+'):
    if type(merged_table) is not pd.DataFrame:
        raise TypeError(f"Invalid input merged_table type {type(merged_table)}.")
    
    merged_table.fillna(value='', inplace=True) # Otherwise it can not use string function
    parsed_table = pd.DataFrame()
    
    for col in merged_table:
        parsed_table[col] = merged_table[col].str.findall(signal_re)
    parsed_table.fillna(value='', inplace=True) # Otherwise it can not use string function
    
    words_series = pd.Series()
    for col in parsed_table.columns:
        temp_series = pd.Series(to_1D(parsed_table[col]).unique())
        words_series = pd.concat([words_series, temp_series])
        
    unique_words = pd.Series(words_series.unique())
    
    # Remove regular english words
    en_words = load_words() # from utilities.files
    en_words_series = pd.Series(en_words).str.lower()
    raw_signals = unique_words[~unique_words.str.lower().isin(en_words_series)].copy()
    
    if invalid_signal_words:
        raw_signals = raw_signals[~raw_signals.isin(invalid_signal_words)]
        
    return invalid_signal_words

def get_file_name_by_keyword(df: pd.DataFrame, keyword: str, file_name_col=COL_FILE_NAME):
    _df = df.fillna('').copy() 
    for col in _df.columns:
        if _df[col].str.contains(keyword).sum() > 0:
            found = list(df.loc[df[col].str.contains(keyword, na=False), 
                                file_name_col].unique())
            logger.debug(f"Found {found} in {file_name_col}.")
            return found
        
    
def hash_signal_to_file_name(search_df: pd.DataFrame, 
                             target_signal_list: list,
                             source_hash_pickle_path=None, 
                             destination_hash_pickle_path=None, 
                             research_none_signal=False):
    if source_hash_pickle_path:
        with open(source_hash_pickle_path, "rb") as s:
            hash_table = pickle.load(s)
    else:
        hash_table = dict()
            
    counts = len(target_signal_list)
    i = 0
    
    for signal in target_signal_list:
        i += 1
        logger.debug(f"Proccessing {signal} with completion: {i}/{counts}.")
        if signal not in hash_table.keys():
            file_name = get_file_name_by_keyword(search_df, signal)
            if file_name:
                hash_table[signal] = file_name
            else:
                hash_table[signal] = None
        else:
            if research_none_signal:
                file_name = get_file_name_by_keyword(search_df, signal)
                if file_name:
                    hash_table[signal] = file_name
                    logger.debug(f"Added {file_name} to signal: {signal}.")
                    
    if not destination_hash_pickle_path:
        t_now = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M")
        destination_hash_pickle_path = os.path.join(out_dir, f'signal_to_file_name_{t_now}.pickle')
        
    with open(destination_hash_pickle_path, "wb") as d:
        pickle.dump(hash_table, d, pickle.HIGHEST_PROTOCOL)
        
    return hash_table
    
    
def check_signal_typo(signal: str, signals_list: list):
    for s in signals_list:
        if (signal.lower() in s.lower()) or (s.lower() in signal.lower()):
            return s
    
if __name__ == "__main__":
    from utils.files_mgmt import get_file_by_suffix
    
    excel_files = get_file_by_suffix('xlsx', 'res')
    # print(excel_files)
    tables = merge_tables_from_excel_files(excel_files)
    # print(tables)
    signal_list = ['Alfred', 'Tullos']
    
    signal_to_file_name = hash_signal_to_file_name(tables, signal_list)
    print(signal_to_file_name)