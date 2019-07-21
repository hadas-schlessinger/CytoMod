import pandas as pd
import os

__all__ = ['Object',
           'read_excel',
           'create_folder',
           'write_DF_to_excel',
           'assert_column_exists_in_path',
           ]

class Object(object):
    pass

def read_excel(path, sheet=0, indexCol=None, nrows=None):
    df = pd.read_excel(path, sheet_name=sheet, index_col=indexCol, nrows=nrows)
    return df

def create_folder(path):
    if (not os.path.exists(path)):
        os.makedirs(path)

def write_DF_to_excel(path, dataframe):
    if type(dataframe)==dict:
        dataframe = pd.Series(dataframe, name='value').to_frame()

    writer = pd.ExcelWriter(path)
    dataframe.to_excel(writer, 'df')
    writer.save()

def assert_column_exists_in_path(file_path, col_name, sheet=0):
    df = read_excel(file_path, sheet=sheet, nrows=3)

    if col_name not in df.columns:
        print('Column', col_name, 'does not exist')
        print('in file', file_path, '.')
        print('Fix column name and re-run script.')
        exit()