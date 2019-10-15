import os
import sys
# sys.path.append(os.path.join(os.getcwd(), 'cytomod', 'otherTools'))
import tools
import warnings
warnings.filterwarnings('ignore')
warnings.simplefilter('ignore')


def read_file(args):
    # insert reading function
    pass



def save_data_on_local_path():
    pass


def create_folders(paths):
    tools.create_folder(paths['gap_statistic'])
    tools.create_folder(paths['clustering_info'])
    tools.create_folder(paths['clustering_figures'])
    tools.create_folder(paths['correlation_figures'])
    tools.create_folder(paths['association_figures'])


def make_ans():
    pass



def make_pdf():
    pass


def download_pdf():
    pass

