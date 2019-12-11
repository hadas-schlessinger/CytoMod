from app.Backend.DataManipulation import clustering
from app.Backend.Visualization import figure_scheme


def calc_abs_figures(args):
    figure_scheme.pairwise_person('abs', args)
    print('finished 1')
    figure_scheme.mean_person(args)
    print('finished 2')
    clustering.best_k(args)
    print('finished 3')
    clustering.clustering(args)
    print('finished 4')
    figure_scheme.pairwise_corelletion_with_moudles('abs', args)
    print('finished 5')
    figure_scheme.same_cluster_reliability('abs', args)
    print('finished 6')
    figure_scheme.modules_cytokine_correlation('abs', args)
    figure_scheme.associations_to_outcomes('abs', args)
    figure_scheme.figures('abs', args)


def calc_adj_figures(args):
    figure_scheme.pairwise_person('adj', args)
    figure_scheme.pairwise_corelletion_with_moudles('abs', args)
    figure_scheme.same_cluster_reliability('adj', args)
    figure_scheme.modules_cytokine_correlation('adj', args)
    figure_scheme.write_results(args)
    figure_scheme.associations_to_outcomes('adj', args)
    figure_scheme.figures('adj', args)


