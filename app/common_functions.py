from sbioapputils.app_runner.app_runner_utils import AppRunnerUtils
import pandas as pd
from pandas.api.types import is_numeric_dtype
from custom_logging import send_log
import os


#.csv or .h5ad
def load_data(datapath, save_dir):
    filename = datapath.split('/')[-1]
    destination = save_dir + '/' + filename
    AppRunnerUtils.download_file(source_file_path = datapath, dest_file_path = destination)
    
    try:
        send_log(f"{os.listdir(save_dir + '/')}")
        data = pd.read_csv(save_dir + '/' + filename)
        return data
    except:
        raise Exception(f"Could not read data. Check data format is tabular and saved in csv, tsv or txt format.")


def load_key():
    AppRunnerUtils.download_file(source_file_path = 'apps/stat_test/resources/open_key.txt', dest_file_path = 'open_key.txt')
    with open('open_key.txt', 'r') as file:
        okey = file.read().rstrip()
    return okey


def process_missing(data, columns, missing_treatment = 'drop'):
    
    if missing_treatment == 'drop':
        for column in columns:
            imputed = data.dropna(subset=[column], how='all')
    elif missing_treatment == 'mean':
        for column in columns:
            mean = data[column].mean()
            data[column] = data[column].fillna(mean)
        imputed = data
    elif missing_treatment == 'ffill':
        for column in columns:
            data[column] = data[column].fillna(method='ffill')
        imputed = data
    return(imputed)


def generate_output_json(stat_tables_out, stat_plots_out, norm_table_out, npara_table_out, mean_table_out, assoc_table_out, figures):
    
    tables = [stat_tables_out, norm_table_out, npara_table_out, mean_table_out, assoc_table_out]
    
    images = [stat_plots_out]
    
    return {'tables': tables, 'images': images, #'figures': [figures],
            'download': figures}


def sensible_names(text_in, length = 10):
    text_out = text_in.replace(" ","_")[:length]
    return(text_out)
