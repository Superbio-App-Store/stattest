import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt


def run_normal_tests(group1, group2, s1, s2, alternative = 'two-sided', output = "/output/"):
    
    metrics_out1 = []
    index_out1 = ['Shapiro','Skew']
    shapiro = stats.shapiro(group1)
    metrics_out1.append((shapiro.statistic,shapiro.pvalue))
    skew = stats.skewtest(group1)
    metrics_out1.append((skew.statistic,skew.pvalue))
    if len(group1) >= 20:
        kurtosis = stats.kurtosistest(group1)
        metrics_out1.append((kurtosis.statistic,kurtosis.pvalue))
        norm = stats.normaltest(group1)
        metrics_out1.append((norm.statistic,norm.pvalue))
        index_out1 = index_out1 + ['Kurtosis','Normal']
    if len(group1) >= 2000:
        jb = stats.jarque_bera(group1)
        metrics_out1.append((jb.statistic,jb.pvalue))
        index_out1.append('Jarque-Bera')
    norm_metrics1 = pd.DataFrame(metrics_out1, index = index_out1)
    
    if s2 != None:
        metrics_out2 = []
        index_out2 = ['Shapiro','Skew']
        shapiro = stats.shapiro(group2)
        metrics_out2.append((shapiro.statistic,shapiro.pvalue))
        skew = stats.skewtest(group2)
        metrics_out2.append((skew.statistic,skew.pvalue))
        if len(group2) >= 20:
            kurtosis = stats.kurtosistest(group2)
            metrics_out2.append((kurtosis.statistic,kurtosis.pvalue))
            norm = stats.normaltest(group2)
            metrics_out2.append((norm.statistic,norm.pvalue))
            index_out2 = index_out2 + ['Kurtosis','Normal']
        if len(group2) >= 2000:
            jb = stats.jarque_bera(group2)
            metrics_out2.append((jb.statistic,jb.pvalue))
            index_out2.append('Jarque-Bera')
        norm_metrics2 = pd.DataFrame(metrics_out2, index = index_out2)
        
        #concatenate the two sets of results
        norm_concat = pd.concat([norm_metrics1, norm_metrics2], axis=1)
        norm_concat.columns = pd.MultiIndex.from_tuples(
        [("Group1", "statistic"), ("Group1", "pvalue"),
         ("Group2", "statistic"), ("Group2", "pvalue")],
        names=["Group", "Metric"]
        )
        
        norm_concat.to_csv(output + 'Normal_Tests.csv')
        
    else:
        norm_metrics1.to_csv(output + 'Normal_Tests.csv')
    
    norm_table_out = [{'file': output + 'Normal_Tests.csv',
                       'title': 'Normal Tests'}]
    return norm_table_out
    
    
    #THIS NEEDS S2
def run_nonparametric_tests(group1, group2, s1, s2, alternative = 'two-sided', output = "/output/"):
    
    metrics_out = []
    index_out = ['Mann-Whitney','Wilcoxon Rank-Sum',
                 'Cramer-Von Mises','Epps-Singleton','Kolmogorov-Smirnov']
    mw = stats.mannwhitneyu(group1, group2, alternative = alternative)
    metrics_out.append((mw.statistic,mw.pvalue))
    rs = stats.ranksums(group1, group2, alternative = alternative)
    metrics_out.append((rs.statistic,rs.pvalue))
    cvm_metrics = stats.cramervonmises_2samp(group1, group2)
    metrics_out.append((cvm_metrics.statistic,cvm_metrics.pvalue))
    es = stats.epps_singleton_2samp(group1, group2)
    metrics_out.append((es.statistic,es.pvalue))
    ks_metrics = stats.ks_2samp(group1, group2, alternative = alternative)
    metrics_out.append((ks_metrics[0],ks_metrics[1]))
    index_out = index_out + ['Mood','Ansari']

    #to test scale parameter of distribution
    mood = stats.mood(group1, group2, alternative = alternative)
    metrics_out.append((mood.statistic,mood.pvalue))
    ansari = stats.ansari(group1, group2, alternative = alternative)
    metrics_out.append((ansari.statistic,ansari.pvalue))
    metrics_df = pd.DataFrame(metrics_out, index = index_out)
    metrics_df.to_csv(output + 'Non_Parametric_Tests.csv')
    
    npara_table_out = [{'file': output + 'Non_Parametric_Tests.csv',
                       'title': 'Non-Parametric Tests'}]
    return npara_table_out

    
    #THIS NEEDS S2 (but see 1 sample t-test and see 3+ sample anova)
def run_mean_tests(group1, group2, s1, s2, alternative = 'two-sided', output = "/output/"):
    
    metrics_out = []
    index_out = ['T-Test','Wilcoxon','BWS Test']
    metrics_out.append(stats.ttest_ind(group1, group2, alternative = alternative))
    metrics_out.append(stats.wilcoxon(group1, group2, alternative = alternative))
    bws_metrics = stats.bws_test(group1, group2, alternative = alternative)
    metrics_out.append((bws_metrics.statistic,bws_metrics.pvalue))
    #to test equal ratio of outliers
    if len(group2) >= 30:
        if len(group2) >= 100:
            dist = 'normal'
        else:
            dist = 't'
        index_out.append('Brunner-Munzel')
        bm = stats.brunnermunzel(group1, group2, alternative = alternative, distribution = dist)
        metrics_out.append((bm.statistic,bm.pvalue))

    metrics_df = pd.DataFrame(metrics_out, index = index_out)
    metrics_df.to_csv(output + 'Mean_Tests.csv')
    
    mean_table_out = [{'file': output + 'Mean_Tests.csv',
                       'title': 'Mean Tests'}]
    return mean_table_out

    
def run_association_tests(group1, group2, s1, s2, alternative = 'two-sided', distribution = 'non-parametric', output = "/output/"):
    
    metrics_out = []
    
    if distribution == 'normal':
        index_out = ['Pearson R','Linear Regression']
        metrics_out.append(stats.pearsonr(group1, group2, alternative = alternative))
        lr_metrics = stats.linregress(group1, group2, alternative = alternative)
        metrics_out.append((lr_metrics[2], lr_metrics[3]))
    
    elif distribution == 'non-parametric':
        index_out = ['Spearman R'] #,'Siegel Slopes','Thiel Slopes']
        metrics_out.append(stats.spearmanr(group1, group2, alternative = alternative))
        #metrics_out.append(stats.siegelslopes(group1, group2, alternative = alternative))   #like linear regression, but ignores outliers
        #metrics_out.append(stats.thielslopes(group1, group2, alternative = alternative))   #fits pairwise slopes
    
    elif distribution == 'ordinal': #not used in version 1
        index_out = ['Kendall Tau','Somers D']
        metrics_out.append(stats.kendalltau(group1, group2, alternative = alternative))
        metrics_out.append(stats.somersd(group1, group2, alternative = alternative))

    metrics_df = pd.DataFrame(metrics_out, index = index_out)
    metrics_df.to_csv(output + 'Association_Tests.csv')
    
    assoc_table_out = [{'file': output + 'Association_Tests.csv',
                       'title': 'Association Tests'}]
    return assoc_table_out