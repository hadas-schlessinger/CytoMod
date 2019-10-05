from . import scheme
from ..DataManipulation import clustering


def adjust_cytokine(args):
    do_recalculate = args.recalculate_modules or \
            not os.path.exists(os.path.join(args.paths['clustering'], 'cyto_mod_adj.dill'))


    # If modules file does not exist in storage,
    # or args.recalculate_modules=True - prepare modules.
    # Otherwise - read from file.
    if do_recalculate:
        # Absolute
        cyto_mod_abs = cytomod.cytomod_class(args.name_data, args.name_compartment, False, cy_data)
        # Adjusted
        cyto_mod_adj = cytomod.cytomod_class(args.name_data, args.name_compartment, True, cy_data)
    else:
        cyto_mod_abs = tools.read_from_dill(os.path.join(args.paths['clustering'], 'cyto_mod_abs.dill'))
        cyto_mod_adj = tools.read_from_dill(os.path.join(args.paths['clustering'], 'cyto_mod_adj.dill'))

def calc_adj_figures(args):
    scheme.pairwise_person('adj')
    scheme.mean_person('adj')
    scheme.modules_cytokine_correlation('adj')
    scheme.best_k('adj')
    clustering('adj')
    scheme.clustering_results('adj')
    scheme.associations_to_outcomes('adj')
    scheme.figures('adj')


