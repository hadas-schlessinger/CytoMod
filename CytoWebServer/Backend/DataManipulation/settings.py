import os
import sys
import pandas as pd
sys.path.append(os.path.join(os.getcwd(), 'cytomod', 'otherTools'))
import matplotlib.pyplot as plt
import cytomod
import cytomod.run_gap_statistic as gap_stat
import cytomod.assoc_to_outcome as outcome
from cytomod import plotting as cyplot
from hclusterplot import plotHColCluster
import tools
from .. import server_tools
import numpy as np
import random
import warnings
warnings.filterwarnings('ignore')
warnings.simplefilter('ignore')

SEED = 1234


def set_data(name_ds,name_comp,log,max_k,final_k,recalc, col_name,regrassion,log_col_name,cytokine = None):
    data = server_tools.read_file()  # needs to be created
    data_path = server_tools.save_data_on_local_path(data)
    paths = set_path(data_path)
    if check_input(name_ds,name_comp, log,max_k, final_k, recalc, col_name, regrassion, log_col_name, paths ):
        args = tools.Object()
        args.name_data = name_ds
        args.name_compartment = name_comp
        args.log_transform = log
        args.max_testing_k = max_k
        args.max_final_k = final_k  # Must be <= max_testing_k
        args.recalculate_modules = recalc
        args.outcomes = col_name  # names of binary outcome columns
        args.covariates = regrassion  # names of regression covariates to control for
        args.log_column_names = log_col_name  # or empty list: []
        args.cytokines = cytokine  # if none, will analyze all
        args.seed = SEED
        return True
    return False


def set_path(args):
    #need to create a local file with the same architecture

    #args.path_files = os.path.join(os.getcwd(), 'data_files')

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
    return args.paths



def check_input(name_data, name_compartment, log_transform,max_testing_k, max_final_k, outcomes, covariates, log_column_names,paths):
    assert type(name_data) is str
    assert type(name_compartment) is str
    assert type(log_transform) is bool
    assert type(max_testing_k) is int
    assert type(max_final_k) is int
    assert max_final_k <= max_testing_k
    assert type(outcomes) is list
    assert type(covariates) is list

    for col_name in outcomes + covariates + log_column_names:
        assert type(col_name) is str
        tools.assert_column_exists_in_path(os.path.join(paths['data'], 'patient_data.xlsx'), col_name)


