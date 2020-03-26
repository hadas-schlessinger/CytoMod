import os
import sys
# sys.path.append(os.path.join(os.getcwd(), 'cytomod', 'otherTools'))
import cytomod
import cytomod.assoc_to_outcome as outcome
from cytomod import plotting as cyplot
from cytomod.otherTools.hclusterplot import plotHColCluster
import numpy as np
import warnings
warnings.filterwarnings('ignore')
warnings.simplefilter('ignore')


def pairwise_person(stage, args):
    if stage == 'abs':
        plotHColCluster(args.cyto_mod_abs.cyDf, method='complete', metric='pearson-signed', figsize=(10, 6),
                        save_path=os.path.join(args.path_files, '%s_correlation_heatmap.png' % args.cyto_mod_abs.name))
    elif stage == 'adj':
        plotHColCluster(args.cyto_mod_adj.cyDf, method='complete', metric='pearson-signed', figsize=(10, 6),
                        save_path=os.path.join(args.path_files, '%s_correlation_heatmap.png' % args.cyto_mod_adj.name))
    return args


def mean_person(args):
    cyplot.plotMeanCorr(args.cyto_mod_abs.withMean, args.cyto_mod_abs.meanS.name,
                        cyList=sorted(args.cyto_mod_abs.cyDf.columns),
                        save_path=os.path.join(args.path_files,
                                               '%s_cy_mean_correlation.png' % args.cyto_mod_abs.name))
    img = {'height': '1000',
           'width': '500',
           'name': '%s_cy_mean_correlation.png' % args.cyto_mod_abs.name,
           'headline': 'Absolute Cytokines Mean Correlation'
           }
    args.images.append(img)
    return args


def pairwise_corelletion_with_moudles(stage, args):
    cytomod.io.plot_clustering_heatmap(args.cyto_modules[stage], args.path_files,
                                       figsize=(10, 6))
    cytomod.io.plot_color_legend(args.cyto_modules[stage], args.path_files)
    img = {'height': '700',
           'width': '1000',
           'name': '%s_hierchical_clust_heatmap.png' % args.cyto_modules[stage].name,
           'headline': 'Hierarchical Clustering Heatmap for %s Cytokines' % stage
           }
    args.images.append(img)
    img = {'height': '300',
           'width': '500',
           'name':  '%s_color_label_legend.png' % args.cyto_modules[stage].name,
           'headline': 'Modules Labels'
           }
    args.images.append(img)
    return args

def same_cluster_reliability(stage,args):
    cytomod.io.plot_reliability(args.cyto_modules[stage], args.path_files,
                                figsize=(10, 6))
    cytomod.io.plot_color_legend(args.cyto_modules[stage], args.path_files)
    img = {'height': '700',
           'width': '1000',
           'name':'%s_reliability.png' % args.cyto_modules[stage].name,
           'headline': 'Reliability Figure Of Pairwise Correlations of %s Cytokines' % stage}
    args.images.append(img)
    img = {'height': '300',
           'width': '500',
           'name': '%s_color_label_legend.png' % args.cyto_modules[stage].name,
           'headline': 'Modules Labels'}
    args.images.append(img)
    return args


def modules_cytokine_correlation(stage, args):
    args = cytomod.io.plot_module_correl(args.cyto_modules[stage], args.path_files, args)
    return args


def write_results(args):
    cytomod.io.write_modules(args.cyto_modules['abs'], args.path_files)
    cytomod.io.write_modules(args.cyto_modules['adj'], args.path_files)


def associations_to_outcomes(stage, args):
    # standardize numeric covariates
    if args.covariates != []:
        standardizeFunc = lambda col: (col - np.nanmean(col)) / np.nanstd(col)

        for covariate in args.covariates:
            if covariate != '' and len(args.patient_data[covariate].unique()) > 2:
                args.patient_data[[covariate]] = args.patient_data[[covariate]].apply(standardizeFunc)

        if stage == 'abs':
            args.mod_outcome_abs_df, args.need_OR = outcome.outcomeAnalysis(args.cyto_modules['abs'], args.patient_data,
                                                         analyzeModules=True,
                                                         outcomeVars=args.outcomes if args.outcomes[0] != '' else [],
                                                         adjustmentVars=args.covariates if args.covariates[0] != '' else [],
                                                         standardize=True)
            args.cy_outcome_abs_df,  args.need_OR = outcome.outcomeAnalysis(args.cyto_modules['abs'], args.patient_data,
                                                        analyzeModules=False,
                                                        outcomeVars=args.outcomes if args.outcomes[0] != '' else [],
                                                        adjustmentVars=args.covariates if args.covariates[0] != '' else [],
                                                        standardize=True)
        if stage == 'adj':
            args.mod_outcome_adj_df,  args.need_OR = outcome.outcomeAnalysis(args.cyto_modules['adj'], args.patient_data,
                                                         analyzeModules=True,
                                                         outcomeVars=args.outcomes if args.outcomes[0] != '' else [],
                                                         adjustmentVars=args.covariates if args.covariates[0] != '' else [],
                                                         standardize=True)
            args.cy_outcome_adj_df,  args.need_OR = outcome.outcomeAnalysis(args.cyto_modules['adj'], args.patient_data,
                                                        analyzeModules=False,
                                                        outcomeVars=args.outcomes if args.outcomes[0] != '' else [],
                                                        adjustmentVars=args.covariates if args.covariates[0] != '' else [],
                                                        standardize=True)
    return args


def outcomes_figures(stage, args):
    if args.outcomes != []:
        if stage == 'abs':
            outcome.plotResultSummary(args.cyto_modules['abs'],
                                      args.mod_outcome_abs_df,
                                      args.cy_outcome_abs_df,
                                      args.outcomes,
                                      fdr_thresh_plot=0.2,
                                      compartmentName=args.name_compartment,
                                      figsize=(6, 9),
                                      save_fig_path=os.path.join(args.path_files,
                                                                 'associations_abs.png'),
                                      logistic= args.need_OR)
            img = {'height': '1000',
                   'width': '500',
                   'name':'associations_abs.png',
                   'headline': 'Associations of Absolute Cytokines'}
            args.images.append(img)
        elif stage == 'adj':
            outcome.plotResultSummary(args.cyto_modules['adj'],
                                      args.mod_outcome_adj_df,
                                      args.cy_outcome_adj_df,
                                      args.outcomes,
                                      fdr_thresh_plot=0.2,
                                      compartmentName=args.name_compartment,
                                      figsize=(6, 9),
                                      save_fig_path=os.path.join(args.path_files,
                                                                 'associations_adj.png'),
                                      logistic=args.need_OR)
            img = {'height': '1000',
                   'width': '500',
                   'name': 'associations_adj.png',
                   'headline': 'Associations of Adjusted Cytokines'}
            args.images.append(img)
    return args