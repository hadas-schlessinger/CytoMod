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


def set_data(args):
    if check_input(args, args.paths):
        args.seed = os.environ.get("SEED")
       # cy_data = server_tools.read_file()  # needs to be created
       # data_path = server_tools.save_data_on_local_path(cy_data)
        set_path(args)
        args.cy_data = import_data.make_cyto_data(args)
        args.patient_data = import_data.make_patiants_data(args)
        log_transform(args, args.cy_data, args.patient_data)
        return args
    # dont forget to delete file!!!!
    return False


def set_path(args):
    # need to create a local file with the same architecture

    args.path_files = os.path.join(os.getcwd(), 'data_files')

    args.paths = {'files': os.path.join(os.getcwd(), 'data_files'),
                  'data': os.path.join(os.getcwd(), 'data_files', 'data'),
                  'gap_statistic': os.path.join(os.getcwd(), 'data_files', 'output', 'gap_statistic'),
                  'clustering': os.path.join(os.getcwd(), 'data_files', 'output', 'clustering'),
                  'clustering_info': os.path.join(os.getcwd(), 'data_files', 'output', 'clustering', 'info'),
                  'clustering_figures': os.path.join(os.getcwd(), 'data_files', 'output', 'clustering', 'figures'),
                  'correlation_figures': os.path.join(os.getcwd(), 'data_files', 'output', 'correlations'),
                  'association_figures': os.path.join(os.getcwd(), 'data_files', 'output', 'associations'),
                  }
    server_tools.create_folders(args.paths)


def check_input(args, paths):
    assert type(args.name_data) is str
    assert type(args.name_compartment) is str
    assert type(args.log_transform) is bool
    assert type(args.max_testing_k) is int
    assert type(args.max_final_k) is int
    assert args.max_final_k <= args.max_testing_k
    assert type(args.outcomes) is list
    assert type(args.covariates) is list

    for col_name in args.outcomes + args.covariates + args.log_column_names:
        assert type(col_name) is str
        tools.assert_column_exists_in_path(os.path.join(paths['data'], 'patient_data.xlsx'), col_name) #change to other things

    return True


def log_transform(args, cy_data, patient_data):

    # needs to change to a better code writing

    if args.log_transform:
        cy_data = np.log10(cy_data)

        if args.log_column_names != [] and args.outcomes != []:
            for col_name in args.log_column_names:
                new_col_name = 'log_' + col_name

                # log transform variable
                patient_data[new_col_name] = np.log10(patient_data[col_name])

                # replace column with new log transformed column
                if col_name in args.covariates:
                    args.covariates.remove(col_name)
                    args.covariates.append(new_col_name)
