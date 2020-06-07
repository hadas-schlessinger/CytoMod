import os
# sys.path.append(os.path.join(os.getcwd(), 'cytomod', 'otherTools'))
import app.cytomod.assoc_to_outcome as outcome
from app.cytomod import plotting as cyplot
from app.cytomod.otherTools.hclusterplot import plotHColCluster
import numpy as np
import warnings
warnings.filterwarnings('ignore')
warnings.simplefilter('ignore')
import app.cytomod.io

def pairwise_person(stage, args):
    if stage == 'abs':
        plotHColCluster(args.cyto_mod_abs.cyDf, method='complete', metric='pearson-signed', figsize=(10, 6),
                        save_path=os.path.join(args.paths['correlation_figures_abs'], '%s_correlation_heatmap.png' % args.cyto_mod_abs.name))
    elif stage == 'adj':
        plotHColCluster(args.cyto_mod_adj.cyDf, method='complete', metric='pearson-signed', figsize=(10, 6),
                        save_path=os.path.join(args.paths['correlation_figures_adj'], '%s_correlation_heatmap.png' % args.cyto_mod_adj.name))
    return args


def mean_person(args):
    cyplot.plotMeanCorr(args.cyto_mod_abs.withMean, args.cyto_mod_abs.meanS.name,
                        cyList=sorted(args.cyto_mod_abs.cyDf.columns),
                        save_path=os.path.join(args.paths['overview'],
                                               '%s_cy_mean_correlation.png' % args.cyto_mod_abs.name))
    img = {'height': '800',
            'width': '400',
           'path': os.path.join(args.paths['overview'],
                                               '%s_cy_mean_correlation.png' % args.cyto_mod_abs.name),
           'headline': 'Absolute Cytokines Mean Correlation',
           'location': 'overview',
           'explanation': 'this plot demonstrates the correlations between cytokine levels and mean cytokine levels'
           }
    args.images.append(img)
    return args


def pairwise_correlation_with_moudles(stage, args):
    app.cytomod.io.plot_clustering_heatmap(args.cyto_modules[stage], args.paths[f'clustering_{stage}'],
                                           figsize=(10, 6))
    img = {'height': '700',
           'width': '1000',
           'path': args.paths[f'clustering_{stage}'] +  '/%s_hierchical_clust_heatmap.png' % args.cyto_modules[stage].name,
           'headline': 'Hierarchical Clustering Heatmap for %s Cytokines' % stage ,
          'location': f'clustering_{stage}',
           'explanation': f"Pairwise Pearson's correlations among the {stage} cytokine levels in the given cohort. Cytokines were sorted along both axes using hierarchical clustering (complete-linkage)"
           }
    args.images.append(img)
    return args

def same_cluster_reliability(stage,args):
    app.cytomod.io.plot_reliability(args.cyto_modules[stage], args.paths[f'clustering_{stage}'],
                                    figsize=(10, 6))
    app.cytomod.io.plot_color_legend(args.cyto_modules[stage], args.paths[f'clustering_{stage}'])
    img = {'height': '700',
           'width': '1000',
           'path': args.paths[f'clustering_{stage}'] + '/%s_reliability.png' % args.cyto_modules[stage].name,
           'headline': 'Reliability Figure Of Pairwise Correlations of %s Cytokines' % stage,
           'location': f'clustering_{stage}',
           'explanation': 'Heatmap of cytokine modules - Complete linkage clustering over the Pearson pairwise correlation similarity measure is used to cluster cytokines into K modules, where K is decided using the gap statistic. '
                          'A clustering reliability score is computed over 1, 000 samplings of subjects that are sampled with replacement. '
                          'The score for each pair of cytokines represents the fraction of times they clustered together across 1, 000 random samples. '
                          'The reliability score of the chosen K is presented here. The final modules are then constructed by clustering the pairwise reliability scores, and are represented by the colored stripes below the clustering dendrogram.'}
    args.images.append(img)
    img = {'height': '300',
           'width': '500',
           'path': args.paths[f'clustering_{stage}'] + '/%s_color_label_legend.png' % args.cyto_modules[stage].name,
           'headline': 'Modules Labels',
           'location': f'clustering_{stage}',
           'explanation': 'the modules are presented in the following colors'}
    args.images.append(img)
    return args


def modules_cytokine_correlation(stage, args):
    args = app.cytomod.io.plot_module_correl(args.cyto_modules[stage], args.paths[f'correlation_figures_{stage}'], args, stage)
    return args


def write_results(args):
    app.cytomod.io.write_modules(args.cyto_modules['abs'], args.paths['overview'])
    app.cytomod.io.write_modules(args.cyto_modules['adj'], args.paths['overview'])


def associations_to_outcomes(stage, args):
    # standardize numeric covariates
    standardizeFunc = lambda col: (col - np.nanmean(col)) / np.nanstd(col)

    if args.covariates != []:
        for covariate in args.covariates:
            if covariate != '':
                args.patient_data[[covariate]] = args.patient_data[[covariate]].apply(standardizeFunc)

    if args.outcomes != []:

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
                                      save_fig_path=os.path.join(args.paths['outcome_abs'],
                                                                 'associations_abs.png'),
                                      logistic= args.need_OR)
            img = {'height': '800',
                   'width': '400',
                   'path':os.path.join(args.paths['outcome_abs'],
                                                                 'associations_abs.png'),
                   'headline': 'Associations of Absolute Cytokines',
                   'location':'outcome_abs',
           'explanation': 'Absolute cytokine associations  with clinical phenotypes as well as the modules assosiations with those phenotypes. '
                          'Associations were identified using the relevant regression (linear for continues outcomes and logistic for binary outcomes) controlling for the inserted covariates. '
                          'Each cytokine or module is indicated along the rows, grouped by their assigned module. Heatmap color indicates the direction and magnitude of the regression coefficient between cytokine or module level with a given clinical phenotype. '
                          'Only associations with false-discovery rate (FDR)-adjusted q-value ≤ 0.2 are colored. Asterisks indicate family-wise error rate (FWER)-adjusted p-values with ***, **, and * indicating p ≤ 0.0005, 0.005, and 0.05, respectively.'}
            args.images.append(img)
        elif stage == 'adj':
            outcome.plotResultSummary(args.cyto_modules['adj'],
                                      args.mod_outcome_adj_df,
                                      args.cy_outcome_adj_df,
                                      args.outcomes,
                                      fdr_thresh_plot=0.2,
                                      compartmentName=args.name_compartment,
                                      figsize=(6, 9),
                                      save_fig_path=os.path.join(args.paths['outcome_adj'],
                                                                 'associations_adj.png'),
                                      logistic=args.need_OR)
            img = {'height': '800',
                   'width': '400',
                   'path': os.path.join(args.paths['outcome_adj'],
                                                                 'associations_adj.png'),
                   'headline': 'Associations of Adjusted Cytokines',
                   'location':'outcome_adj',
           'explanation': 'Adjusted cytokine associations with clinical phenotypes as well as the modules assosiations with those phenotypes. '
                          'Associations were identified using the relevant regression (linear for continues outcomes and logistic for binary outcomes) controlling for the inserted covariates. '
                          'Each cytokine or module is indicated along the rows, grouped by their assigned module. Heatmap color indicates the direction and magnitude of the regression coefficient between cytokine or module level with a given clinical phenotype. '
                          'Only associations with false-discovery rate (FDR)-adjusted q-value ≤ 0.2 are colored. Asterisks indicate family-wise error rate (FWER)-adjusted p-values with ***, **, and * indicating p ≤ 0.0005, 0.005, and 0.05, respectively.'}
            args.images.append(img)
    return args
