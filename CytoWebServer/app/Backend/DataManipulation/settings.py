import os
import io
import sys
sys.path.append(os.path.join(os.getcwd(), 'cytomod', 'otherTools'))
import tools
from .. import server_tools
import warnings
import app
import csv

warnings.filterwarnings('ignore')
warnings.simplefilter('ignore')

SEED = 1234


def set_data(args):
    stream = io.StringIO(f.stream.read().decode("UTF8"), newline=None)
    csv_data = csv.reader(stream)
    for row in csv.reader(stream, dialect=csv.excel):
        if row:
            data.append(row)


    data = server_tools.read_file()  # needs to be created
    data_path = server_tools.save_data_on_local_path(data)
    paths = set_path(data_path)

    if check_input(args, paths):
        args.seed = app.config.get_namespace('SEED')
        return True
    #dont forget to delete file!!!!
    return False


def set_path(args):
    #need to create a local file with the same architecture

    #args.path_files = os.path.join(os.getcwd(), 'data_files')

    args.paths = {'files': os.path.join(os.getcwd(), 'data_files'),
                  'data': os.path.join(os.getcwd(), 'data_files', 'data'),
                  'gap_statistic': os.path.join(os.getcwd(), 'data_files', 'output', 'gap_statistic'),
                  'clustering': os.path.join(os.getcwd(), 'data_files', 'output', 'clustering'),
                  'clustering_info': os.path.join(os.getcwd(), 'data_files', 'output', 'clustering', 'info'),
                  'clustering_figures': os.path.join(os.getcwd(), 'data_files', 'output', 'clustering', 'figures'),
                  'correlation_figures': os.path.join(os.getcwd(), 'data_files', 'output', 'correlations'),
                  'association_figures': os.path.join(os.getcwd(), 'data_files', 'output', 'associations'),
                  }
    server_tools.create_folders(args.paths)
    return args.paths



def check_input(args,paths):
    assert type(args.name_data) is str
    assert type(args.name_compartment) is str
    assert type(args.log_transform) is bool
    assert type(args.max_testing_k) is int
    assert type(args.max_final_k) is int
    assert args.max_final_k <= args.max_testing_k
    assert type(args.outcomes) is list
    assert type(args.covariates) is list

    for col_name in args.outcomes + args.covariates + args.log_column_names:
        assert type(col_name) is str
        tools.assert_column_exists_in_path(os.path.join(paths['data'], 'patient_data.xlsx'), col_name)


def transform(text_file_contents):
    return text_file_contents.replace("=", ",")
