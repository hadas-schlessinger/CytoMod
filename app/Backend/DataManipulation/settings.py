import os
import io
import sys
sys.path.append(os.path.join(os.getcwd(), 'cytomod', 'otherTools'))
import tools
from .. import server_tools
import warnings
import app
import csv
from . import import_data
import numpy as np
warnings.filterwarnings('ignore')
warnings.simplefilter('ignore')
import logging


def set_data(parameters):
    set_path(parameters)
    if check_input(parameters, parameters.paths):
        parameters.seed = 1234
            #os.environ.get("SEED") #by configuration!!!!!!!!!
       # data_path = server_tools.save_data_on_local_path(cy_data)
        parameters.cy_data = import_data.make_cyto_data(parameters)
        parameters.patient_data = import_data.make_patiants_data(parameters)
        parameters.patient_data, parameters.cy_data = log_transform(parameters, parameters.cy_data, parameters.patient_data)
        logging.warning('finished set_data')
        return parameters
    # dont forget to delete file!!!!
    return False


def set_path(parameters):
    parameters.path_files = os.path.join('app/static', 'data_files')

    parameters.paths = {'files': os.path.join('app/static', 'data_files'),
                  'data': os.path.join('app/static', 'data_files', 'data'),
                  'gap_statistic': os.path.join('app/static'),
                  'clustering': os.path.join('app/static'),
                  'clustering_info': os.path.join('app/static'),
                  'clustering_figures': os.path.join('app/static'),
                  'correlation_figures': os.path.join('app/static'),
                  'association_figures': os.path.join('app/static'),
                # 'data': os.path.join('app/static', 'data_files', 'data'),
                # 'gap_statistic': os.path.join('app/static', 'data_files', 'output', 'gap_statistic'),
                # 'clustering': os.path.join('app/static', 'data_files', 'output', 'clustering'),
                # 'clustering_info': os.path.join('app/static', 'data_files', 'output', 'clustering', 'info'),
                # 'clustering_figures': os.path.join('app/static', 'data_files', 'output', 'clustering',
                #                                    'figures'),
                # 'correlation_figures': os.path.join('app/static', 'data_files', 'output', 'correlations'),
                # 'association_figures': os.path.join('app/static', 'data_files', 'output', 'associations'),
                  }
    #server_tools.create_folders(parameters.paths)


def check_input(parameters, paths):
    assert type(parameters.name_data) is str
    assert type(parameters.name_compartment) is str
    assert type(parameters.log_transform) is bool
    assert type(parameters.max_testing_k) is int
    assert type(parameters.outcomes) is list
    assert type(parameters.covariates) is list

    for col_name in parameters.outcomes + parameters.covariates + parameters.log_column_names:
        assert type(col_name) is str
        [tools.assert_column_exists_in_path(os.path.join(paths['data'],
                                                         tools.read_excel(os.path.join('app/static', 'data_files_names.xlsx')).get_value(1, 0)), col_name) if col_name != '' else ''] # change to other things

    return True


def log_transform(parameters, cy_data, patient_data):
    print(cy_data)
    cy_data = np.log10(cy_data.astype(float)) if parameters.log_transform else cy_data

    # log transform cytokines and args.log_column_names
    if parameters.log_column_names != [''] and parameters.outcomes != ['']:
        for col_name in parameters.log_column_names:
            new_col_name = 'log_' + col_name

            # log transform variable
            patient_data[new_col_name] = np.log10(patient_data[col_name])

            # replace column with new log transformed column
            if col_name in parameters.covariates:
                parameters.covariates.remove(col_name)
                parameters.covariates.append(new_col_name)

    return patient_data, cy_data
