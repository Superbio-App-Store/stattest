def process_missing(data, column, missing_treatment = 'drop'):
    if missing_treatment == 'drop':
        imputed = data[column].dropna()
    elif missing_treatment == 'mean':
        mean = data[column].mean()
        imputed = data[column].fillna(mean)
    elif missing_treatment == 'ffill':
        imputed = data[column].fillna(method='ffill')
    array = imputed.to_numpy()
    return(array)


def generate_output_json(stat_tables_out, stat_plots_out, norm_table_out, npara_table_out, mean_table_out, assoc_table_out):
    
    tables = {'Descriptive Statistics': stat_tables_out,
              'Tests for Normal Distribution': norm_table_out,
              'Non-Parametric Tests': npara_table_out,
              'Mean Tests': mean_table_out,
              'Tests for Association': assoc_table_out}
    
    images = {'Descriptive Statistics': stat_plots_out}
    
    return {'tables': tables, 'images': images}