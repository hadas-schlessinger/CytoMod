import os
import sys
# sys.path.append(os.path.join(os.getcwd(), 'cytomod', 'otherTools'))
import tools
import warnings
warnings.filterwarnings('ignore')
warnings.simplefilter('ignore')



def create_folders(paths):
    tools.create_folder(paths['gap_statistic'])
    tools.create_folder(paths['clustering_info'])
    tools.create_folder(paths['clustering_figures'])
    tools.create_folder(paths['correlation_figures'])
    tools.create_folder(paths['association_figures'])


def make_ans(parameters):
    ans_pics_path=[]
    for img in parameters.images:
        ans = {'path': os.path.join('/static', img['name']),
               'height': img['height'],
               'width': img['width'],
               'name': img['name'],
               'headline': img['headline']}
        ans_pics_path.append(ans)
    return ans_pics_path


def clean_static():
    for f in os.listdir('app/static'):
        if f.endswith('.png'):
            os.remove('app/static/' + f)


def clean_data():
    print('cleaning data')
    for f in os.listdir('app/static/data_files/data/'):
       # if f.endswith('.xisx'):
        print(f'deleting {f}')
        os.remove('app/static/data_files/data/' + f)


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
