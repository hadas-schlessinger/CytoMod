import os
import cytomod
import tools
import logging


def adjust_cytokine(args):
    args.do_recalculate = args.recalculate_modules or \
            not os.path.exists(os.path.join(args.paths['clustering'], 'cyto_mod_adj.dill'))
    # If modules file does not exist in storage,
    # or args.recalculate_modules=True - prepare modules.
    # Otherwise - read from file.
    if args.do_recalculate:
        # Absolute
        args.cyto_mod_abs = cytomod.cytomod_class(args.name_data, args.name_compartment, False, args.cy_data)
        # Adjusted
        args.cyto_mod_adj = cytomod.cytomod_class(args.name_data, args.name_compartment, True, args.cy_data)
    else:
        args.cyto_mod_abs = tools.read_from_dill(os.path.join(args.paths['clustering'], 'cyto_mod_abs.dill'))
        args.cyto_mod_adj = tools.read_from_dill(os.path.join(args.paths['clustering'], 'cyto_mod_adj.dill'))
    print('finished adjustments')
    return args
