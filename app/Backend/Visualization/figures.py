from app.Backend.DataManipulation import clustering
from app.Backend.Visualization import figure_scheme
import logging


def calc_abs_figures(args):
    logging.warning('starting associations for absolute cytokines')
    figure_scheme.pairwise_person('abs', args)
    figure_scheme.mean_person(args)
    logging.warning('starting clustering')
    clustering.best_k(args)
    clustering.clustering(args)
    logging.warning('starting correlations for absolute cytokines')
    figure_scheme.pairwise_corelletion_with_moudles('abs', args)
    figure_scheme.same_cluster_reliability('abs', args)
    figure_scheme.modules_cytokine_correlation('abs', args)
    logging.warning('starting associations to outcomes for absolute cytokines')
    figure_scheme.associations_to_outcomes('abs', args)
    figure_scheme.figures('abs', args)
    print('finished creating abs figures')
    # add print tables


def calc_adj_figures(args):
    logging.warning('starting associations for adjusted cytokines')
    figure_scheme.pairwise_person('adj', args)
    logging.warning('starting correlations for adjusted cytokines')
    figure_scheme.pairwise_corelletion_with_moudles('abs', args)
    figure_scheme.same_cluster_reliability('adj', args)
    figure_scheme.modules_cytokine_correlation('adj', args)
    figure_scheme.write_results(args)
    logging.warning('starting associations to outcomes for adjusted cytokines')
    figure_scheme.associations_to_outcomes('adj', args)
    figure_scheme.figures('adj', args)
    print('finished creating adj figures')
    # add print tables

