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
    