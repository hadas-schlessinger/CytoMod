from mycompile import mycompile

from dfprint import toPDF, toPNG
import matplotlib.pyplot as plt
import statsmodels.api as sm
import palettable
import seaborn as sns
import itertools
from cycluster import plotting as cyplot
import cycluster as cy
import scipy

sys.path.append('C:/Users/liel-/PycharmProjects/LielTools/')
from write2Excel import writeDF2Excel
from dillReadWrite import writeDf2Dill

sns.set(style='darkgrid', palette='muted', font_scale=1.5)

ff = lambda f: '%1.2g' % f


def addOutcomeVars(df, standardize=False):
    out = df.join(ptidDf, rsuffix='_ptid')
    symptoms = sliceByDay(
        symptomDf[['Total', 'Systemic', 'Upper RT', 'Lower RT', 'Any LRT', 'Gastrointestinal', 'Day']],
        day=early).copy()

    if (standardize):
        standardizeFunc = lambda col: (col - np.nanmean(col)) / np.nanstd(col)
        symptoms.loc[:, ['Total', 'Systemic', 'Upper RT', 'Lower RT', 'Gastrointestinal']] = symptoms.loc[:,
                                                                                             ['Total', 'Systemic',
                                                                                              'Upper RT', 'Lower RT',
                                                                                              'Gastrointestinal']].apply(
            standardizeFunc)

    out = out.join(symptoms, rsuffix='_symptom')

    logVL = sliceByDay(viralDf[['log-VL', 'Day']], day=early).copy()

    out = out.drop(['Age'], axis=1)

    if (standardize):
        logVL.loc[:, ['log-VL']] = logVL.loc[:, ['log-VL']].apply(standardizeFunc)

    out = out.join(logVL, rsuffix='_viral')
    out = out.join(illnessDf[severeIllness + ['Severe Illness']], rsuffix='_ill')

    if (standardize):
        out.loc[:, ['log-Age']] = out.loc[:, ['log-Age']].apply(standardizeFunc)

    return out


def GLMResults(df, outcome, predictors, adj=[], logistic=True):
    print("called GLMResults with \noutcome: " + outcome + "\npredictors: " + str(predictors) + "\nadj: " + str(adj))
    if logistic:
        family = sm.families.Binomial()
        coefFunc = np.exp
        cols = ['OR', 'LL', 'UL', 'pvalue', 'Diff']
    else:
        family = sm.families.Gaussian()
        coefFunc = lambda x: x
        cols = ['Coef', 'LL', 'UL', 'pvalue', 'Diff']
    k = len(predictors)
    assoc = np.zeros((k, 6))
    params = []
    pvalues = []
    for i, predc in enumerate(predictors):
        exogVars = list(set([predc] + adj))
        if (outcome == 'log-VL' and ('log-VL' in adj)):  # LIEL added
            exogVars.remove('log-VL')
        tmp = df[[outcome] + exogVars].dropna()
        # print("********** GLM outcome df shape (supposed to be 1 column): "+ str(tmp[outcome].shape))
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
        except sm.tools.sm_exceptions.PerfectSeparationError:
            assoc[i, 0] = np.nan
            assoc[i, 3] = 0
            assoc[i, 1:3] = [np.nan, np.nan]
            assoc[i, 4] = tmp[predc].loc[tmp[outcome] == 1].mean() - tmp[predc].loc[tmp[outcome] == 0].mean()
            params.append({k: np.nan for k in [predc] + adj})
            pvalues.append({k: np.nan for k in [predc] + adj})
            print('PerfectSeparationError: %s with %s' % (predc, outcome))
        print("finished calculating GLM for: " + predc)
    outDf = pd.DataFrame(assoc[:, :5], index=predictors, columns=cols)
    outDf['params'] = params
    outDf['pvalues'] = pvalues
    print("finished running GLMResults")
    return outDf


def outcomeAnalysis(ds, outcomeVars, binaryOutcomes=False, analyzeModules=True, dsKeys=None,
                    adjustmentVars=[[], ['log-Age']], adjustmentStrs=['NoAdj', 'AgeAdj'], standardize=False):
    print("started outcomeAnalysis for outcomeVars: " + str(outcomeVars))
    if dsKeys is None:
        dsKeys = ['nw', 'pb', 'npb', 'nnw']
    modStr = 'Module' if analyzeModules else 'Analyte'
    resL = []
    for adjVars, adjStr in zip(adjustmentVars, adjustmentStrs):
        for bv in outcomeVars:
            print("########## started oucomeAnalysis for outcomeVar: " + bv)
            for s in dsKeys:
                print("#### started oucomeAnalysis for key: " + s)
                if analyzeModules:  # analyze modules (already standardized)
                    dataDf = ds[s].modDf
                else:  # analyze cytokines
                    dataDf = ds[s].cyDf
                    if standardize:  # LIEL - standardize cytokine values
                        standardizeFunc = lambda col: (col - np.nanmean(col)) / np.nanstd(col)
                        dataDf = dataDf.apply(standardizeFunc)

                tmpDf = addOutcomeVars(dataDf.join(ds[s].meanS), standardize=standardize)
                tmpVars = dataDf.columns.tolist()
                if s[0] == 'n':
                    """Only test mean as predictor once (when its a normed compartment)"""
                    # tmpVars += [ds[s].meanS.name] # LIEL i don't want the mean to be analyzed

                tmpres = GLMResults(tmpDf, bv, tmpVars, adj=adjVars, logistic=binaryOutcomes)
                tmpres['Model'] = adjStr
                tmpres['Outcome'] = bv
                tmpres['Compartment'] = ds[s].sampleStr
                tmpres['Normalized'] = 'Yes' if ds[s].normed else 'No'
                tmpres['Fold-diff'] = np.exp(tmpres['Diff'])
                tmpres[modStr] = tmpVars
                resL.append(tmpres)
    resDf = pd.concat(resL, axis=0, ignore_index=True)
    print("finished outcomeAnalysis for outcomeVars: " + str(outcomeVars))
    return resDf


def singleOutcomeBoxplot(cyDf, cyVar, outcomeVar, axh=None):
    if axh is None:
        axh = plt.gca()
    tmp = cyDf.copy()
    if set(cyDf[outcomeVar].dropna().unique()) == {0, 1}:
        tmp[outcomeVar] = tmp[outcomeVar].map({1: 'Yes', 0: 'No'})
        order = ['No', 'Yes']
    else:
        order = None

    axh.cla()
    sns.boxplot(y=cyVar, x=outcomeVar, data=tmp, ax=axh, order=order, fliersize=0)
    sns.stripplot(y=cyVar, x=outcomeVar, data=tmp, jitter=True, ax=axh, order=order)


def cyOutcomeScatter(resDf, outcomeVars=['Severe Illness'], adjustVar='NoAdj', normalized=True, plotLabels=True,
                     value='Fold-diff'):
    if normalized:
        normalizedVar = 'Yes'
    else:
        normalizedVar = 'No'

    ORTicks = [0.1, 0.2, 0.3, 0.5, 0.7, 1, 1.5, 2, 3, 5, 10]
    colors = palettable.colorbrewer.qualitative.Set1_4.mpl_colors
    cols = ['Compartment', 'Analyte', value]

    plt.clf()
    figh = plt.gcf()
    axh = figh.add_axes([0.1, 0.1, 0.8, 0.8], aspect='equal')
    if isinstance(outcomeVars, str) or len(outcomeVars) == 1:
        plt.title(outcomeVars[0], size='xx-large', weight='bold')
        tmp = \
        resDf.loc[(resDf.Normalized == normalizedVar) & (resDf.Model == adjustVar) & (resDf.Outcome == outcomeVars[0])][
            cols]
        tmp = tmp.pivot(index='Analyte', columns='Compartment', values=value)
        tmp = np.log(tmp)
        plt.scatter(tmp.NW.values, tmp.PB.values, color=colors[0], s=50, alpha=0.6)
        if plotLabels:
            for cy in tmp.index:
                if np.all(~np.isnan(tmp.loc[cy, ['NW', 'BS']])):
                    plt.annotate(cy, xy=(tmp.loc[cy, 'NW'], tmp.loc[cy, 'BS']),
                                 xytext=(3, 3),
                                 ha='left',
                                 va='bottom',
                                 textcoords='offset points',
                                 size='small')
        mx = max(np.abs(tmp.NW).max(), np.abs(tmp.PB).max())
    else:
        plt.title('%s to %s' % tuple(outcomeVars), size='xx-large', weight='bold')
        tmp = {}
        mx = {}
        for ov, color in zip(outcomeVars, colors):
            tmp[ov] = \
            resDf.loc[(resDf.Normalized == normalizedVar) & (resDf.Model == adjustVar) & (resDf.Outcome == ov)][cols]
            tmp[ov] = tmp[ov].pivot(index='Analyte', columns='Compartment', values=value)
            tmp[ov] = np.log(tmp[ov])
            plt.scatter(tmp[ov].NW.values, tmp[ov].PB.values, color=color, s=50, alpha=1, zorder=5)
            mx[ov] = max(np.abs(tmp[ov].NW).max(), np.abs(tmp[ov].PB).max())
        if plotLabels:
            for cy in tmp[outcomeVars[0]].index:
                if np.all(~np.isnan(tmp[outcomeVars[0]].loc[cy, ['NW', 'BS']])):
                    plt.annotate(cy, xy=(tmp[outcomeVars[0]].loc[cy, 'NW'], tmp[outcomeVars[0]].loc[cy, 'BS']),
                                 xytext=(3, 3),
                                 ha='left',
                                 va='bottom',
                                 textcoords='offset points',
                                 size='small')

        for a in tmp[outcomeVars[0]].index:
            x = [tmp[outcomeVars[0]].loc[a, 'NW'], tmp[outcomeVars[1]].loc[a, 'NW']]
            y = [tmp[outcomeVars[0]].loc[a, 'BS'], tmp[outcomeVars[1]].loc[a, 'BS']]
            # plt.plot(x, y, 'k-')
            plt.annotate('',
                         xy=(x[1], y[1]), xycoords='data',
                         xytext=(x[0], y[0]), textcoords='data',
                         size=10, va="bottom", ha="left",
                         bbox=dict(boxstyle="round", fc="w"),
                         arrowprops=dict(arrowstyle="wedge",
                                         connectionstyle="arc3,rad=0.0",
                                         relpos=(0, 0),
                                         fc="k"))

        mx = max(mx[outcomeVars[0]], mx[outcomeVars[1]])

    lims = (-mx * 1.1, mx * 1.1)

    plt.axis('scaled')
    plt.plot([0, 0], np.array(lims) * 10, '--', color='gray')
    plt.plot(np.array(lims) * 10, [0, 0], '--', color='gray')
    plt.xlabel('NW %s' % value)
    plt.ylabel('PB %s' % value)
    plt.xticks(np.log(ORTicks), ORTicks)
    plt.yticks(np.log(ORTicks), ORTicks)
    if value == 'OR':
        plt.xlim((np.log([1 / 10., 10])))
        plt.ylim((np.log([1 / 10., 10])))
    else:
        plt.xlim((np.log([1 / 3., 3])))
        plt.ylim((np.log([1 / 3., 3])))
    plt.xlim(lims)
    plt.ylim(lims)


'''
binVars = severeIllness + ['Severe Illness']
binVars.remove('Death')
binVars.remove('Intensive Care Unit')
'''

# binVars = ['Hospitalization', 'Any LRT']
'''
bvResDf = outcomeAnalysis(ds, outcomeVars=binVars, binaryOutcomes=True, analyzeModules=True)
bvResDf['Age_p'] = bvResDf.pvalues.map(lambda d: d.get('log-Age', np.nan))
bvResDf['Age_coef'] = bvResDf.params.map(lambda d: np.exp(d.get('log-Age', np.nan)))
bvResDf['VL_p'] = bvResDf.pvalues.map(lambda d: d.get('log-VL', np.nan))
bvResDf['VL_coef'] = bvResDf.params.map(lambda d: np.exp(d.get('log-VL', np.nan)))
bvResDf['FWER'] = sm.stats.multipletests(bvResDf.pvalue.values, method='holm')[1]
bvResDf['FDR'] = sm.stats.multipletests(bvResDf.pvalue.values, method='fdr_bh')[1]

bvCyDf = outcomeAnalysis(ds, outcomeVars=binVars, binaryOutcomes=True, analyzeModules=False)
bvCyDf['Age_p'] = bvCyDf.pvalues.map(lambda d: d.get('log-Age', np.nan))
bvCyDf['Age_coef'] = bvCyDf.params.map(lambda d: np.exp(d.get('log-Age', np.nan)))
bvCyDf['VL_p'] = bvCyDf.pvalues.map(lambda d: d.get('log-VL', np.nan))
bvCyDf['VL_coef'] = bvCyDf.params.map(lambda d: np.exp(d.get('log-VL', np.nan)))
bvCyDf['FWER'] = sm.stats.multipletests(bvCyDf.pvalue.values, method='holm')[1]
bvCyDf['FDR'] = sm.stats.multipletests(bvCyDf.pvalue.values, method='fdr_bh')[1]
'''


def mapColors2Labels(labels, setStr='Set3', cmap=None):
    """Return pd.Series of colors based on labels"""
    if cmap is None:
        N = max(3, min(12, len(np.unique(labels))))
        # cmap = palettable.colorbrewer.get_map(setStr, 'Qualitative', N).mpl_colors
        """Use B+W colormap"""
    cmapLookup = {k: col for k, col in zip(sorted(np.unique(labels)), itertools.cycle(cmap))}
    return labels.map(cmapLookup.get)


def plotResultSummary(ds, resDf,
                      cyResDf,
                      foldChange,
                      qthreshInc=1, qthreshPlot=0.2, cyclustObject=None,
                      compartment='BS',  # LIEL - changed from BS
                      normalized='Yes',
                      sigCol='FDR',
                      scalebar=True,
                      outcomes=['Hospitalization', 'Emergency Room', 'Missed Work/School', 'Severe Illness'],
                      adjusted=True,
                      associatMeasure='Fold-diff'):  # LIEL - added
    resDf.loc[:, 'Name'] = resDf['Module']
    cyResDf.loc[:, 'Name'] = cyResDf['Analyte']
    # outcomes = ['Hospitalization', 'Emergency Room', 'Missed Work/School', 'Severe Illness'] # LIEL - deleted

    if adjusted:
        adjVal = 'AgeAdj'  ##### LIEL - or AgeVLAdj! decided to adjust with age only. See OneNote
    else:
        adjVal = 'NoAdj'
    modInd = (resDf['Model'] == adjVal) & (resDf['Normalized'] == normalized) & (resDf['Outcome'].isin(outcomes)) & (
                resDf['Compartment'] == compartment) & (~resDf['Module'].isin(['Mean']))

    if compartment == 'Core':
        cycompartment = 'BS'
    else:
        cycompartment = compartment

    cyInd = (cyResDf['Model'] == adjVal) & (cyResDf['Normalized'] == normalized) & (
        cyResDf['Outcome'].isin(outcomes)) & (cyResDf['Compartment'] == cycompartment) & (
                ~cyResDf['Analyte'].isin(['Total Protein', 'Mean']))

    tmp = cyResDf.loc[cyInd, :].copy()
    tmpMod = resDf.loc[modInd, :].copy()
    tmp['FWER'] = sm.stats.multipletests(tmp.pvalue.values, method='holm')[1]
    tmp['FDR'] = sm.stats.multipletests(tmp.pvalue.values, method='fdr_bh')[1]
    tmpMod['FWER'] = sm.stats.multipletests(tmpMod.pvalue.values, method='holm')[1]
    tmpMod['FDR'] = sm.stats.multipletests(tmpMod.pvalue.values, method='fdr_bh')[1]

    modInd = (tmpMod[sigCol] <= qthreshInc)
    cyInd = (tmp[sigCol] <= qthreshInc)

    tmp = tmp.loc[cyInd, :]

    if cyclustObject != None:
        cyInd = (tmp['Analyte'].isin(cyclustObject.cyDf.columns))
        tmp = tmp.loc[cyInd, :]

    if cyclustObject == None:
        if (compartment == 'BS' or compartment == 'BS'):  # LIEL
            if (normalized == 'Yes'):
                name2mod = lambda a: '%s%1.0f' % (compartment, ds['npb'].labels[a])
            elif (normalized == 'No'):
                name2mod = lambda a: '%s%1.0f' % (compartment, ds['pb'].labels[a])
            else:
                print('wrong normalized value in plotResultSummary_beta')
        elif compartment == 'NW':
            if (normalized == 'Yes'):
                name2mod = lambda a: '%s%1.0f' % (compartment, ds['nnw'].labels[a])
            elif (normalized == 'No'):
                name2mod = lambda a: '%s%1.0f' % (compartment, ds['nw'].labels[a])
            else:
                print('wrong normalized value in plotResultSummary')
    else:
        name2mod = lambda a: '%s%1.0f' % (compartment, cyclustObject.labels[a])

    tmp.loc[:, 'Module'] = tmp['Analyte'].map(name2mod)
    if ('Coef' in cyResDf.columns):
        cols = ['Outcome', 'Name', 'Module', 'Fold-diff', 'Coef', 'FWER', 'FDR']  # LIEL
    else:
        cols = ['Outcome', 'Name', 'Module', 'Fold-diff', 'OR', 'FWER', 'FDR']

    hDf = pd.concat((tmpMod.loc[modInd, cols], tmp[cols]), axis=0)
    hDf.loc[:, 'isAnalyte'] = (hDf['Module'] != hDf['Name'])
    order = hDf[['Module', 'Name', 'isAnalyte']].drop_duplicates().sort_values(by=['Module', 'isAnalyte', 'Name'])
    fdrH = hDf.pivot(index='Name', columns='Outcome', values='FDR').loc[order.Name, outcomes]
    fdrH = fdrH.fillna(1)
    fwerH = hDf.pivot(index='Name', columns='Outcome', values='FWER').loc[order.Name, outcomes]
    fwerH = fwerH.fillna(1)
    foldH = hDf.pivot(index='Name', columns='Outcome', values=associatMeasure).loc[order.Name, outcomes]

    censorInd = fdrH.values > qthreshPlot
    """Use fold-change as threshold?"""
    # censorInd = np.abs(np.log(foldH.values)) <= np.log(1.5)

    fdrH.values[censorInd] = 1.
    foldH.values[censorInd] = 1.
    foldH = foldH.fillna(1)

    if foldChange:
        # cmap = palettable.colorbrewer.diverging.RdGy_9.mpl_colormap
        # cmap = palettable.colorbrewer.diverging.RdYlGn_9_r.mpl_colormap
        # cmap = palettable.colorbrewer.diverging.RdBu_9_r.mpl_colormap
        cmap = palettable.colorbrewer.diverging.PuOr_9_r.mpl_colormap

        vals = np.log(foldH.values)
        pcParams = dict(vmin=-1, vmax=1, cmap=cmap)
        scaleLabel = associatMeasure
        ytl = np.array(['1/2.5', '1/2', '1/1.5', 1, 1.5, 2, 2.5])
        yt = np.log([1 / 2.5, 1 / 2., 1 / 1.5, 1, 1.5, 2, 2.5])
    else:
        # cmap = palettable.colorbrewer.sequential.YlOrRd_9.mpl_colormap
        cmap = palettable.colorbrewer.sequential.Blues_9.mpl_colormap
        vals = (-10 * np.log10(fdrH)).values
        pcParams = dict(vmin=0, vmax=30, cmap=cmap)
        scaleLabel = '%s-adj p' % sigCol
        yt = -10 * np.log10(np.array([0.001, 0.01, 0.1, 1]))
        ytl = ['$10^{-3}$', '$10^{-2}$', '$10^{-1}$', '$1$']

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
    if foldChange:
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
    for lab in order['Module'].unique():
        y = np.mean(np.arange(order.shape[0])[np.nonzero(order['Module'] == lab)]) - 0.5
        plt.annotate(lab, xy=(0.25, y), ha='center', va='center', rotation=90, color='white', size=12)

    """Scale colorbar"""
    if scalebar:
        scaleAxh = figh.add_subplot(plt.GridSpec(1, 1, left=0.1, bottom=0.87, right=0.2, top=0.98)[0, 0])
        cb = figh.colorbar(pcolOut, cax=scaleAxh, ticks=yt)
        cb.set_label(scaleLabel, size=9)
        # cb.set_ticks(yt)
        cb.ax.set_yticklabels(ytl, fontsize=8)


def plotResultSummary_beta(ds, resDf,
                           cyResDf,
                           qthreshInc=1, qthreshPlot=0.2, cyclustObject=None,
                           compartment='BS',  # LIEL - changed from BS
                           normalized='Yes',
                           sigCol='FDR',
                           scalebar=True,
                           outcomes=['Hospitalization', 'Emergency Room', 'Missed Work/School', 'Severe Illness'],
                           # LIEL - added
                           adjusted=True):  # LIEL - added
    resDf.loc[:, 'Name'] = resDf['Module']
    cyResDf.loc[:, 'Name'] = cyResDf['Analyte']

    if adjusted:
        adjVal = 'AgeAdj'  ##### LIEL - or AgeVLAdj! decided to adjust with age only. See OneNote
    else:
        adjVal = 'NoAdj'
    modInd = (resDf['Model'] == adjVal) & (resDf['Normalized'] == normalized) & (resDf['Outcome'].isin(outcomes)) & (
                resDf['Compartment'] == compartment) & (~resDf['Module'].isin(['Mean']))

    if compartment == 'Core':
        cycompartment = 'BS'
    else:
        cycompartment = compartment

    cyInd = (cyResDf['Model'] == adjVal) & (
            cyResDf['Normalized'] == normalized) & (cyResDf['Outcome'].isin(outcomes)) & (
                    cyResDf['Compartment'] == cycompartment) & (
                ~cyResDf['Analyte'].isin(['Total Protein', 'Mean']))

    tmp = cyResDf.loc[cyInd, :].copy()
    tmpMod = resDf.loc[modInd, :].copy()
    tmp['FWER'] = sm.stats.multipletests(tmp.pvalue.values, method='holm')[1]
    tmp['FDR'] = sm.stats.multipletests(tmp.pvalue.values, method='fdr_bh')[1]
    tmpMod['FWER'] = sm.stats.multipletests(tmpMod.pvalue.values, method='holm')[1]
    tmpMod['FDR'] = sm.stats.multipletests(tmpMod.pvalue.values, method='fdr_bh')[1]

    modInd = (tmpMod[sigCol] <= qthreshInc)
    cyInd = (tmp[sigCol] <= qthreshInc)

    tmp = tmp.loc[cyInd, :]

    if cyclustObject != None:
        cyInd = (tmp['Analyte'].isin(cyclustObject.cyDf.columns))
        tmp = tmp.loc[cyInd, :]

    if cyclustObject == None:
        if (compartment == 'BS' or compartment == 'BS'):  # LIEL
            if (normalized == 'Yes'):
                name2mod = lambda a: '%s%1.0f' % (compartment, ds['npb'].labels[a])
            elif (normalized == 'No'):
                name2mod = lambda a: '%s%1.0f' % (compartment, ds['pb'].labels[a])
            else:
                print('wrong normalized value in plotResultSummary_beta')
        elif compartment == 'NW':
            if (normalized == 'Yes'):
                name2mod = lambda a: '%s%1.0f' % (compartment, ds['nnw'].labels[a])
            elif (normalized == 'No'):
                name2mod = lambda a: '%s%1.0f' % (compartment, ds['nw'].labels[a])
            else:
                print('wrong normalized value in plotResultSummary_beta')
    else:
        name2mod = lambda a: '%s%1.0f' % (compartment, cyclustObject.labels[a])

    tmp.loc[:, 'Module'] = tmp['Analyte'].map(name2mod)
    if ('Coef' in cyResDf.columns):
        cols = ['Outcome', 'Name', 'Module', 'Fold-diff', 'Coef', 'FWER', 'FDR']  # LIEL
    else:
        cols = ['Outcome', 'Name', 'Module', 'Fold-diff', 'OR', 'FWER', 'FDR']

    hDf = pd.concat((tmpMod.loc[modInd, cols], tmp[cols]), axis=0)
    hDf.loc[:, 'isAnalyte'] = (hDf['Module'] != hDf['Name'])
    order = hDf[['Module', 'Name', 'isAnalyte']].drop_duplicates().sort_values(by=['Module', 'isAnalyte', 'Name'])
    fdrH = hDf.pivot(index='Name', columns='Outcome', values='FDR').loc[order.Name, outcomes]
    fdrH = fdrH.fillna(1)
    fwerH = hDf.pivot(index='Name', columns='Outcome', values='FWER').loc[order.Name, outcomes]
    fwerH = fwerH.fillna(1)
    foldH = hDf.pivot(index='Name', columns='Outcome', values='Fold-diff').loc[order.Name, outcomes]

    betaVals = hDf.pivot(index='Name', columns='Outcome', values='Coef').loc[order.Name, outcomes]  # LIEL

    censorInd = fdrH.values > qthreshPlot
    """Use fold-change as threshold?"""
    # censorInd = np.abs(np.log(foldH.values)) <= np.log(1.5)

    fdrH.values[censorInd] = 1.
    foldH.values[censorInd] = 1.
    foldH = foldH.fillna(1)
    betaVals.values[censorInd] = 0.

    cmap = palettable.colorbrewer.diverging.PuOr_9_r.mpl_colormap
    vals = betaVals.values
    # pcParams = dict(vmin=-0.7, vmax=0.7, cmap=cmap)
    pcParams = dict(vmin=-0.8, vmax=0.8, cmap=cmap)
    scaleLabel = 'Beta Coefficient'
    # ytl = np.array([-0.7, -0.35,  0, 0.35, 0.7])
    # yt = np.array([-0.7, -0.35,  0, 0.35, 0.7])
    ytl = np.array([-0.8, -0.4, 0, 0.4, 0.8])
    yt = np.array([-0.8, -0.4, 0, 0.4, 0.8])

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
    # if foldChange:
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
    if scalebar:
        scaleAxh = figh.add_subplot(plt.GridSpec(1, 1, left=0.1, bottom=0.87, right=0.2, top=0.98)[0, 0])
        cb = figh.colorbar(pcolOut, cax=scaleAxh, ticks=yt)
        cb.set_label(scaleLabel, size=9)
        # cb.set_ticks(yt)
        cb.ax.set_yticklabels(ytl, fontsize=8)


def plotResultSummary_beta_reverse(ds, resDf,
                                   cyResDf,
                                   FWERthreshInc=1, FWERthreshPlot=0.2, cyclustObject=None,
                                   compartment='BS',  # LIEL - changed from BS
                                   normalized='Yes',
                                   sigCol='FWER',
                                   scalebar=True,
                                   outcomes=['Hospitalization', 'Emergency Room', 'Missed Work/School',
                                             'Severe Illness'],  # LIEL - added
                                   adjusted=True):  # LIEL - added
    resDf.loc[:, 'Name'] = resDf['Module']
    cyResDf.loc[:, 'Name'] = cyResDf['Analyte']

    if adjusted:
        adjVal = 'AgeAdj'  ##### LIEL - or AgeVLAdj! decided to adjust with age only. See OneNote
    else:
        adjVal = 'NoAdj'
    modInd = (resDf['Model'] == adjVal) & (resDf['Normalized'] == normalized) & (resDf['Outcome'].isin(outcomes)) & (
                resDf['Compartment'] == compartment) & (~resDf['Module'].isin(['Mean']))

    if compartment == 'Core':
        cycompartment = 'BS'
    else:
        cycompartment = compartment

    cyInd = (cyResDf['Model'] == adjVal) & (
            cyResDf['Normalized'] == normalized) & (cyResDf['Outcome'].isin(outcomes)) & (
                    cyResDf['Compartment'] == cycompartment) & (
                ~cyResDf['Analyte'].isin(['Total Protein', 'Mean']))

    tmp = cyResDf.loc[cyInd, :].copy()
    tmpMod = resDf.loc[modInd, :].copy()
    tmp['FWER'] = sm.stats.multipletests(tmp.pvalue.values, method='holm')[1]
    tmp['FDR'] = sm.stats.multipletests(tmp.pvalue.values, method='fdr_bh')[1]
    tmpMod['FWER'] = sm.stats.multipletests(tmpMod.pvalue.values, method='holm')[1]
    tmpMod['FDR'] = sm.stats.multipletests(tmpMod.pvalue.values, method='fdr_bh')[1]

    modInd = (tmpMod[sigCol] <= FWERthreshInc)
    cyInd = (tmp[sigCol] <= FWERthreshInc)

    tmp = tmp.loc[cyInd, :]

    if cyclustObject != None:
        cyInd = (tmp['Analyte'].isin(cyclustObject.cyDf.columns))
        tmp = tmp.loc[cyInd, :]

    if cyclustObject == None:
        if (compartment == 'BS' or compartment == 'BS'):  # LIEL
            if (normalized == 'Yes'):
                name2mod = lambda a: '%s%1.0f' % (compartment, ds['npb'].labels[a])
            elif (normalized == 'No'):
                name2mod = lambda a: '%s%1.0f' % (compartment, ds['pb'].labels[a])
            else:
                print('wrong normalized value in plotResultSummary_beta')
        elif compartment == 'NW':
            if (normalized == 'Yes'):
                name2mod = lambda a: '%s%1.0f' % (compartment, ds['nnw'].labels[a])
            elif (normalized == 'No'):
                name2mod = lambda a: '%s%1.0f' % (compartment, ds['nw'].labels[a])
            else:
                print('wrong normalized value in plotResultSummary_beta')
    else:
        name2mod = lambda a: '%s%1.0f' % (compartment, cyclustObject.labels[a])

    tmp.loc[:, 'Module'] = tmp['Analyte'].map(name2mod)
    if ('Coef' in cyResDf.columns):
        cols = ['Outcome', 'Name', 'Module', 'Fold-diff', 'Coef', 'FWER', 'FDR']  # LIEL
    else:
        cols = ['Outcome', 'Name', 'Module', 'Fold-diff', 'OR', 'FWER', 'FDR']

    hDf = pd.concat((tmpMod.loc[modInd, cols], tmp[cols]), axis=0)
    hDf.loc[:, 'isAnalyte'] = (hDf['Module'] != hDf['Name'])
    order = hDf[['Module', 'Name', 'isAnalyte']].drop_duplicates().sort_values(by=['Module', 'isAnalyte', 'Name'])
    fdrH = hDf.pivot(index='Name', columns='Outcome', values='FDR').loc[order.Name, outcomes]
    fdrH = fdrH.fillna(1)
    fwerH = hDf.pivot(index='Name', columns='Outcome', values='FWER').loc[order.Name, outcomes]
    fwerH = fwerH.fillna(1)
    foldH = hDf.pivot(index='Name', columns='Outcome', values='Fold-diff').loc[order.Name, outcomes]

    betaVals = hDf.pivot(index='Name', columns='Outcome', values='Coef').loc[order.Name, outcomes]  # LIEL

    censorInd = fwerH.values > FWERthreshPlot
    """Use fold-change as threshold?"""
    # censorInd = np.abs(np.log(foldH.values)) <= np.log(1.5)

    fwerH.values[censorInd] = 1.
    foldH.values[censorInd] = 1.
    foldH = foldH.fillna(1)
    betaVals.values[censorInd] = 0.

    cmap = palettable.colorbrewer.diverging.PuOr_9_r.mpl_colormap
    vals = betaVals.values
    # pcParams = dict(vmin=-0.7, vmax=0.7, cmap=cmap)
    pcParams = dict(vmin=-0.8, vmax=0.8, cmap=cmap)
    scaleLabel = 'Beta Coefficient'
    # ytl = np.array([-0.7, -0.35,  0, 0.35, 0.7])
    # yt = np.array([-0.7, -0.35,  0, 0.35, 0.7])
    ytl = np.array([-0.8, -0.4, 0, 0.4, 0.8])
    yt = np.array([-0.8, -0.4, 0, 0.4, 0.8])

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
    # if foldChange:
    for cyi, cy in enumerate(betaVals.index):
        for outi, out in enumerate(betaVals.columns):
            if fdrH.loc[cy, out] < 0.0005:
                ann = '***'
            elif fdrH.loc[cy, out] < 0.005:
                ann = '**'
            elif fdrH.loc[cy, out] < 0.05:
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
    if scalebar:
        scaleAxh = figh.add_subplot(plt.GridSpec(1, 1, left=0.1, bottom=0.87, right=0.2, top=0.98)[0, 0])
        cb = figh.colorbar(pcolOut, cax=scaleAxh, ticks=yt)
        cb.set_label(scaleLabel, size=9)
        # cb.set_ticks(yt)
        cb.ax.set_yticklabels(ytl, fontsize=8)


def printTable(resDf1, cols, title='', pdfFile=None, fdrLimit=1, fwerLimit=1, pvalLimit=1, dpi=200, hideConsole=True,
               compartment=None, adjusted=None, **subgroupVars):
    ff = lambda f: '%1.2g' % f

    resDf = resDf1[(resDf1['Compartment'] == compartment) & (resDf1['Normalized'] == adjusted)].copy()
    resDf['FWER'] = sm.stats.multipletests(resDf.pvalue.values, method='holm')[1]
    resDf['FDR'] = sm.stats.multipletests(resDf.pvalue.values, method='fdr_bh')[1]

    ind = (resDf['FDR'] <= fdrLimit) & (resDf['FWER'] <= fwerLimit) & (resDf['pvalue'] <= pvalLimit)

    if pdfFile is None:
        print('\n' + title)
        print('==================================')
        print(resDf[cols].loc[ind].sort_values(by='pvalue').to_string(float_format=ff))
    elif pdfFile[-3:] == 'png':
        if 'Analyte' in resDf.columns.tolist():
            resDf['Analyte'] = resDf['Analyte'].map(greek2latex)
        toPNG(resDf[cols].loc[ind].sort_values(by='pvalue'),
              pdfFile,
              titStr='FLU09: %s' % title,
              float_format='%1.3g',
              dpi=dpi)
    elif pdfFile[-3:] == 'pdf':
        if 'Analyte' in resDf.columns.tolist():
            resDf['Analyte'] = resDf['Analyte'].map(greek2latex)
        toPDF(resDf[cols].loc[ind].sort_values(by='pvalue'),
              pdfFile,
              titStr='FLU09: %s' % title,
              float_format='%1.3g')
    elif pdfFile[-3:] == 'csv':
        if 'Analyte' in resDf.columns.tolist():
            resDf['Analyte'] = resDf['Analyte'].map(greek2latex)

        resDf[cols].loc[ind].sort_values(by='pvalue').to_csv(pdfFile,
                                                             index=False,
                                                             float_format='%1.3g')


def greek2latex(s):
    greek = {chr(0x3b1): '$\\alpha$',
             chr(0x3b2): '$\\beta$',
             chr(0x3b3): '$\\gamma$'}
    for g in list(greek.keys()):
        s = s.replace(g, greek[g])
    return s


'''
plotParams = dict(foldChange=True, qthreshInc=1, qthreshPlot=0.2, sigCol='FDR')

figh2 = plt.figure(62, figsize=(3.6, 9))
plotResultSummary(ds, bvResDf, bvCyDf, compartment='NW', **plotParams)
fname = FIG_PATH + 'outcome/outcome_binvars_normalized.png'
figh2.savefig(fname)
'''

#########################################################################################################

############## Continuous outcomes analysis

conVars = ['Total', 'Systemic', 'Upper RT', 'Lower RT', 'Gastrointestinal', 'log-VL']
standardize = True

conResDf = outcomeAnalysis(ds, outcomeVars=conVars, binaryOutcomes=False, analyzeModules=True,
                           adjustmentVars=[['log-Age']], adjustmentStrs=['AgeAdj'], standardize=standardize)
# conResDf['Age_p'] = conResDf.pvalues.map(lambda d: d.get('log-Age', np.nan))
# conResDf['Age_coef'] = conResDf.params.map(lambda d: d.get('log-Age', np.nan))
# conResDf['FWER'] = sm.stats.multipletests(conResDf.pvalue.values, method='holm')[1]
# conResDf['FDR'] = sm.stats.multipletests(conResDf.pvalue.values, method='fdr_bh')[1]

conCyDf = outcomeAnalysis(ds, outcomeVars=conVars, binaryOutcomes=False, analyzeModules=False,
                          adjustmentVars=[['log-Age']], adjustmentStrs=['AgeAdj'], standardize=standardize)
# conCyDf['Age_p'] = conCyDf.pvalues.map(lambda d: d.get('log-Age', np.nan))
# conCyDf['Age_coef'] = conCyDf.params.map(lambda d: d.get('log-Age', np.nan))
# conCyDf['FWER'] = sm.stats.multipletests(conCyDf.pvalue.values, method='holm')[1]
# conCyDf['FDR'] = sm.stats.multipletests(conCyDf.pvalue.values, method='fdr_bh')[1]

# Beta graphs - adjusted for age (can change to age and viral load - see OneNote)

if standardize:
    figPathOutcomes = 'outcome/outcome-Stand'
else:
    figPathOutcomes = 'outcome/outcome'

plotParams = dict(qthreshInc=1, qthreshPlot=0.2, sigCol='FDR')

figh2 = plt.figure(3581, figsize=(3.6, 9))
plotResultSummary_beta(ds, conResDf, conCyDf, **plotParams, outcomes=conVars)
fname = FIG_PATH + figPathOutcomes + 'FWERfix_conBeta_ageAdj_bs_normalized.png'
figh2.savefig(fname)

figh2 = plt.figure(3581, figsize=(3.6, 9))
plotResultSummary_beta(ds, conResDf, conCyDf, compartment='NW', **plotParams, outcomes=conVars)
fname = FIG_PATH + figPathOutcomes + 'FWERfix_conBeta_ageAdj_nw_normalized.png'
figh2.savefig(fname)

figh2 = plt.figure(3581, figsize=(3.6, 9))
plotResultSummary_beta(ds, conResDf, conCyDf, normalized='No', **plotParams, outcomes=conVars)
fname = FIG_PATH + figPathOutcomes + 'FWERfix_conBeta_ageAdj_bs_raw.png'
figh2.savefig(fname)

figh2 = plt.figure(3581, figsize=(3.6, 9))
plotResultSummary_beta(ds, conResDf, conCyDf, compartment='NW', normalized='No', **plotParams, outcomes=conVars)
fname = FIG_PATH + figPathOutcomes + 'FWERfix_conBeta_ageAdj_nw_raw.png'
figh2.savefig(fname)

# reverse

plotParams = dict(FWERthreshInc=1, FWERthreshPlot=0.2)

figh2 = plt.figure(3581, figsize=(3.6, 9))
plotResultSummary_beta_reverse(ds, conResDf, conCyDf, **plotParams, outcomes=conVars)
fname = FIG_PATH + figPathOutcomes + 'reverse_conBeta_ageAdj_bs_normalized.png'
figh2.savefig(fname)

figh2 = plt.figure(3581, figsize=(3.6, 9))
plotResultSummary_beta_reverse(ds, conResDf, conCyDf, compartment='NW', **plotParams, outcomes=conVars)
fname = FIG_PATH + figPathOutcomes + 'reverse_conBeta_ageAdj_nw_normalized.png'
figh2.savefig(fname)

figh2 = plt.figure(3581, figsize=(3.6, 9))
plotResultSummary_beta_reverse(ds, conResDf, conCyDf, normalized='No', **plotParams, outcomes=conVars)
fname = FIG_PATH + figPathOutcomes + 'reverse_conBeta_ageAdj_bs_raw.png'
figh2.savefig(fname)

figh2 = plt.figure(3581, figsize=(3.6, 9))
plotResultSummary_beta_reverse(ds, conResDf, conCyDf, compartment='NW', normalized='No', **plotParams, outcomes=conVars)
fname = FIG_PATH + figPathOutcomes + 'reverse_conBeta_ageAdj_nw_raw.png'
figh2.savefig(fname)

'''
# Beta graphs - NOT adjusted (can change to age and viral load - see OneNote)

plotParams = dict(qthreshInc=1, qthreshPlot=0.2, sigCol='FDR')

figh2 = plt.figure(3581, figsize=(3.6, 9))
plotResultSummary_beta(ds, conResDf, conCyDf, **plotParams, outcomes=conVars, adjusted=False)
fname = FIG_PATH + figPathOutcomes + '_conBeta_NoAdj_bs_normalized.png'
figh2.savefig(fname)

figh2 = plt.figure(3581, figsize=(3.6, 9))
plotResultSummary_beta(ds, conResDf, conCyDf, compartment='NW', **plotParams, outcomes=conVars, adjusted=False)
fname = FIG_PATH + figPathOutcomes + '_conBeta_NoAdj_nw_normalized.png'
figh2.savefig(fname)

figh2 = plt.figure(3581, figsize=(3.6, 9))
plotResultSummary_beta(ds, conResDf, conCyDf, normalized='No', **plotParams, outcomes=conVars, adjusted=False)
fname = FIG_PATH + figPathOutcomes + '_conBeta_NoAdj_bs_raw.png'
figh2.savefig(fname)

figh2 = plt.figure(3581, figsize=(3.6, 9))
plotResultSummary_beta(ds, conResDf, conCyDf, compartment='NW', normalized='No', **plotParams, outcomes=conVars, adjusted=False)
fname = FIG_PATH + figPathOutcomes + '_conBeta_NoAdj_nw_raw.png'
figh2.savefig(fname)
'''

modCols = ['Outcome', 'Module', 'Coef', 'pvalue', 'FWER', 'FDR']
dpi = 400
fdrLimitV = 1
fwerLimitV = 1
pvalLimitV = 0.05
printTable(conResDf, modCols, 'Serum (Adjusted)',
           fdrLimit=fdrLimitV, fwerLimit=fwerLimitV, pvalLimit=pvalLimitV,
           compartment='BS', adjusted='Yes',
           pdfFile=GIT_PATH + 'cyclustMS/FLU09/tables/outcome/tables_conBeta_ageAdj_bs_adj.pdf', dpi=dpi)

printTable(conResDf, modCols, 'Serum (Absolute)',
           fdrLimit=fdrLimitV, fwerLimit=fwerLimitV, pvalLimit=pvalLimitV,
           compartment='BS', adjusted='No',
           pdfFile=GIT_PATH + 'cyclustMS/FLU09/tables/outcome/tables_conBeta_ageAdj_bs_raw.pdf', dpi=dpi)

printTable(conResDf, modCols, 'Nasal Wash (Adjusted)',
           fdrLimit=fdrLimitV, fwerLimit=fwerLimitV, pvalLimit=pvalLimitV,
           compartment='NW', adjusted='Yes',
           pdfFile=GIT_PATH + 'cyclustMS/FLU09/tables/outcome/tables_conBeta_ageAdj_nw_adj.pdf', dpi=dpi)

printTable(conResDf, modCols, 'Nasal Wash (Absolute)',
           fdrLimit=fdrLimitV, fwerLimit=fwerLimitV, pvalLimit=pvalLimitV,
           compartment='NW', adjusted='No',
           pdfFile=GIT_PATH + 'cyclustMS/FLU09/tables/outcome/tables_conBeta_ageAdj_nw_raw.pdf', dpi=dpi)

# CY
modCols = ['Outcome', 'Analyte', 'Coef', 'pvalue', 'FWER', 'FDR']

printTable(conCyDf, modCols, 'Serum (Adjusted)',
           fdrLimit=fdrLimitV, fwerLimit=fwerLimitV, pvalLimit=pvalLimitV,
           compartment='BS', adjusted='Yes',
           pdfFile=GIT_PATH + 'cyclustMS/FLU09/tables/outcome/tablesCy_conBeta_ageAdj_bs_adj.pdf', dpi=dpi)

printTable(conCyDf, modCols, 'Serum (Absolute)',
           fdrLimit=fdrLimitV, fwerLimit=fwerLimitV, pvalLimit=pvalLimitV,
           compartment='BS', adjusted='No',
           pdfFile=GIT_PATH + 'cyclustMS/FLU09/tables/outcome/tablesCy_conBeta_ageAdj_bs_raw.pdf', dpi=dpi)

printTable(conCyDf, modCols, 'Nasal Wash (Adjusted)',
           fdrLimit=fdrLimitV, fwerLimit=fwerLimitV, pvalLimit=pvalLimitV,
           compartment='NW', adjusted='Yes',
           pdfFile=GIT_PATH + 'cyclustMS/FLU09/tables/outcome/tablesCy_conBeta_ageAdj_nw_adj.pdf', dpi=dpi)

printTable(conCyDf, modCols, 'Nasal Wash (Absolute)',
           fdrLimit=fdrLimitV, fwerLimit=fwerLimitV, pvalLimit=pvalLimitV,
           compartment='NW', adjusted='No',
           pdfFile=GIT_PATH + 'cyclustMS/FLU09/tables/outcome/tablesCy_conBeta_ageAdj_nw_raw.pdf', dpi=dpi)

#################### continuous outcomes - CORE

chosenLabels_NormPB = {'sCD40-L': 1, 'EGF': 1, 'GRO': 1, 'MDC': 1,
                       'IL2': 2, 'IL12-P40': 2, 'IL15': 2,
                       'IL4': 3, 'IL13': 3, 'IL1β': 3,
                       'MIP1β': 4, 'TNFα': 4,
                       'IP10': 5, 'MCP1': 5, 'MIP1α': 5, 'IL8': 5,
                       'GCSF': 6, 'IL6': 6}

chosenLabels_RawPB = {'sCD40-L': 1, 'GRO': 1, 'MDC': 1,
                      'IL2': 2, 'IL12-P40': 2, 'IL15': 2,
                      'IL4': 3, 'IL13': 3, 'IL1β': 3, 'IL3': 3,
                      'MIP1β': 4, 'TNFα': 4,
                      'IP10': 5, 'MCP1': 5,
                      'MIP1α': 6, 'IL8': 6, 'GCSF': 6, 'IL6': 6,
                      'IL7': 7, 'IL9': 7}


def chosenCysLabels(labelsDict):
    chosenCys_ = list(labelsDict.keys())
    chosenLabels_ = pd.Series(labelsDict)
    return ([chosenCys_, chosenLabels_])


chosenCys_NormPB, chosenLabels_NormPB = chosenCysLabels(chosenLabels_NormPB)
chosenCys_RawPB, chosenLabels_RawPB = chosenCysLabels(chosenLabels_RawPB)

dsCore = {}
dsCore['npb_c'] = cy.cyclusterClass('FLU09', 'Core', True, pbEarly[chosenCys_NormPB])
dsCore['pb_c'] = cy.cyclusterClass('FLU09', 'Core', False, pbEarly[chosenCys_RawPB])

dsCore['npb_c'].clusterCytokines(labelMap=chosenLabels_NormPB)
dsCore['pb_c'].clusterCytokines(labelMap=chosenLabels_RawPB)

conResDf_c = outcomeAnalysis(dsCore, outcomeVars=conVars, binaryOutcomes=False, dsKeys=['npb_c', 'pb_c'],
                             analyzeModules=True, adjustmentVars=[['log-Age']], adjustmentStrs=['AgeAdj'],
                             standardize=standardize)
# conResDf_c['Age_p'] = conResDf_c.pvalues.map(lambda d: d.get('log-Age', np.nan))
# conResDf_c['Age_coef'] = conResDf_c.params.map(lambda d: d.get('log-Age', np.nan))
# conResDf_c['FWER'] = sm.stats.multipletests(conResDf_c.pvalue.values, method='holm')[1]
# conResDf_c['FDR'] = sm.stats.multipletests(conResDf_c.pvalue.values, method='fdr_bh')[1]

# Beta graphs - adjusted for age (can change to age and viral load - see OneNote)

if standardize:
    figPathOutcomes = 'outcome/outcome-Stand'
else:
    figPathOutcomes = 'outcome/outcome'

plotParams = dict(qthreshInc=1, qthreshPlot=0.2, sigCol='FDR')

figh2 = plt.figure(3581, figsize=(3.6, 9))
plotResultSummary_beta(dsCore, conResDf_c, conCyDf, compartment='Core', cyclustObject=dsCore['npb_c'], **plotParams,
                       outcomes=conVars)
fname = FIG_PATH + figPathOutcomes + 'FWERfix_CORE_conBeta_ageAdj_bs_normalized.png'
figh2.savefig(fname)

figh2 = plt.figure(3581, figsize=(3.6, 9))
plotResultSummary_beta(dsCore, conResDf_c, conCyDf, compartment='Core', cyclustObject=dsCore['pb_c'], normalized='No',
                       **plotParams, outcomes=conVars)
fname = FIG_PATH + figPathOutcomes + 'FWERfix_CORE_conBeta_ageAdj_bs_raw.png'
figh2.savefig(fname)

plotParams = dict(qthreshInc=1, qthreshPlot=0.05, sigCol='FDR')

figh2 = plt.figure(3581, figsize=(3.6, 9))
plotResultSummary_beta(dsCore, conResDf_c, conCyDf, compartment='Core', cyclustObject=dsCore['npb_c'], **plotParams,
                       outcomes=conVars)
fname = FIG_PATH + figPathOutcomes + 'FDR05_FWERfix_CORE_conBeta_ageAdj_bs_normalized.png'
figh2.savefig(fname)

figh2 = plt.figure(3581, figsize=(3.6, 9))
plotResultSummary_beta(dsCore, conResDf_c, conCyDf, compartment='Core', cyclustObject=dsCore['pb_c'], normalized='No',
                       **plotParams, outcomes=conVars)
fname = FIG_PATH + figPathOutcomes + 'FDR05_FWERfix_CORE_conBeta_ageAdj_bs_raw.png'
figh2.savefig(fname)

modCols = ['Outcome', 'Module', 'Coef', 'pvalue', 'FWER', 'FDR']
dpi = 400
fdrLimitV = 1
fwerLimitV = 1
pvalLimitV = 0.05
printTable(conResDf_c, modCols, 'Serum (Adjusted)',
           fdrLimit=fdrLimitV, fwerLimit=fwerLimitV, pvalLimit=pvalLimitV,
           compartment='Core', adjusted='Yes',
           pdfFile=GIT_PATH + 'cyclustMS/FLU09/tables/outcome/tables_CORE_conBeta_ageAdj_bs_adj.pdf', dpi=dpi)

printTable(conResDf_c, modCols, 'Serum (Absolute)',
           fdrLimit=fdrLimitV, fwerLimit=fwerLimitV, pvalLimit=pvalLimitV,
           compartment='Core', adjusted='No',
           pdfFile=GIT_PATH + 'cyclustMS/FLU09/tables/outcome/tables_CORE_conBeta_ageAdj_bs_raw.pdf', dpi=dpi)

############## binary outcomes analysis
binVars = ['Hospitalization', 'Any LRT', 'Emergency Room', 'Missed Work/School', 'Severe Illness']
standardize = True

bvResDf = outcomeAnalysis(ds, outcomeVars=binVars, binaryOutcomes=True, analyzeModules=True,
                          adjustmentVars=[['log-Age']], adjustmentStrs=['AgeAdj'], standardize=standardize)
# bvResDf['Age_p'] = bvResDf.pvalues.map(lambda d: d.get('log-Age', np.nan))
# bvResDf['Age_coef'] = bvResDf.params.map(lambda d: np.exp(d.get('log-Age', np.nan)))
# bvResDf['VL_p'] = bvResDf.pvalues.map(lambda d: d.get('log-VL', np.nan))
# bvResDf['VL_coef'] = bvResDf.params.map(lambda d: np.exp(d.get('log-VL', np.nan)))
# bvResDf['FWER'] = sm.stats.multipletests(bvResDf.pvalue.values, method='holm')[1]
# bvResDf['FDR'] = sm.stats.multipletests(bvResDf.pvalue.values, method='fdr_bh')[1]

bvCyDf = outcomeAnalysis(ds, outcomeVars=binVars, binaryOutcomes=True, analyzeModules=False,
                         adjustmentVars=[['log-Age']], adjustmentStrs=['AgeAdj'], standardize=standardize)
# bvCyDf['Age_p'] = bvCyDf.pvalues.map(lambda d: d.get('log-Age', np.nan))
# bvCyDf['Age_coef'] = bvCyDf.params.map(lambda d: np.exp(d.get('log-Age', np.nan)))
# bvCyDf['VL_p'] = bvCyDf.pvalues.map(lambda d: d.get('log-VL', np.nan))
# bvCyDf['VL_coef'] = bvCyDf.params.map(lambda d: np.exp(d.get('log-VL', np.nan)))
# bvCyDf['FWER'] = sm.stats.multipletests(bvCyDf.pvalue.values, method='holm')[1]
# bvCyDf['FDR'] = sm.stats.multipletests(bvCyDf.pvalue.values, method='fdr_bh')[1]

'''
# age adj
plotParams = dict(foldChange=True, qthreshInc=1, qthreshPlot=0.2, sigCol='FDR')

if standardize:
    figPathOutcomes = 'outcome/outcome-Stand'
else:
    figPathOutcomes = 'outcome/outcome'

figh2 = plt.figure(3581, figsize=(3.6, 9))
plotResultSummary(ds, bvResDf, bvCyDf, **plotParams, outcomes=binVars)
fname = FIG_PATH + figPathOutcomes + '_binVars_ageAdj_bs_normalized.png'
figh2.savefig(fname)

figh2 = plt.figure(3581, figsize=(3.6, 9))
plotResultSummary(ds, bvResDf, bvCyDf, compartment='NW', **plotParams, outcomes=binVars)
fname = FIG_PATH + figPathOutcomes + '_binVars_ageAdj_nw_normalized.png'
figh2.savefig(fname)

figh2 = plt.figure(3581, figsize=(3.6, 9))
plotResultSummary(ds, bvResDf, bvCyDf, normalized='No', **plotParams, outcomes=binVars)
fname = FIG_PATH + figPathOutcomes + '_binVars_ageAdj_bs_raw.png'
figh2.savefig(fname)

figh2 = plt.figure(3581, figsize=(3.6, 9))
plotResultSummary(ds, bvResDf, bvCyDf, compartment='NW', normalized='No', **plotParams, outcomes=binVars)
fname = FIG_PATH + figPathOutcomes + '_binVars_ageAdj_nw_raw.png'
figh2.savefig(fname)

'''

# Odds ratio

plotParams = dict(foldChange=True, qthreshInc=1, qthreshPlot=0.2, sigCol='FDR', associatMeasure='OR')

if standardize:
    figPathOutcomes = 'outcome/outcome-Stand'
else:
    figPathOutcomes = 'outcome/outcome'

figh2 = plt.figure(3581, figsize=(3.6, 9))
plotResultSummary(ds, bvResDf, bvCyDf, **plotParams, outcomes=binVars)
fname = FIG_PATH + figPathOutcomes + '_binVarsOR_ageAdj_bs_normalized.png'
figh2.savefig(fname)

figh2 = plt.figure(3581, figsize=(3.6, 9))
plotResultSummary(ds, bvResDf, bvCyDf, compartment='NW', **plotParams, outcomes=binVars)
fname = FIG_PATH + figPathOutcomes + '_binVarsOR_ageAdj_nw_normalized.png'
figh2.savefig(fname)

figh2 = plt.figure(3581, figsize=(3.6, 9))
plotResultSummary(ds, bvResDf, bvCyDf, normalized='No', **plotParams, outcomes=binVars)
fname = FIG_PATH + figPathOutcomes + '_binVarsOR_ageAdj_bs_raw.png'
figh2.savefig(fname)

figh2 = plt.figure(3581, figsize=(3.6, 9))
plotResultSummary(ds, bvResDf, bvCyDf, compartment='NW', normalized='No', **plotParams, outcomes=binVars)
fname = FIG_PATH + figPathOutcomes + '_binVarsOR_ageAdj_nw_raw.png'
figh2.savefig(fname)

#################### binvars CORE

bvResDf_c = outcomeAnalysis(dsCore, outcomeVars=binVars, binaryOutcomes=True, dsKeys=['npb_c', 'pb_c'],
                            analyzeModules=True, adjustmentVars=[['log-Age']], adjustmentStrs=['AgeAdj'],
                            standardize=standardize)
# bvResDf_c['Age_p'] = bvResDf_c.pvalues.map(lambda d: d.get('log-Age', np.nan))
# bvResDf_c['Age_coef'] = bvResDf_c.params.map(lambda d: d.get('log-Age', np.nan))
# bvResDf_c['FWER'] = sm.stats.multipletests(bvResDf_c.pvalue.values, method='holm')[1]
# bvResDf_c['FDR'] = sm.stats.multipletests(bvResDf_c.pvalue.values, method='fdr_bh')[1]

# Beta graphs - adjusted for age (can change to age and viral load - see OneNote)

if standardize:
    figPathOutcomes = 'outcome/outcome-Stand'
else:
    figPathOutcomes = 'outcome/outcome'

plotParams = dict(foldChange=True, qthreshInc=1, qthreshPlot=0.2, sigCol='FDR', associatMeasure='OR')

figh2 = plt.figure(3581, figsize=(3.6, 9))
plotResultSummary(dsCore, bvResDf_c, bvCyDf, cyclustObject=dsCore['npb_c'], compartment='Core', **plotParams,
                  outcomes=binVars)
fname = FIG_PATH + figPathOutcomes + 'CORE_binVarsOR_ageAdj_bs_normalized.png'
figh2.savefig(fname)

figh2 = plt.figure(3581, figsize=(3.6, 9))
plotResultSummary(dsCore, bvResDf_c, bvCyDf, cyclustObject=dsCore['pb_c'], normalized='No', compartment='Core',
                  **plotParams, outcomes=binVars)
fname = FIG_PATH + figPathOutcomes + 'CORE_binVarsOR_ageAdj_bs_raw.png'
figh2.savefig(fname)

####################################### Core correlations

for s in dsCore.keys():
    plt.figure(50, figsize=(15, 9))
    for lab in list(cy.labels2modules(dsCore[s].labels, dsCore[s].dropped).keys()):
        cyplot.plotModuleCorr(dsCore[s].cyDf, dsCore[s].labels, lab, dropped=dsCore[s].dropped, sampleStr='Core')
        plt.figure(50).savefig(FIG_PATH + 'cores/%s_core_corr_%s.png' % (dsCore[s].name, lab))

    """Plot inter-module correlation"""
    plt.figure(51, figsize=(15, 9))
    cyplot.plotInterModuleCorr(dsCore[s].withMean, dsCore[s].labels, dropped=dsCore[s].dropped,
                               compCommVar=dsCore[s].meanS.name, sampleStr='Core')
    plt.figure(51).savefig(FIG_PATH + 'cores/%s_inter-core_correlat.png' % dsCore[s].name)


def getCorrPvalTable(data, method='pearson'):
    table = pd.DataFrame(columns=['Correlation', 'Pvalue', 'Pvalue*'])

    for var1 in data.columns:
        for var2 in data.columns:
            if (var1 != var2) & ~((str(var2) + '-' + str(var1) in table.index)):
                if (method == 'spearman'):
                    corrtest = getSpearmanForDFColumns(data[var1], data[var2])
                else:
                    corrtest = getPearsonForDFColumns(data[var1], data[var2])

                if corrtest[1] < 0.0005:
                    ann = '***'
                elif corrtest[1] < 0.005:
                    ann = '**'
                elif corrtest[1] < 0.05:
                    ann = '*'
                else:
                    ann = ' '
                indName = str(var1) + '-' + str(var2)
                table = table.append(pd.Series([corrtest[0], corrtest[1], ann], index=table.columns, name=indName))
    return table


def getPearsonForDFColumns(col1, col2):
    tmpDFa = pd.DataFrame(col1)
    tmpDFa.columns = ['col1']

    tmpDFb = pd.DataFrame(col2)
    tmpDFb.columns = ['col2']

    tmpDF1 = tmpDFa.join(tmpDFb).dropna()
    return (scipy.stats.stats.pearsonr(tmpDF1.loc[:, 'col1'], tmpDF1.loc[:, 'col2']))


corrDataAdj = getCorrPvalTable(dsCore['npb_c'].modDf, method='pearson')
corrDataAbs = getCorrPvalTable(dsCore['pb_c'].modDf, method='pearson')

writeDF2Excel(
    'C:/Users/liel-/Dropbox/PhD/Projects/Cytokine Tomer-Andrew/23-08 Final analysis/core correl final/FLU09_adj.xlsx',
    corrDataAdj)
writeDF2Excel(
    'C:/Users/liel-/Dropbox/PhD/Projects/Cytokine Tomer-Andrew/23-08 Final analysis/core correl final/FLU09_abs.xlsx',
    corrDataAbs)

writeDf2Dill(
    'C:/Users/liel-/Dropbox/PhD/Projects/Cytokine Tomer-Andrew/23-08 Final analysis/All DFs together/FLU09_adj.dill',
    dsCore['npb_c'].modDf)

'''

"""Make tables of the modules for presentation."""
for k in list(ds.keys()):
    tmpMod = ds[k].modS.copy()
    mx = np.max([len(m) for m in list(tmpMod.values())])
    for j in list(tmpMod.keys()):
        if len(tmpMod[j]) < mx:
            tmpMod[j] += ['']*(mx - len(tmpMod[j]))
    tmpDf = pd.DataFrame(tmpMod)
    tmpDf = tmpDf.rename_axis(lambda c: '%s%d' % (ds[k].sampleStr, c), axis=1)
    tmpDf = tmpDf[sorted(tmpDf.columns)]
    if ds[k].normed:
        titStr = 'Normalized ' + ds[k].sampleStr + ' Modules'
    else:
        titStr = 'Raw ' + ds[k].sampleStr + ' Modules'
    print() 
    toPNG(tmpDf, GIT_PATH + 'cyclustMS/FLU09/tables/%smodules.png' % ds[k].name, titStr=titStr, float_format='%1.3g')


for sampleStr in ['NW', 'BS']:
    printInd = (bvResDf.Normalized=='Yes') & (bvResDf.Compartment == sampleStr) & (bvResDf.FDR < 0.2)
    printCols = ['Outcome', 'Module', 'OR', 'LL', 'UL', 'Fold-diff', 'pvalue', 'FWER', 'FDR', 'Age_coef', 'VL_coef']
    pdf = bvResDf[printCols].loc[printInd].sort_values(by='pvalue')
    toPDF(pdf, GIT_PATH + 'cyclustMS/FLU09/tables/%s_mod_bv.pdf' % sampleStr, titStr='FLU09: %s Modules and binary outcomes' % sampleStr, float_format='%1.3g')
    #toPNG(pdf, GIT_PATH + 'cyclustMS/FLU09/tables/%s_mod_bv.png' % sampleStr, titStr='FLU09: %s Modules and binary outcomes' % sampleStr, float_format='%1.3g')
    """
    printInd = (~conResDf.Age_p.isnull()) & (conResDf.Normalized=='Yes') & (conResDf.Compartment == sampleStr)
    printCols = ['Outcome','Module','Coef','LL','UL','Fold-diff','pvalue','FWER','FDR','Age_coef','VL_coef']
    pdf = conResDf[printCols].loc[printInd].sort_values(by='pvalue')
    toPDF(pdf, GIT_PATH + 'cyclustMS/FLU09/tables/%s_mod_con.pdf' % sampleStr, titStr='FLU09: %s Modules and continuous outcomes' % sampleStr, float_format='%1.3g')
    """

for sampleStr in ['NW', 'BS']:
    printInd = (bvCyDf.Normalized=='Yes') & (bvCyDf.Compartment == sampleStr) & (bvResDf.FDR < 0.2)
    printCols = ['Outcome', 'Analyte', 'OR', 'LL', 'UL', 'Fold-diff', 'pvalue', 'FWER', 'FDR', 'Age_coef', 'VL_coef']
    pdf = bvCyDf[printCols].loc[printInd].sort_values(by='pvalue')
    toPDF(pdf, GIT_PATH + 'cyclustMS/FLU09/tables/%s_cy_bv.pdf' % sampleStr, titStr='FLU09: %s Cytokines and binary outcomes' % sampleStr, float_format='%1.3g')
    #toPNG(pdf, GIT_PATH + 'cyclustMS/FLU09/tables/%s_cy_bv.png' % sampleStr, titStr='FLU09: %s Cytokines and binary outcomes' % sampleStr, float_format='%1.3g')

    """
    printInd = (~conCyDf.Age_p.isnull()) & (conCyDf.Normalized=='Yes') & (conCyDf.Compartment == sampleStr)
    printCols = ['Outcome','Analyte','Coef','LL','UL','Fold-diff','pvalue','FWER','FDR','Age_coef','VL_coef']
    pdf = conCyDf[printCols].loc[printInd].sort_values(by='pvalue')
    toPDF(pdf, GIT_PATH + 'cyclustMS/FLU09/tables/%s_cy_con.pdf' % sampleStr, titStr='FLU09: %s Cytokines and continuous outcomes' % sampleStr, float_format='%1.3g')
    """

plt.figure(505, figsize=(12, 10))
for adj in ['AgeVLAdj', 'NoAdj']:
    cyOutcomeScatter(bvCyDf, outcomeVars=['Hospitalization'], adjustVar=adj, normalized=True)
    plt.figure(505).savefig(FIG_PATH + 'comp/Hospitalization_normalized.png')
    cyOutcomeScatter(bvCyDf, outcomeVars=['Any LRT'], adjustVar=adj, normalized=True)
    plt.figure(505).savefig(FIG_PATH + 'comp/AnyLRT_normalized.png')

    #cyOutcomeScatter(conCyDf, outcomeVars=['Total'], adjustVar=adj, normalized=True)
    #plt.figure(505).savefig(FIG_PATH + 'comp/Total_normalized.png')

    #cyOutcomeScatter(conCyDf, outcomeVars=['Upper RT'], adjustVar=adj, normalized=True)
    #plt.figure(505).savefig(FIG_PATH + 'comp/Upper_normalized.png')

    #cyOutcomeScatter(conCyDf, outcomeVars=['Lower RT'], adjustVar=adj, normalized=True)
    #plt.figure(505).savefig(FIG_PATH + 'comp/Lower_normalized.png')



"""Boxplots of cytokines/modules by outcome"""
plt.figure(400)
for s in list(ds.keys()):
    for sv in ds[s].modDf.columns:
        tmpDf = addOutcomeVars(ds[s].modDf)
        singleOutcomeBoxplot(tmpDf, sv, 'Severe Illness')
        plt.figure(400).savefig(FIG_PATH + 'outcome/%sSevere_illness_%s.png' % (ds[s].name, sv))

plt.figure(400)
for s in list(ds.keys()):
    for sv in ['MCP3', 'IL6', 'IL8', 'EGF', 'IL4', 'IL5', 'GCSF', 'VEGF', 'IL9', 'Eotaxin']:
        tmpDf = addOutcomeVars(ds[s].cyDf)
        singleOutcomeBoxplot(tmpDf, sv, 'Severe Illness')
        plt.figure(400).savefig(FIG_PATH + 'outcome/%sSevere_illness_%s.png' % (ds[s].name, sv))








cyPaper = ['IFN-alpha2', 'IL1-beta', 'IP10', 'MCP3', 'IL8', 'IL10', 'IFN-gamma', 'IL6', 'VEGF', 'GCSF']
lielCyDf = conCyDf.loc[conCyDf['Analyte'].isin(cyPaper)]
lielCyDf_pb_normed = lielCyDf.loc[(lielCyDf['Compartment'] == 'BS') & (lielCyDf['Normalized'] == 'Yes')]
lielCyDf_pb_notNormed = lielCyDf.loc[(lielCyDf['Compartment'] == 'BS') & (lielCyDf['Normalized'] == 'No')]
lielCyDf_nw_normed = lielCyDf.loc[(lielCyDf['Compartment'] == 'NW') & (lielCyDf['Normalized'] == 'Yes')]
lielCyDf_nw_notNormed = lielCyDf.loc[(lielCyDf['Compartment'] == 'NW') & (lielCyDf['Normalized'] == 'No')]


lielCyDf_pb_normed2 = conCyDf.loc[(conCyDf['Compartment'] == 'BS') & (conCyDf['Normalized'] == 'Yes') & (conCyDf['Model'] == 'AgeVLAdj')]
lielCyDf_pb_notNormed2 = conCyDf.loc[(conCyDf['Compartment'] == 'BS') & (conCyDf['Normalized'] == 'No') & (conCyDf['Model'] == 'AgeVLAdj')]
lielCyDf_nw_normed2 = conCyDf.loc[(conCyDf['Compartment'] == 'NW') & (conCyDf['Normalized'] == 'Yes') & (conCyDf['Model'] == 'AgeVLAdj')]
lielCyDf_nw_notNormed2 = conCyDf.loc[(conCyDf['Compartment'] == 'NW') & (conCyDf['Normalized'] == 'No') & (conCyDf['Model'] == 'AgeVLAdj')]








def outcomesPairPlot_Age(df, outcomes, vars, line=False):
    tmp = addOutcomeVars(df)
    tmp = tmp.loc[:, (outcomes + vars + ['Age'])].dropna()
    bin = [0, 15, 30, 50, 80]
    tmp['Age_binned'] = pd.cut(tmp['Age'], bin)
    if line:
        sns.pairplot(tmp, size=3, diag_kind="kde", hue='Age_binned', x_vars=outcomes, y_vars=vars, kind="reg"), plt.show()
    else:
        sns.pairplot(tmp, size=3, diag_kind="kde", hue='Age_binned', x_vars=outcomes, y_vars=vars), plt.show()

def outcomesPairPlot(df, outcomes, vars):
    tmp = addOutcomeVars(df)
    tmp = tmp.loc[:, (outcomes + vars + ['Age'])]
    bin = [0, 15, 30, 50, 80]
    tmp['Age_binned'] = pd.cut(tmp['Age'], bin)
    sns.pairplot(tmp, size=3, diag_kind="kde", kind="reg", x_vars=outcomes, y_vars=vars), plt.show()

outcomesPairPlot(ds['nnw'].modDf, ['Total', 'Systemic', 'Gastrointestinal', 'log-VL'], ['NW1', 'NW2','NW3','NW4','NW5','NW6'])

outcomesPairPlot(ds['nnw'].cyDf, ['Total', 'Systemic', 'Gastrointestinal', 'log-VL'], ['FLT3L', 'GM-CSF', 'IL12-P70', 'IL5'])

outcomesPairPlot_Age(ds['nnw'].cyDf, ['Total', 'Systemic'], ['FLT3L', 'GM-CSF', 'IL12-P70', 'IL2', 'IL5', 'IL7', 'TGF-alpha', 'TNF-beta'], line=False)

outcomesPairPlot(ds['nnw'].cyDf, ['Total', 'Systemic'], ['FLT3L', 'GM-CSF', 'IL12-P70', 'IL2', 'IL5', 'IL7', 'TGF-alpha', 'TNF-beta'])
'''