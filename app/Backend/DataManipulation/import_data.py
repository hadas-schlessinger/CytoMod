import os
import sys
import pandas as pd
import tools
import warnings
sys.path.append(os.path.join(os.getcwd(), 'cytomod', 'otherTools'))
warnings.filterwarnings('ignore')
warnings.simplefilter('ignore')


def make_cyto_data(parameters):
    if(parameters.luminex):
        cy_data = tools.read_excel(os.path.join(parameters.paths['data'], 'cytokine_data.xlsx'), indexCol=0)
        #insert to skip a row
    cy_data = tools.read_excel(os.path.join(parameters.paths['data'], 'cytokine_data.xlsx'), indexCol=0)
    cy_data.dropna(axis='index', how='all', inplace=True)

    if parameters.cytokines is None:
        parameters.cytokines = list(cy_data.columns)
# Only cytokines contained in parameters.cytokines list
        parameters.path_files = os.path.join(os.getcwd(), 'data_files')
    return cy_data


def make_patiants_data(parameters):
    if parameters.outcomes != []:
        patient_data = tools.read_excel(os.path.join(parameters.paths['data'], 'patient_data.xlsx'), indexCol=0)
        patient_data.dropna(axis='index', how='all', inplace=True)
        return patient_data
    return None




