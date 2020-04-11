import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'cytomod', 'otherTools'))
import tools
import warnings
from . import import_data
from .. import server_tools
import numpy as np
import pandas as pd
warnings.filterwarnings('ignore')
warnings.simplefilter('ignore')
import logging


def set_data(parameters):
    parameters = set_path(parameters)
    tools.create_folder(parameters.path_files)
    if check_input(parameters):
        # todo: inser seed by configuration  - > os.environ.get("SEED")
        parameters.cy_data = import_data.make_cyto_data(parameters)
        parameters.patient_data = import_data.make_patients_data(parameters)
        parameters.patient_data, parameters.cy_data, parameters = log_transform(parameters, parameters.cy_data, parameters.patient_data)
        logging.warning('finished set_data')
        return parameters
    # Todo: dont forget to delete file!!!!
    return False


def set_path(parameters):
    parameters.path_files = os.path.join('app/static', parameters.name_data)
    parameters.data_files = os.path.join(parameters.path_files, 'data_files')
    parameters.paths = {
                    'overview': os.path.join(parameters.path_files, 'overview'),
                  'clustering_abs': os.path.join(parameters.path_files, 'clustering_abs'),
                  'clustering_adj': os.path.join(parameters.path_files, 'clustering_adj'),
                  'correlation_figures_abs': os.path.join(parameters.path_files, 'correlation_figures_abs'),
                  'correlation_figures_adj': os.path.join(parameters.path_files, 'correlation_figures_adj'),
                  'outcome_abs': os.path.join(parameters.path_files, 'outcome_abs'),
                  'outcome_adj': os.path.join(parameters.path_files, 'outcome_adj'),
                  }
    server_tools.create_folders(parameters.paths)
    return parameters


def check_input(parameters):
    assert type(parameters.name_data) is str
    assert type(parameters.name_compartment) is str
    assert type(parameters.log_transform) is bool
    assert type(parameters.max_testing_k) is int
    assert type(parameters.outcomes) is list
    assert type(parameters.covariates) is list
    if parameters.outcomes != ['']:
        file_name = tools.read_excel(os.path.join(parameters.path_files, 'data_files_names.xlsx')).get_value(1, 0)
        # TODO: INSERT CHECK FILE
        path = os.path.join(parameters.data_files, file_name)
        for col_name in parameters.outcomes + parameters.covariates + parameters.log_column_names:
            assert type(col_name) is str
            if col_name != '':
                tools.assert_column_exists_in_path(file_path=path, col_name=col_name)
    return True


def log_transform(parameters, cy_data, patient_data):
    if parameters.log_transform:
        cy_data = _log_cytokines(parameters, cy_data)
    if parameters.log_column_names != [''] and parameters.outcomes != ['']:
        patient_data, parameters = _log_covariates(parameters, patient_data)
    return patient_data, cy_data, parameters


def _log_covariates(parameters, patient_data):
    # log transform args.log_column_names
    if parameters.log_column_names != [''] and parameters.outcomes != ['']:
        for col_name in parameters.log_column_names + parameters.outcomes:
            if(_is_continues(col_name, patient_data)):
                new_col_name = 'log_' + col_name  # log transform variable
                patient_data[col_name] = patient_data[col_name][patient_data[col_name] != 0]
                patient_data[new_col_name] = np.log10(patient_data[col_name]) # replace column with new log transformed column
                # if col_name in parameters.outcomes:
                #     parameters.outcomes.remove(col_name)
                #     parameters.outcomes.append(new_col_name)
                if col_name in parameters.covariates:
                    parameters.covariates.remove(col_name)
                    parameters.covariates.append(new_col_name)
    return patient_data, parameters


def _is_continues(col_name, df):
    return not np.isin(df[col_name].dropna().unique(), [0, 1]).all()


def _log_cytokines(parameters, cy_data):
    if parameters.log_transform and parameters.luminex:
        cy_data = np.log10(cy_data.astype(float))
        # TODO: use cy_data.dtypes to automatically log all data according to types
    if parameters.log_transform and not parameters.luminex:
        cy_data = np.log10(cy_data)
    return cy_data
