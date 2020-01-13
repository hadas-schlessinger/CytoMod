from app.Backend.DataManipulation import clustering
from app.Backend.Visualization import figure_scheme
import logging


def calc_abs_figures(parameters):
    logging.warning('starting associations for absolute cytokines')
    figure_scheme.pairwise_person('abs', parameters)
    figure_scheme.mean_person(parameters)
    logging.warning('starting clustering')
    clustering.best_k(parameters)
    clustering.clustering(parameters)
    logging.warning('starting correlations for absolute cytokines')
    figure_scheme.pairwise_corelletion_with_moudles('abs', parameters)
    figure_scheme.same_cluster_reliability('abs', parameters)
    figure_scheme.modules_cytokine_correlation('abs', parameters)
    logging.warning('starting associations to outcomes for absolute cytokines')
    figure_scheme.associations_to_outcomes('abs', parameters)
    figure_scheme.figures('abs', parameters)
    logging.warning('finished creating abs figures')
    # add print tables


def calc_adj_figures(parameters):
    logging.warning('starting associations for adjusted cytokines')
    figure_scheme.pairwise_person('adj', parameters)
    logging.warning('starting correlations for adjusted cytokines')
    figure_scheme.pairwise_corelletion_with_moudles('adj', parameters)
    figure_scheme.same_cluster_reliability('adj', parameters)
    figure_scheme.modules_cytokine_correlation('adj', parameters)
    figure_scheme.write_results(parameters)
    logging.warning('starting associations to outcomes for adjusted cytokines')
    figure_scheme.associations_to_outcomes('adj', parameters)
    figure_scheme.figures('adj', parameters)
    logging.warning('finished creating adj figures')
    # add print tables

