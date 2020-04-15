from app.backend.data_manipulation import clustering
from app.backend.visualization import figure_scheme
from app.backend import server_tools
import logging
import sys
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


def calc_clustering(parameters):
    parameters = figure_scheme.mean_person(parameters)
    logging.info('starting clustering')
    parameters = clustering.best_k(parameters)
    parameters = clustering.clustering(parameters)
    parameters = server_tools.create_modules_dict(parameters)
    return parameters

def calc_abs_figures(parameters):
    # parameters = figure_scheme.pairwise_person('abs', parameters)
    logging.info('starting correlations for absolute cytokines')
    parameters = figure_scheme.pairwise_correlation_with_moudles('abs', parameters)
    parameters = figure_scheme.same_cluster_reliability('abs', parameters)
    parameters = figure_scheme.modules_cytokine_correlation('abs', parameters)
    logging.info('starting associations to outcomes for absolute cytokines')
    if parameters.outcomes[0]!= '':
        parameters = figure_scheme.associations_to_outcomes('abs', parameters)
        parameters = figure_scheme.outcomes_figures('abs', parameters)
    logging.info('finished creating abs figures')
    return parameters
    # add print tables


def calc_adj_figures(parameters):
    # parameters = figure_scheme.pairwise_person('adj', parameters)
    logging.info('starting correlations for adjusted cytokines')
    parameters = figure_scheme.pairwise_correlation_with_moudles('adj', parameters)
    parameters = figure_scheme.same_cluster_reliability('adj', parameters)
    parameters = figure_scheme.modules_cytokine_correlation('adj', parameters)
    figure_scheme.write_results(parameters)
    logging.info('starting associations to outcomes for adjusted cytokines')
    if parameters.outcomes[0] != '':
        parameters = figure_scheme.associations_to_outcomes('adj', parameters)
        figure_scheme.outcomes_figures('adj', parameters)
    logging.info('finished creating adj figures')
    return parameters
    # add print tables

