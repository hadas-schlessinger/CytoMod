from app.Backend.DataManipulation import clustering
from app.Backend.Visualization import figure_scheme
from app.Backend import server_tools
import logging


def calc_abs_figures(parameters):
    logging.warning('starting associations for absolute cytokines')
    parameters = figure_scheme.pairwise_person('abs', parameters)
    parameters = figure_scheme.mean_person(parameters)
    logging.warning('starting clustering')
    parameters = clustering.best_k(parameters)
    parameters = clustering.clustering(parameters)
    parameters = server_tools.create_modules_dict(parameters)
    logging.warning('starting correlations for absolute cytokines')
    parameters = figure_scheme.pairwise_corelletion_with_moudles('abs', parameters)
    parameters = figure_scheme.same_cluster_reliability('abs', parameters)
    parameters = figure_scheme.modules_cytokine_correlation('abs', parameters)
    logging.warning('starting associations to outcomes for absolute cytokines')
    if parameters.outcomes[0]!= '':
        parameters = figure_scheme.associations_to_outcomes('abs', parameters)
        parameters = figure_scheme.outcomes_figures('abs', parameters)
    logging.warning('finished creating abs figures')
    return parameters
    # add print tables


def calc_adj_figures(parameters):
    logging.warning('starting associations for adjusted cytokines')
    parameters = figure_scheme.pairwise_person('adj', parameters)
    logging.warning('starting correlations for adjusted cytokines')
    parameters = figure_scheme.pairwise_corelletion_with_moudles('adj', parameters)
    parameters = figure_scheme.same_cluster_reliability('adj', parameters)
    parameters = figure_scheme.modules_cytokine_correlation('adj', parameters)
    figure_scheme.write_results(parameters)
    logging.warning('starting associations to outcomes for adjusted cytokines')
    if parameters.outcomes[0] != '':
        parameters = figure_scheme.associations_to_outcomes('adj', parameters)
        figure_scheme.outcomes_figures('adj', parameters)
    logging.warning('finished creating adj figures')
    return parameters
    # add print tables

