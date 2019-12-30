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
        ans_pics_path.append(os.path.join('/static', img))
    return ans_pics_path



def make_pdf():
    pass


def download_pdf():
    pass

