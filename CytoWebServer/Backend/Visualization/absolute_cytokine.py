from . import scheme
from ..DataManipulation import clustering

def calc_abs_figures():
    scheme.pairwise_person('abs')
    scheme.mean_person('abs')
    scheme.modules_cytokine_correlation('abs')
    scheme.best_k('abs')
    clustering('abs')
    scheme.clustering_results('abs')
    scheme.associations_to_outcomes('abs')
    scheme.figures('abs')
