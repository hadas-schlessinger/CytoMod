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
       # cy_data = server_tools.read_file()  # needs to be created
       # data_path = server_tools.save_data_on_local_path(cy_data)
        data = tools.Object
        data.cy_data = import_data.make_cyto_data(parameters)
        data.patient_data = import_data.make_patiants_data(parameters)
        log_transform(parameters, parameters.cy_data, parameters.patient_data)
        print('finished set_data')
        return parameters
    # dont forget to delete file!!!!
    return False


def set_path(parameters):
    # need to create a local file with the same architecture

    parameters.path_files = os.path.join(os.getcwd(), 'data_files')

    parameters.paths = {'files': os.path.join(os.getcwd(), 'data_files'),
                  'data': os.path.join(os.getcwd(), 'data_files', 'data'),
                  'gap_statistic': os.path.join(os.getcwd(), 'data_files', 'output', 'gap_statistic'),
                  'clustering': os.path.join(os.getcwd(), 'data_files', 'output', 'clustering'),
                  'clustering_info': os.path.join(os.getcwd(), 'data_files', 'output', 'clustering', 'info'),
                  'clustering_figures': os.path.join(os.getcwd(), 'data_files', 'output', 'clustering', 'figures'),
                  'correlation_figures': os.path.join(os.getcwd(), 'data_files', 'output', 'correlations'),
                  'association_figures': os.path.join(os.getcwd(), 'data_files', 'output', 'associations'),
                  }
    server_tools.create_folders(parameters.paths)


def check_input(parameters, paths):
    assert type(parameters.name_data) is str
    assert type(parameters.name_compartment) is str
    assert type(parameters.log_transform) is bool
    assert type(parameters.max_testing_k) is int
    assert type(parameters.max_final_k) is int
    assert parameters.max_final_k <= parameters.max_testing_k
    assert type(parameters.outcomes) is list
    assert type(parameters.covariates) is list

    for col_name in parameters.outcomes + parameters.covariates + parameters.log_column_names:
        assert type(col_name) is str
        tools.assert_column_exists_in_path(os.path.join(paths['data'], 'patient_data.xlsx'), col_name) #change to other things

    return True


def log_transform(parameters, cy_data, patient_data):

    # needs to change to a better code writing

    if parameters.log_transform:
        cy_data = np.log10(cy_data)

        if parameters.log_column_names != [] and parameters.outcomes != []:
            for col_name in parameters.log_column_names:
                new_col_name = 'log_' + col_name

                # log transform variable
                patient_data[new_col_name] = np.log10(patient_data[col_name])

                # replace column with new log transformed column
                if col_name in parameters.covariates:
                    parameters.covariates.remove(col_name)
                    parameters.covariates.append(new_col_name)
