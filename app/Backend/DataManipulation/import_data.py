import os
import sys
import pandas as pd
sys.path.append(os.path.join(os.getcwd(), 'cytomod', 'otherTools'))
import tools
import warnings
import numpy as np
warnings.filterwarnings('ignore')
warnings.simplefilter('ignore')


def make_cyto_data(args):
    cy_data = tools.read_excel(os.path.join(args.paths['data'], 'cytokine_data.xlsx'), indexCol=0)
    cy_data.dropna(axis='index', how='all', inplace=True)

    if args.cytokines is None:
        args.cytokines = list(cy_data.columns)

    # Only cytokines contained in args.cytokines list
    args.path_files = os.path.join(os.getcwd(), 'data_files')

def make_patiants_data(args):
    if args.outcomes != []:
        patient_data = tools.read_excel(os.path.join(args.paths['data'], 'patient_data.xlsx'),
                                        indexCol=0)
        patient_data.dropna(axis='index', how='all', inplace=True)


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


