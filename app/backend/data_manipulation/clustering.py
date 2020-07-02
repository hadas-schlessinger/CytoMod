import random
from app.cytomod import run_gap_statistic as gap_stat
from app.backend import tools
import os


def best_k(args):
    if args.do_recalculate:
        random.seed(args.seed)  # set seed for random numbers stream
        args.bestK = {}
        args.bestK['adj'] = gap_stat.getBestK(args.cyto_mod_adj.cyDf,
                                              max_testing_k=args.max_testing_k,
                                              max_final_k=args.max_testing_k,
                                              save_fig_path=os.path.join(args.paths['clustering_adj'], 'gap_stat_adj.png'))
        img = {'height': '500',
               'width': '700',
               'headline': 'Gap Statistic (adjusted cytokines)',
                'path': os.path.join(args.paths['clustering_adj'], 'gap_stat_adj.png' ),
                 'location':'clustering_adj',
           'explanation': 'Automated selection of the optimal number of modules. '
                          'The Tibshirani gap statistic is used to automatically determine the optimal number of modules. '
                          'The cytokine profiles are clustered into several K clusters as inserted in the settings section and the optimal K is selected. '
                          'The plot shows the δ gap statistic, defined as Gap(K) − (Gap(K + 1) − Sk + 1) for as dependent in K. '
                          'The optimal number of modules is selected by identifying the first value of K for which this measure is positive or, if there are no positive values, the highest measurment'

               }
        args.images.append(img)
        args.bestK['abs'] = gap_stat.getBestK(args.cyto_mod_abs.cyDf,
                                              max_testing_k=args.max_testing_k,
                                              max_final_k=args.max_testing_k,
                                              save_fig_path=os.path.join(args.paths['clustering_abs'], 'gap_stat_abs.png'))
        img = {'height': '500',
               'width': '700',
               'headline': 'Gap Statistic (absolute cytokines)',
               'path': os.path.join(args.paths['clustering_abs'], 'gap_stat_abs.png'),
               'location': 'clustering_abs',
               'explanation': 'Automated selection of the optimal number of modules. '
                          'The Tibshirani gap statistic is used to automatically determine the optimal number of modules. '
                          'The cytokine profiles are clustered into several K clusters as inserted in the settings section and the optimal K is selected. '
                          'The plot shows the δ gap statistic, defined as Gap(K) − (Gap(K + 1) − Sk + 1) for as dependent in K. '
                          'The optimal number of modules is selected by identifying the first value of K for which this measure is positive or, is there are no positive values, the highest measurment'

               }
        args.images.append(img)

        tools.write_DF_to_excel(os.path.join(args.path_files, 'bestK.xlsx'), args.bestK)
    else:
        # Get modules from storage
        args.bestK = tools.read_excel(os.path.join(args.path_files, 'bestK.xlsx'))
        args.bestK = dict(args.bestK['value'])
    return args


def clustering(args):
    # Cluster and write modules to file
    if args.do_recalculate:
        args.cyto_mod_adj.cluster_cytokines(K=args.bestK['adj'])
        args.cyto_mod_abs.cluster_cytokines(K=args.bestK['abs'])
        tools.write_to_dill(os.path.join(args.paths['clustering_adj'], 'cyto_mod_adj.dill'), args.cyto_mod_adj)
        tools.write_to_dill(os.path.join(args.paths['clustering_abs'], 'cyto_mod_abs.dill'), args.cyto_mod_abs)
    else: # Read modules from file
        args.cyto_mod_adj = tools.read_from_dill(os.path.join(args.paths['clustering_adj'], 'cyto_mod_adj.dill'))
        args.cyto_mod_abs = tools.read_from_dill(os.path.join(args.paths['clustering_abs'], 'cyto_mod_abs.dill'))

    args.cyto_modules = {'adj': args.cyto_mod_adj, 'abs': args.cyto_mod_abs}
    return args

