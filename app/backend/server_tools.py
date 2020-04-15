import os
import sys
# sys.path.append(os.path.join(os.getcwd(), 'cytomod', 'otherTools'))
import tools
import warnings
warnings.filterwarnings('ignore')
warnings.simplefilter('ignore')
import io
import base64


def create_folders(paths):
    tools.create_folder(paths['overview'])
    tools.create_folder(paths['clustering_abs'])
    tools.create_folder(paths['clustering_adj'])
    tools.create_folder(paths['correlation_figures_abs'])
    tools.create_folder(paths['correlation_figures_adj'])
    tools.create_folder(paths['outcome_abs'])
    tools.create_folder(paths['outcome_adj'])


def make_ans(parameters):
    ans_pics_path=[]
    for img in parameters.images:
        ans = {'path':img['path'],
               'height': img['height'],
               'width': img['width'],
               'headline': img['headline']}
        ans_pics_path.append(ans)
    return ans_pics_path


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
