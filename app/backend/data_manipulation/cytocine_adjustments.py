import os
from app import cytomod
from app.backend import tools
import logging


def adjust_cytokine(parameters):
    parameters.do_recalculate = parameters.recalculate_modules or \
            not os.path.exists(os.path.join(parameters.paths['clustering_adj'], 'cyto_mod_adj.dill'))
    # If modules file does not exist in storage,
    # or parameters.recalculate_modules=True - prepare modules.
    # Otherwise - read from file.
    if parameters.do_recalculate:
        # Absolute
        parameters.cyto_mod_abs = cytomod.cytomod_class(parameters.name_data, parameters.name_compartment, False, parameters.cy_data)
        # Adjusted
        parameters.cyto_mod_adj = cytomod.cytomod_class(parameters.name_data, parameters.name_compartment, True, parameters.cy_data)
    else:
        parameters.cyto_mod_abs = tools.read_from_dill(os.path.join(parameters.paths['clustering_abs'], 'cyto_mod_abs.dill'))
        parameters.cyto_mod_adj = tools.read_from_dill(os.path.join(parameters.paths['clustering_adj'], 'cyto_mod_adj.dill'))
    parameters.cyto_modules = {'adj': parameters.cyto_mod_adj, 'abs': parameters.cyto_mod_abs}
    logging.info('finished adjustments')
    return parameters
