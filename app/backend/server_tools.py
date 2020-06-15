import os
import warnings
warnings.filterwarnings('ignore')
warnings.simplefilter('ignore')
import base64
from app.backend import data_manipulation as dm, tools
from app.backend import visualization
import logging
import pandas as pd
import time

DELETION_TIME = 60*60*24*7


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
                   'location':img['location'],
                   'explanation': img['explanation']}
        index = index + 1
        results.append(result)

    abs_module = {'index': f'row_{index}',
                  'image': 'not',
                'type': 'module',
                'absolute': arrange_modules(parameters.modules[0]),
                  'explanation':'this is the absolute cytokines moduls',
                  'location': 'overview'}
    adj_module = {'index': f'row_{index+1}',
                  'image':'not',
                'type': 'module',
                'adjusted': arrange_modules(parameters.modules[1]),
                  'explanation': 'this is the adjusted cytokines moduls',
                  'location': 'overview'}

    results.append(abs_module)
    results.append(adj_module)

    tools.write_DF_to_excel(os.path.join('static/', parameters.id['id'], 'all_results.xlsx'),
                            pd.DataFrame(results))


def arrange_modules(modules):
    string_modules = []
    for module in modules:
        module_string = ', '.join(module)
        string_modules.append([module_string])
    return string_modules


def encode_images(id):
    xls_results = tools.read_excel(os.path.join('static/', id, 'all_results.xlsx')).set_index('index')
    index = 1
    for image in xls_results['image']:
        if image != 'not':
            with open(image, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read())
                xls_results['image'][f'row_{index}']= f'{encoded_string}'
        index = index +1
    return xls_results


def clean_folder(path):
    for file in os.listdir(path):
        logging.info(f'deleting {file}')
        os.remove(os.path.join(path,  file))
    delete_folder(path)


def delete_folder(folder_path):
    logging.info(f'deleting {folder_path}')
    os.rmdir(os.path.join(folder_path))


def clean_project(parameters):
    logging.info('cleaning data')
    for folder_path in parameters.paths.values():
        clean_folder(folder_path)
    clean_folder(parameters.data_files)
    clean_folder(parameters.path_files)


def create_modules_dict(parameters):
    modules_adj = []
    counter = 1
    for module in range(len(parameters.cyto_mod_adj.modDf.columns)):
        modules_adj.append([])
        i = 0
        for cytokine in parameters.cyto_mod_adj.labels:
            modules_adj[module].append(parameters.cyto_mod_adj.cyDf.columns[i]) if cytokine == counter else ""
            i = i + 1
        counter = counter+1
    modules_abs = []
    counter = 1
    for module in range(len(parameters.cyto_mod_abs.modDf.columns)):
        modules_abs.append([])
        i = 0
        for cytokine in parameters.cyto_mod_abs.labels:
            modules_abs[module].append(parameters.cyto_mod_abs.cyDf.columns[i]) if cytokine == counter else ""
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

def assert_column_exists_in_path(file_path, col_name, sheet=0):
    df = tools.read_excel(file_path, sheet=sheet, nrows=3)
    if col_name not in df.columns:
        logging.error(f'Column {col_name} does not exist in file {file_path}')
        return False
    return True


def run_server(*parameters_dict):
    parameters = create_parameters_object(*parameters_dict)
    try:
        id = parameters.id['id']
        parameters = dm.settings.set_data(parameters)
        if parameters is False:
            logging.error('setting data was incorrect')
            error_id = {'id': id,
                        'status': 'ERROR'}
            tools.write_DF_to_excel(os.path.join('static/', id, 'process_id_status.xlsx'), error_id)
            exit()
        parameters = dm.cytocine_adjustments.adjust_cytokine(parameters)
        parameters = visualization.figures.calc_clustering(parameters)
        parameters = visualization.figures.calc_abs_figures(parameters)
        parameters = visualization.figures.calc_adj_figures(parameters)
        save_images_and_modules(parameters)
        parameters.id = {'id': parameters.id['id'],
                         'status': 'DONE'}
        tools.write_DF_to_excel(os.path.join('static/', parameters.id['id'], 'process_id_status.xlsx'), parameters.id)
        # todo: insert save file to database
        # parameters.save_file = request.form.get('save_file') in ['true', '1', 'True', 'TRUE', 'on']  # for saving the file in the server
        logging.info('finished to calc the method')
        time.sleep(DELETION_TIME)
        # todo: insert email send
        logging.info('deleting the data')
        clean_project(parameters)
    except Exception as e:
        logging.error(f'an error occured while calculating the method: {e}')
        parameters.id = {'id': parameters.id['id'],
                         'status': 'ERROR'}
        tools.write_DF_to_excel(os.path.join('static/', parameters.id['id'], 'process_id_status.xlsx'), parameters.id)
        time.sleep(600)
        logging.info('deleting the data')
        clean_project(parameters)

