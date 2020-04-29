import os
import sys
# sys.path.append(os.path.join(os.getcwd(), 'cytomod', 'otherTools'))
import tools
import warnings
warnings.filterwarnings('ignore')
warnings.simplefilter('ignore')
import io
import base64
from app.backend import data_manipulation as dm
from app.backend import visualization
import logging
import pandas as pd
from PIL import Image
from io import BytesIO



def create_folders(paths):
    tools.create_folder(paths['overview'])
    tools.create_folder(paths['clustering_abs'])
    tools.create_folder(paths['clustering_adj'])
    tools.create_folder(paths['correlation_figures_abs'])
    tools.create_folder(paths['correlation_figures_adj'])
    tools.create_folder(paths['outcome_abs'])
    tools.create_folder(paths['outcome_adj'])


def save_images_and_modules(parameters):
    results=[]
    index = 1
    for img in parameters.images:
        result = {'index': f'row_{index}',
                   'type': 'image',
                   'image': img['path'],
                   'height': img['height'],
                   'width': img['width'],
                   'headline': img['headline'],
                   'location':img['location']}
        index = index + 1
        results.append(result)

    abs_module = {'index': f'row_{index}',
                  'image': 'not',
                'type': 'module',
                'absolute': parameters.modules[0],
                  'location': 'overview'}
    adj_module = {'index': f'row_{index+1}',
                  'image':'not',
                'type': 'module',
                'adjusted': parameters.modules[1],
                  'location': 'overview'}

    results.append(abs_module)
    results.append(adj_module)

    tools.write_DF_to_excel(os.path.join('app/static/', parameters.name_data, 'all_results.xlsx'),
                            pd.DataFrame(results))
    tools.write_DF_to_excel(os.path.join(parameters.paths['overview'], 'abs_modules.xlsx'), parameters.modules[0])
    tools.write_DF_to_excel(os.path.join(parameters.paths['overview'], 'adj_modules.xlsx'), parameters.modules[1])


def encode_images(name):
    xls_results = tools.read_excel(os.path.join('app/static/',  name, 'all_results.xlsx')).set_index('index')
    index = 1
    for image in xls_results['image']:
        if image != 'not':
            with open(image, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read())
                xls_results['image'][f'row_{index}']= f'{encoded_string}'
        index = index +1
    return xls_results


def clean_static(parameters):
    for f in os.listdir(parameters.path_files):
        if f.endswith('.png'):
            os.remove(parameters.path_files + f)


def clean_data(parameters):
    print('cleaning data')
    for f in os.listdir(parameters.data_files):
       # if f.endswith('.xisx'):
        print(f'deleting {f}')
        os.remove(parameters.data_files + f)


def create_modules_dict(parameters):
    modules_adj = {'headline': 'Adjusted Modules:'}
    counter = 1
    for module in range(len(parameters.cyto_mod_adj.modDf.columns)):
        modules_adj[module+1] = []
        i = 0
        for cytokine in parameters.cyto_mod_adj.labels:
            modules_adj.get(module+1).append(parameters.cyto_mod_adj.cyDf.columns[i]) if cytokine == counter else ""
            i = i + 1
        counter = counter+1
    modules_abs = {'headline': 'Absolute Modules:'}
    counter = 1
    for module in range(len(parameters.cyto_mod_abs.modDf.columns)):
        modules_abs[module+1] = []
        i = 0
        for cytokine in parameters.cyto_mod_abs.labels:
            modules_abs.get(module+1).append(parameters.cyto_mod_abs.cyDf.columns[i]) if cytokine == counter else ""
            i = i + 1
        counter = counter + 1
    parameters.modules = []
    parameters.modules.append(modules_abs)
    parameters.modules.append(modules_adj)
    return parameters


def create_parameters_object(name_data, id, name_compartment, luminex, log_transform, max_testing_k, recalculate_modules, outcomes, covariates, log_column_names, cytokines):
    parameters = tools.Object()
    parameters.images = []
    parameters.name_data = name_data
    parameters.id =id
    parameters.name_compartment= name_compartment
    parameters.luminex =luminex
    parameters.log_transform = log_transform
    parameters.max_testing_k = max_testing_k
    parameters.recalculate_modules =recalculate_modules
    parameters.outcomes = outcomes
    parameters.covariates = covariates
    parameters.log_column_names = log_column_names
    parameters.cytokines = cytokines
    return parameters

def run_server(*parameters_dict):
    parameters = create_parameters_object(*parameters_dict)
    parameters = dm.settings.set_data(parameters)
    parameters = dm.cytocine_adjustments.adjust_cytokine(parameters)
    parameters = visualization.figures.calc_clustering(parameters)
    parameters = visualization.figures.calc_abs_figures(parameters)
    parameters = visualization.figures.calc_adj_figures(parameters)
    save_images_and_modules(parameters)
    parameters.id = {'id': parameters.id,
                     'status': 'DONE'}
    tools.write_DF_to_excel(os.path.join('app/static/', parameters.name_data, 'process_id_status.xlsx'), parameters.id)
    # parameters.save_file = request.form.get('save_file') in ['true', '1', 'True', 'TRUE', 'on']  # for saving the file in the server
    # print(parameters.save_file)
    logging.info('finished to calc the method')