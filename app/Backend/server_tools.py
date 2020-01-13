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
    for f in os.listdir('app/static/data_files/data'):
        print(f'deleting {f}')
        os.remove('app/static/data_files/data' + f)



