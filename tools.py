import pandas as pd
import os
import dill

__all__ = ['Object',
           'read_excel',
           'create_folder',
           'write_DF_to_excel',
           'assert_column_exists_in_path',
           ]


class Object(object):
    pass


def read_excel(path, sheet=0, indexCol=None, nrows=None, skiprows=[], header = 0):
    df = pd.read_excel(path, sheet_name=sheet, skiprows=skiprows, index_col=indexCol, nrows=nrows, header=header)
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
        raise Exception('assert_column_exists_in_path: Fix column name and re-run script.')


def write_to_dill(path, variable):
    with open(path, 'wb') as d:
        dill.dump(variable, d, protocol=-1)


def read_from_dill(path):
    with open(path, 'rb') as fh:
        ans = dill.load(fh)
    return ans
