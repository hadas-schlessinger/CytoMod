import os
import sys
from app.backend import tools
import warnings
sys.path.append(os.path.join(os.getcwd(), 'cytomod', 'otherTools'))
warnings.filterwarnings('ignore')
warnings.simplefilter('ignore')


def make_cyto_data(parameters):
    cy_data_name = tools.read_excel(os.path.join(parameters.path_files, 'data_files_and_project_names.xlsx')).get_value(0, 0)
    cy_data = tools.read_excel(os.path.join(parameters.data_files, cy_data_name), skiprows=[4, 5, 6, 7], indexCol=0, header = 3) if parameters.luminex \
        else tools.read_excel(os.path.join(parameters.data_files, cy_data_name), indexCol=0)
    cy_data.dropna(axis='index', how='all', inplace=True)
    parameters.cytokines = list(cy_data.columns) if parameters.cytokines[0] == '' and len(parameters.cytokines) == 1 else parameters.cytokines # None
    cy_data = cy_data[parameters.cytokines]     # Only cytokines contained in parameters.cytokines list
    # TODO: ADD convertLevel
    return cy_data


def make_patients_data(parameters):
    if parameters.outcomes[0] != '':
        patient_data_name = tools.read_excel(os.path.join(parameters.path_files, 'data_files_and_project_names.xlsx')).get_value(1, 0)
        if patient_data_name == "no file":
            return None
        patient_data = tools.read_excel(os.path.join(parameters.data_files, patient_data_name), indexCol=0)
        patient_data.dropna(axis='index', how='all', inplace=True)
        return patient_data
    return None




