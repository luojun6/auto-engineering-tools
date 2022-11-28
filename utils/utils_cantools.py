import os, sys
current_dir = os.path.dirname(__file__)
root_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.insert(0, root_dir)

import pandas as pd
import cantools

from utils.files_mgmt import get_file_by_suffix


can_dbc_filtered_cols = [
    'name',
    'scale',
    'offset',
    'is_float',
    'minimum',
    'maximum',
    'choices',
    'start',
    'length',
    'byte_order',
    'is_signed',
    'initial',
    'unit',
    'receivers',
    'comments'
]

def parse_can_dbc_to_df(dbc):
    
    df = pd.DataFrame()
    for msg in dbc.messages:
        signal_attr = [[getattr(signal, attr) for attr in can_dbc_filtered_cols] for signal in msg.signals]
        temp_df = pd.DataFrame(signal_attr, columns=can_dbc_filtered_cols)
        temp_df['message_name'] = msg.name
        temp_df['message_id'] = msg.frame_id
        
        df = pd.concat([df, temp_df])
    df.reset_index(drop=True, inplace=True)
    
    return df
    
def get_dbcs_from_local(dir_name=None, strict=True):
    can_dbc_paths_hash = get_file_by_suffix(suffix_name='dbc', dir_name=dir_name)
    dbc_df = pd.DataFrame()
    
    for dbc_name in can_dbc_paths_hash.keys():
        temp_dbc = cantools.database.load_file(can_dbc_paths_hash[dbc_name], strict=strict)
        temp_dbc_df = parse_can_dbc_to_df(temp_dbc)
        temp_dbc_df['dbc_name'] = dbc_name
        dbc_df = pd.concat([dbc_df, temp_dbc_df])
        
    return dbc_df
    
    
if __name__ == "__main__":
    from utils.files_mgmt import out_dir
    dbc_dir = r'res'
    dbc = get_dbcs_from_local(dir_name=dbc_dir)
    print(dbc)
    out_path = os.path.join(out_dir, 'tesla_can_dbc.csv')
    dbc.to_csv(out_path, index=None)