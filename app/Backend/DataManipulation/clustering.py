import random
from cytomod import run_gap_statistic as gap_stat
import tools
import os


def best_k(args):
    if args.do_recalculate:
        random.seed(args.seed)  # set seed for random numbers stream
        args.bestK = {}
        args.bestK['adj'] = gap_stat.getBestK(args.cyto_mod_adj.cyDf,
                                              max_testing_k=args.max_testing_k,
                                              max_final_k=args.max_final_k,
                                              save_fig_path=os.path.join(args.paths['gap_statistic'], 'gap_stat_adj.png'))
        args.images.append('gap_stat_adj.png')
        args.bestK['abs'] = gap_stat.getBestK(args.cyto_mod_abs.cyDf,
                                              max_testing_k=args.max_testing_k,
                                              max_final_k=args.max_final_k,
                                              save_fig_path=os.path.join(args.paths['gap_statistic'], 'gap_stat_abs.png'))
        args.images.append('gap_stat_abs.png')

        tools.write_DF_to_excel(os.path.join(args.paths['clustering'], 'bestK.xlsx'), args.bestK)
    else:
        # Get modules from storage
        args.bestK = tools.read_excel(os.path.join(args.paths['clustering'], 'bestK.xlsx'))
        args.bestK = dict(args.bestK['value'])
    return args


def clustering(args):
    # Cluster and write modules to file
    if args.do_recalculate:
        args.cyto_mod_adj.cluster_cytokines(K=args.bestK['adj'])
        args.cyto_mod_abs.cluster_cytokines(K=args.bestK['abs'])
        tools.write_to_dill(os.path.join(args.paths['clustering'], 'cyto_mod_adj.dill'), args.cyto_mod_adj)
        tools.write_to_dill(os.path.join(args.paths['clustering'], 'cyto_mod_abs.dill'), args.cyto_mod_abs)
    else: # Read modules from file
        args.cyto_mod_adj = tools.read_from_dill(os.path.join(args.paths['clustering'], 'cyto_mod_adj.dill'))
        args.cyto_mod_abs = tools.read_from_dill(os.path.join(args.paths['clustering'], 'cyto_mod_abs.dill'))

    args.cyto_modules = {'adj': args.cyto_mod_adj, 'abs': args.cyto_mod_abs}
    return args

