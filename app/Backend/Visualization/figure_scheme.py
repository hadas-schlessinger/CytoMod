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
                        save_path=os.path.join(args.paths['correlation_figures'], '%s_correlation_heatmap.png' % args.cyto_mod_abs.name))
        #cytomod.io.plot_clustering_heatmap(args.cyto_modules['abs'], args.paths['clustering_figures'],figsize=(10, 6))
    elif stage == 'adj':
        plotHColCluster(args.cyto_mod_adj.cyDf, method='complete', metric='pearson-signed', figsize=(10, 6),
                        save_path=os.path.join(args.paths['correlation_figures'], '%s_correlation_heatmap.png' % args.cyto_mod_adj.name))


def mean_person(args):
    cyplot.plotMeanCorr(args.cyto_mod_abs.withMean, args.cyto_mod_abs.meanS.name,
                        cyList=sorted(args.cyto_mod_abs.cyDf.columns),
                        save_path=os.path.join(args.paths['correlation_figures'],
                                               '%s_cy_mean_correlation.png' % args.cyto_mod_abs.name))


def pairwise_corelletion_with_moudles(stage, args):
    cytomod.io.plot_clustering_heatmap(args.cyto_modules[stage], args.paths['clustering_figures'],
                                       figsize=(10, 6))
    cytomod.io.plot_color_legend(args.cyto_modules[stage], args.paths['clustering_figures'])


def same_cluster_reliability(stage,args):
    cytomod.io.plot_reliability(args.cyto_modules[stage], args.paths['clustering_figures'],
                                figsize=(10, 6))
    cytomod.io.plot_color_legend(args.cyto_modules[stage], args.paths['clustering_figures'])


def modules_cytokine_correlation(stage, args):
    cytomod.io.plot_module_correl(args.cyto_modules[stage], args.paths['clustering_figures'])


def write_results(args):
    cytomod.io.write_modules(args.cyto_modules['abs'], args.paths['clustering_info'])
    cytomod.io.write_modules(args.cyto_modules['adj'], args.paths['clustering_info'])


def associations_to_outcomes(stage, args):
    # standardize numeric covariates
    if args.covariates != []:
        standardizeFunc = lambda col: (col - np.nanmean(col)) / np.nanstd(col)

        for covariate in args.covariates:
            if len(args.patient_data[covariate].unique()) > 2:
                args.patient_data[[covariate]] = args.patient_data[[covariate]].apply(standardizeFunc)

        if stage == 'abs':
            args.mod_outcome_abs_df = outcome.outcomeAnalysis(args.cyto_modules['abs'], args.patient_data,
                                                         analyzeModules=True,
                                                         outcomeVars=args.outcomes,
                                                         adjustmentVars=args.covariates,
                                                         standardize=True)
            args.cy_outcome_abs_df = outcome.outcomeAnalysis(args.cyto_modules['abs'], args.patient_data,
                                                        analyzeModules=False,
                                                        outcomeVars=args.outcomes,
                                                        adjustmentVars=args.covariates,
                                                        standardize=True)
        elif stage == 'adj':
            args.mod_outcome_adj_df = outcome.outcomeAnalysis(args.cyto_modules['adj'], args.patient_data,
                                                         analyzeModules=True,
                                                         outcomeVars=args.outcomes,
                                                         adjustmentVars=args.covariates,
                                                         standardize=True)
            args.cy_outcome_adj_df = outcome.outcomeAnalysis(args.cyto_modules['adj'], args.patient_data,
                                                        analyzeModules=False,
                                                        outcomeVars=args.outcomes,
                                                        adjustmentVars=args.covariates,
                                                        standardize=True)


def figures(stage, args):
    if args.outcomes != []:
        if stage == 'abs':
            outcome.plotResultSummary(args.cyto_modules['abs'],
                                      args.mod_outcome_abs_df,
                                      args.cy_outcome_abs_df,
                                      args.outcomes,
                                      fdr_thresh_plot=0.2,
                                      compartmentName=args.name_compartment,
                                      figsize=(6, 9),
                                      save_fig_path=os.path.join(args.paths['association_figures'],
                                                                 'associations_abs.png'))
        elif stage == 'adj':
            outcome.plotResultSummary(args.cyto_modules['abs'],
                                      args.mod_outcome_abs_df,
                                      args.cy_outcome_abs_df,
                                      args.outcomes,
                                      fdr_thresh_plot=0.2,
                                      compartmentName=args.name_compartment,
                                      figsize=(6, 9),
                                      save_fig_path=os.path.join(args.paths['association_figures'],
                                                                 'associations_abs.png'))
