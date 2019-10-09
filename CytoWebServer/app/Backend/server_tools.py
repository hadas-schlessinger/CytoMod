import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'cytomod', 'otherTools'))
import tools
import warnings
warnings.filterwarnings('ignore')
warnings.simplefilter('ignore')
import pandas as pd

def read_file(args):

    pass


def save_data_on_local_path():
    pass


def create_folders(paths):
    tools.create_folder(paths['gap_statistic'])
    tools.create_folder(paths['clustering_info'])
    tools.create_folder(paths['clustering_figures'])
    tools.create_folder(paths['correlation_figures'])
    tools.create_folder(paths['association_figures'])

def save_figure():
    pass

def save_var():
    pass


def make_pdf():
    pass

def download_pdf():
    pass

