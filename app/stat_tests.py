import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt


def run_normal_tests(group1, group2, s1, s2, alternative = 'two-sided', output = "/output/"):
    
    metrics_out1 = []
    index_out1 = ['Shapiro','Skew']
    metrics_out1.append(stats.shapiro(group1))
    metrics_out1.append(stats.skewtest(group1))
    if len(group1) >= 20:
        metrics_out1.append(stats.kurtosistest(group1))
        metrics_out1.append(stats.normaltest(group1))
        index_out1 = index_out1 + ['Kurtosis','Normal']
    if len(group1) >= 2000:
        metrics_out1.append(stats.jarque_bera(group1))
        index_out1.append('Jarque-Bera')
    norm_metrics1 = pd.DataFrame(metrics_out1, index = index_out1)
    
    if s2 != None:
        metrics_out2 = []
        index_out2 = ['Shapiro','Skew']
        metrics_out2.append(stats.shapiro(group2))
        metrics_out2.append(stats.skewtest(group2))
        if len(group2) >= 20:
            metrics_out2.append(stats.kurtosistest(group2))
            metrics_out2.append(stats.normaltest(group2))
            index_out2 = index_out2 + ['Kurtosis','Normal']
        if len(group2) >= 2000:
            metrics_out2.append(stats.jarque_bera(group2))
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
    
    
    #THIS NEEDS S2
def run_nonparametric_tests(group1, group2, s1, s2, alternative = 'two-sided', output = "/output/"):
    
    metrics_out = []
    index_out = ['Mann-Whitney','Wilcoxon Rank-Sum','BWS','Cramer-Von Mises','Epps-Singleton','Kolmogorov-Smirnov']
    metrics_out.append(stats.mannwhitneyu(group1, group2, alternative = alternative))
    metrics_out.append(stats.ranksums(group1, group2, alternative = alternative))
    metrics_out.append(stats.bws_test(group1, group2, alternative = alternative))
    metrics_out.append(stats.cramervonmises_2samp(group1, group2, alternative = alternative))
    metrics_out.append(stats.epps_singleton_2samp(group1, group2, alternative = alternative))
    metrics_out.append(stats.ks_2samp(group1, group2, alternative = alternative))
    
    index_out = index_out + ['Brunner-Munzel','Mood','Ansari']
    #to test equal ratio of outliers
    metrics_out.append(stats.brunnermunzel(group1, group2, alternative = alternative))
    #to test scale parameter of distribution
    metrics_out.append(stats.mood(group1, group2, alternative = alternative))
    metrics_out.append(stats.ansari(group1, group2, alternative = alternative))
    metrics_df = pd.DataFrame(metrics_out, index = index_out)
    metrics_df.to_csv(output + 'Non_Parametric_Tests.csv')
    
    
    #THIS NEEDS S2 (but see 1 sample t-test and see 3+ sample anova)
def run_mean_tests(group1, group2, s1, s2, alternative = 'two-sided', output = "/output/"):
    
    metrics_out = []
    index_out = ['T-Test','Wilcoxon','BWS Test']
    metrics_out.append(stats.ttest_ind(group1, group2, alternative = alternative))
    metrics_out.append(stats.wilcoxon(group1, group2, alternative = alternative))
    metrics_out.append(stats.bws_test(group1, group2, alternative = alternative))
    metrics_df = pd.DataFrame(metrics_out, index = index_out)
    metrics_df.to_csv(output + 'Mean_Tests.csv')
    
    
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
    
    