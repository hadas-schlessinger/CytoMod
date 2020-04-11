import os.path as op

# import plotting as cyplot
# from biplot import biplot
# import plotting as cyplot
# import cycluster as cy
import matplotlib.pyplot as plt
import scipy.stats.stats
import numpy as np
import palettable
import itertools
import seaborn as sns
import statsmodels as sm

# sys.path.append('C:/Users/liel-/PycharmProjects/LielTools/')
# from write2Excel import writeDF2Excel
# from dillReadWrite import writeDf2Dill

sns.set(style='darkgrid', font_scale=1.5, palette='muted')

####----------------- helpers --------------####
from copy import deepcopy
import seaborn as sns
# from glm_compare import compare_lr_test
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm

sns.set(style='darkgrid', palette='muted', font_scale=2.0)

def GLMResults(df, outcome, predictors, adj=[], logistic=True):
    if logistic:
        family = sm.families.Binomial()
        coefFunc = np.exp
        cols = ['OR', 'LL', 'UL', 'pvalue', 'Diff', 'N']
    else:
        family = sm.families.Gaussian()
        coefFunc = lambda x: x
        cols = ['Coef', 'LL', 'UL', 'pvalue', 'Diff', 'N']

    k = len(predictors)
    assoc = np.zeros((k, 6))
    params = []
    pvalues = []
    resObj = []
    for i, predc in enumerate(predictors):
        exogVars = list(set([predc] + adj))
        tmp = df[[outcome] + exogVars].dropna()

        model = sm.GLM(endog=tmp[outcome].astype(float), exog=sm.add_constant(tmp[exogVars].astype(float)),
                       family=family)
        try:
            res = model.fit()
            assoc[i, 0] = coefFunc(res.params[predc])
            assoc[i, 3] = res.pvalues[predc]
            assoc[i, 1:3] = coefFunc(res.conf_int().loc[predc])
            assoc[i, 4] = tmp[predc].loc[tmp[outcome] == 1].mean() - tmp[predc].loc[tmp[outcome] == 0].mean()
            params.append(res.params.to_dict())
            pvalues.append(res.pvalues.to_dict())
            resObj.append(res)
        except sm.tools.sm_exceptions.PerfectSeparationError:
            assoc[i, 0] = np.nan
            assoc[i, 3] = 0
            assoc[i, 1:3] = [np.nan, np.nan]
            assoc[i, 4] = tmp[predc].loc[tmp[outcome] == 1].mean() - tmp[predc].loc[tmp[outcome] == 0].mean()
            params.append({k: np.nan for k in [predc] + adj})
            pvalues.append({k: np.nan for k in [predc] + adj})
            resObj.append(None)
            print('PerfectSeparationError: %s with %s' % (predc, outcome))
        assoc[i, 5] = tmp.shape[0]
    outDf = pd.DataFrame(assoc[:, :6], index=predictors, columns=cols)
    outDf['params'] = params
    outDf['pvalues'] = pvalues
    outDf['res'] = resObj
    print(f'outDf = {outDf}')
    return outDf


def outcomeAnalysis(cytomod_obj, patient_data,
                    analyzeModules=True,
                    outcomeVars=[],
                    adjustmentVars=[],
                    standardize=True):
    need_OR = False
    df = pd.DataFrame(patient_data)
    modStr = 'Module' if analyzeModules else 'Analyte'
    resL = []
    for outcome in outcomeVars:
        logistic = np.isin(df[outcome].dropna().unique(), [0, 1]).all() # checks if the data is binary
        if logistic:
            need_OR = True
        """Logistic regression on outcome"""
        if analyzeModules:
            dataDf = cytomod_obj.modDf
        else:
            dataDf = cytomod_obj.cyDf
            if standardize:  # standardize cytokine values
                standardizeFunc = lambda col: (col - np.nanmean(col)) / np.nanstd(col)
                dataDf = dataDf.apply(standardizeFunc)

        predictors = dataDf.columns
        data_outcome_Df = patient_data[outcomeVars + adjustmentVars].join(dataDf)
        tmpres = GLMResults(data_outcome_Df, outcome, predictors, adj=adjustmentVars, logistic=logistic)
        tmpres['Outcome'] = outcome
        tmpres['Compartment'] = cytomod_obj.sampleStr
        tmpres['Adjusted'] = 'Yes' if cytomod_obj.adjusted else 'No'
        tmpres['Fold-diff'] = np.exp(tmpres['Diff'])
        tmpres[modStr] = predictors
        resL.append(tmpres)

    resDf = pd.concat(resL, axis=0, ignore_index=True)
    return resDf, need_OR


####### outcome #######
def mapColors2Labels(labels, setStr='MapSet', cmap=None):
    """Return pd.Series of colors based on labels"""
    if cmap is None:
        N = max(3, min(12, len(np.unique(labels))))
        cmap = palettable.colorbrewer.get_map(setStr, 'Qualitative', N).mpl_colors
        """Use B+W colormap"""
    cmapLookup = {k:col for k, col in zip(sorted(np.unique(labels)), itertools.cycle(cmap))}
    return labels.map(cmapLookup.get)


def adjust_pvals(res_df):
    res_df = deepcopy(res_df)
    res_df.loc[:, 'FWER'] = sm.stats.multipletests(res_df.pvalue.values, method='holm')[1]
    res_df.loc[:, 'FDR'] = sm.stats.multipletests(res_df.pvalue.values, method='fdr_bh')[1]
    res_df.loc[:, 'Bonferroni'] = sm.stats.multipletests(res_df.pvalue.values, method='bonferroni')[1]
    return res_df


def plotResultSummary(cytomod_obj,
                      mod_res_df,
                      cy_res_df,
                      outcomeVars,
                      fdr_thresh_plot=0.2,
                      compartmentName='BS',
                      showScalebar=True,
                      figsize=(6,9),
                      save_fig_path=None,
                      logistic=False):
    mod_res_df = mod_res_df.copy()
    cy_res_df = cy_res_df.copy()

    mod_res_df.loc[:, 'Name'] = mod_res_df['Module']
    cy_res_df.loc[:, 'Name'] = cy_res_df['Analyte']

    cy_res_df = adjust_pvals(cy_res_df)
    mod_res_df = adjust_pvals(mod_res_df)

    name2mod = lambda a: '%s%1.0f' % (compartmentName, cytomod_obj.labels[a])

    cy_res_df.loc[:, 'Module'] = cy_res_df['Analyte'].map(name2mod)
    if logistic:
       cols = ['Outcome', 'Name', 'Module', 'Fold-diff', 'OR', 'N', 'FWER', 'FDR']
    else:
       cols = ['Outcome', 'Name', 'Module', 'Fold-diff', 'Coef', 'N', 'FWER', 'FDR']

    hDf = pd.concat((mod_res_df[cols], cy_res_df[cols]), axis=0)
    hDf.loc[:, 'isAnalyte'] = (hDf['Module'] != hDf['Name'])
    order = hDf[['Module', 'Name', 'isAnalyte']].drop_duplicates().sort_values(by=['Module', 'isAnalyte', 'Name'])
    fdrH = hDf.pivot(index='Name', columns='Outcome', values='FDR').loc[order.Name, outcomeVars]
    fdrH = fdrH.fillna(1)
    fwerH = hDf.pivot(index='Name', columns='Outcome', values='FWER').loc[order.Name, outcomeVars]
    fwerH = fwerH.fillna(1)
    censorInd = fdrH.values > fdr_thresh_plot

    fdrH.values[censorInd] = 1.


    cmap = palettable.colorbrewer.diverging.PuOr_9_r.mpl_colormap

    if logistic:
        print("####starting logistic regression")
        foldH = hDf.pivot(index='Name', columns='Outcome', values='Fold-diff').loc[order.Name, outcomeVars]
        foldH.values[censorInd] = 1.
        foldH = foldH.fillna(1)
        scaleLabel = 'Odds Ratio'
        ytl = np.array(['1/2.5', '1/2', '1/1.5', 1, 1.5, 2, 2.5])
        yt = np.log([1 / 2.5, 1 / 2, 1 / 1.5, 1, 1.5, 2, 2.5])
        vals = np.log(foldH.values)
        pcParams = dict(vmin=-1, vmax=1, cmap=cmap)
        plt.figure(figsize=figsize)
        figh = plt.gcf()
        plt.clf()
        axh = figh.add_subplot(plt.GridSpec(1, 1, left=0.6, bottom=0.05, right=0.95, top=0.85)[0, 0])
        axh.grid(None)
        pcolOut = plt.pcolormesh(vals, **pcParams)
        plt.yticks(())
        plt.xticks(np.arange(fdrH.shape[1]) + 0.5, fdrH.columns, size=11, rotation=90)
        axh.xaxis.set_ticks_position('top')
        plt.xlim((0, fdrH.shape[1]))
        plt.ylim((0, fdrH.shape[0]))
        axh.invert_yaxis()
        for cyi, cy in enumerate(foldH.index):
            for outi, out in enumerate(foldH.columns):
                if fwerH.loc[cy, out] < 0.0005:
                    ann = '***'
                elif fwerH.loc[cy, out] < 0.005:
                    ann = '**'
                elif fwerH.loc[cy, out] < 0.05:
                    ann = '*'
                else:
                    ann = ''
                if not ann == '':
                    plt.annotate(ann, xy=(outi + 0.5, cyi + 0.75), weight='bold', size=14, ha='center', va='center')

        """Colorbar showing module membership: Add labels, make B+W"""
        cbAxh = figh.add_subplot(plt.GridSpec(1, 1, left=0.5, bottom=0.05, right=0.59, top=0.85)[0, 0])
        cbAxh.grid(None)
        cmap = [(0.3, 0.3, 0.3),
                (0.7, 0.7, 0.7)]
        cbS = mapColors2Labels(order.set_index('Name')['Module'], cmap=cmap)
        _ = cbAxh.imshow([[x] for x in cbS.values], interpolation='nearest', aspect='auto', origin='lower')
        plt.ylim((0, fdrH.shape[0]))
        plt.yticks(np.arange(fdrH.shape[0]), fdrH.index, size=11)
        plt.xlim((0, 0.5))
        plt.ylim((-0.5, fdrH.shape[0] - 0.5))
        plt.xticks(())
        cbAxh.invert_yaxis()
    else:
        print('######starting linear regression')
        betaVals = hDf.pivot(index='Name', columns='Outcome', values='Coef').loc[order.Name, outcomeVars]  # LIEL
        betaVals.values[censorInd] = 0.
        vals = betaVals.values
        pcParams = dict(vmin=-0.8, vmax=0.8, cmap=cmap)
        scaleLabel = 'Beta Coefficient'
        ytl = np.array([-0.8, -0.4, 0, 0.4, 0.8])
        yt = np.array([-0.8, -0.4, 0, 0.4, 0.8])
        plt.figure(figsize=figsize)
        figh = plt.gcf()
        plt.clf()
        axh = figh.add_subplot(plt.GridSpec(1, 1, left=0.6, bottom=0.05, right=0.95, top=0.85)[0, 0])
        axh.grid(None)
        pcolOut = plt.pcolormesh(vals, **pcParams)
        plt.yticks(())

        plt.xticks(np.arange(betaVals.shape[1]) + 0.5, betaVals.columns, size=11, rotation=90)
        axh.xaxis.set_ticks_position('top')
        plt.xlim((0, betaVals.shape[1]))
        plt.ylim((0, betaVals.shape[0]))
        axh.invert_yaxis()
        for cyi, cy in enumerate(betaVals.index):
            for outi, out in enumerate(betaVals.columns):
                if fwerH.loc[cy, out] < 0.0005:
                    ann = '***'
                elif fwerH.loc[cy, out] < 0.005:
                    ann = '**'
                elif fwerH.loc[cy, out] < 0.05:
                    ann = '*'
                else:
                    ann = ''
                if not ann == '':
                    plt.annotate(ann, xy=(outi + 0.5, cyi + 0.75), weight='bold', size=14, ha='center', va='center')

        """Colorbar showing module membership: Add labels, make B+W"""
        cbAxh = figh.add_subplot(plt.GridSpec(1, 1, left=0.5, bottom=0.05, right=0.59, top=0.85)[0, 0])
        cbAxh.grid(None)
        cmap = [(0.3, 0.3, 0.3),
                (0.7, 0.7, 0.7)]
        cbS = mapColors2Labels(order.set_index('Name')['Module'], cmap=cmap)
        _ = cbAxh.imshow([[x] for x in cbS.values], interpolation='nearest', aspect='auto', origin='lower')
        plt.ylim((0, betaVals.shape[0]))
        plt.yticks(np.arange(betaVals.shape[0]), betaVals.index, size=11)
        plt.xlim((0, 0.5))
        plt.ylim((-0.5, betaVals.shape[0] - 0.5))
        plt.xticks(())
        cbAxh.invert_yaxis()

    for lab in order['Module'].unique():
        y = np.mean(np.arange(order.shape[0])[np.nonzero(order['Module'] == lab)]) - 0.5
        plt.annotate(lab, xy=(0.25, y), ha='center', va='center', rotation=90, color='white', size=12)

    """Scale colorbar"""
    if showScalebar:
        scaleAxh = figh.add_subplot(plt.GridSpec(1, 1, left=0.1, bottom=0.87, right=0.2, top=0.98)[0, 0])
        cb = figh.colorbar(pcolOut, cax=scaleAxh, ticks=yt)
        cb.set_label(scaleLabel, size=9)
        cb.ax.set_yticklabels(ytl, fontsize=8)

    plt.show()

    if save_fig_path is None:
        plt.show()
    else:
        plt.savefig(save_fig_path)
