import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

from app.common_functions import process_missing


def generate_histograms(array, column, bins = 20, output = "/output/"):
    res = stats.cumfreq(array, numbins=bins)
    x = res.lowerlimit + np.linspace(0, res.binsize*res.cumcount.size, res.cumcount.size)
    fig = plt.figure(figsize=(15, 6))
    ax1 = fig.add_subplot(1, 2, 1)
    ax2 = fig.add_subplot(1, 2, 2)
    ax1.hist(array, bins=bins)
    ax1.set_title('Relative frequency histogram')
    ax2.bar(x, res.cumcount, width=res.binsize)
    ax2.set_title('Cumulative histogram')
    ax2.set_xlim([x.min(), x.max()])
    plt.savefig(output + f'histogram_{column}.png')
    return output + f'histogram_{column}.png'
    

def calc_mode(data, column):
    mode_list = data[column].mode()
    if len(mode_list) == 1:
        mode_out = mode_list[0]
    else:
        mode_out = np.NaN
    return mode_out
        
        
def generate_summary_stats(data, s1, s2 = None, missing_treatment = 'drop', output = "/output/"):
    
    metadata = {}
    metadata['nobs'] = data.shape[0]
    
    # Get data and handle missing data
    data[s1] = pd.to_numeric(data[s1], errors='coerce')
    missing1 = data[s1].isna().sum()
    group1 = process_missing(data, s1, missing_treatment)
    if s2 != None:
        data[s2] = pd.to_numeric(data[s2], errors='coerce')
        missing2 = data[s2].isna().sum()
        group2 = process_missing(data, s2, missing_treatment)    
    
    # DescribeResult(nobs=12, minmax=(17, 25), mean=21.0, variance=7.454545454545453, skewness=0.027991172768634366, kurtosis=-1.4187983343248067)
    descriptive1 = stats.describe(group1)
    if s2 != None:
        descriptive2 = stats.describe(group2)
        
    # lower, upper quartiles, median, mode
    range1 = np.quantile(group1, [0,0.25,0.5,0.75,1])
    mode1 = calc_mode(data, s1)

    if s2 != None:
        range2 = np.quantile(group1, [0,0.25,0.5,0.75,1])
        mode2 = calc_mode(data, s2)
    
    # Table1: Observations, Missing, Mean, Mode, Variance, Stdev, Skewness, Kurtosis
    input_metrics1 = [metadata['nobs'], missing1, str((missing1/metadata['nobs'])*100)+"%", descriptive1[2], mode1, descriptive1[3], descriptive1[3]**(0.5), descriptive1[4], descriptive1[5]]
    if s2 == None:
        Table1 = pd.DataFrame(input_metrics1, index = ['Observations','Missing/Invalid','Missing Percent','Mean','Mode','Variance','Standard Deviation','Skewness','Kurtosis'], columns = [s1])
    else:
        input_metrics2 = [metadata['nobs'], missing2, str((missing2/metadata['nobs'])*100)+"%", descriptive2[2], mode2, descriptive2[3], descriptive2[3]**(0.5), descriptive2[4], descriptive2[5]]
        Table1 = pd.DataFrame([input_metrics1,input_metrics2], columns = ['Observations','Missing Count','Missing Percent','Mean','Mode','Variance','Standard Deviation','Skewness','Kurtosis'], index = [s1,s2]).T
    Table1.to_csv(output + 'Descriptive_Statistics.csv')
    stat_tables_out =  [{'file': output + 'Descriptive_Statistics.csv',
                         'title': 'Descriptive Statistics'}]
      
    # Table2: Min, Lower Quartile, Median, Upper Quartile, Max
    if s2 == None:    
        Table2 = pd.DataFrame(range1, index = ['Min','Lower Quartile','Median','Upper Quartile','Max'], columns = [s1])
    else:
        Table2 = pd.DataFrame([range1,range2], columns = ['Min','Lower Quartile','Median','Upper Quartile','Max'], index = [s1,s2]).T
    Table2.to_csv(output + 'Range_Statistics.csv')
    stat_tables_out.append({'file': output + 'Range_Statistics.csv',
                         'title': 'Range Statistics'})
    
    # Box plot of group1 and group2
    if s2 == None:
        plt.boxplot(group1, vert=True, labels=[s1])
        plt.savefig(output + 'boxplots.png')
    else:
        plt.boxplot([group1,group2], vert=True, labels=[s1,s2])
        plt.savefig(output + 'boxplots.png')
    stat_plots_out = [{'file': output + 'boxplots.png',
                       'title': 'Boxplots'}]
    
    # Frequency stats
    title = generate_histograms(group1, s1, bins = 20, output = output)
    stat_plots_out.append({'file': title,
                       'title': "Histograms (Sample 1)"})
    if s2 != None:
        title = generate_histograms(group2, s2, bins = 20, output = output)
        stat_plots_out.append({'file': title,
                           'title': "Histograms (Sample 2)"})
        
    return group1, group2, metadata, stat_tables_out, stat_plots_out