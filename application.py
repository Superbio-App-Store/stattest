import argparse
import json

from summary_stats import generate_summary_stats
from stat_tests import run_normal_tests, run_nonparametric_tests, run_mean_tests, run_association_tests
from common_functions import load_data, generate_output_json
from report import generate_pdf
import os
from os.path import exists
from custom_logging import send_log
import sys


if __name__ == "__main__":
     
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d", "--data", help="Name of file uploaded to container, which contains data", type=str, required=True, default='data.csv'
    )
    parser.add_argument(
        "-s", "--sample1", help="Name of column containing sample1 (or only sample)", type=str, required=True
    )
    parser.add_argument(
        "-s2", "--sample2", help="Name of column containing sample2 (optional)", type=str, required=False, default=None
    )
    parser.add_argument(
        "-m", "--missing_treatment", help="Either drop rows with missing data, or replace missing data with mean of each column", type=str, required=False, default='drop'
    )
    parser.add_argument(
        "-n", "--distribution", help="Non-parametric or normal distribution (support for other distributions to be added in future)", type=str, required=True, default='non-parametric'
    )
    parser.add_argument(
        "-a", "--alternative", help="Two-sided tests (default), greater or less", type=str, required=True, default='two-sided'
    )
    parser.add_argument(
        "-c", "--confidence", help="Confidence-level", type=float, required=False, default=0.95
    )
    args, _ = parser.parse_known_args()
    
    os.chdir("/")
    send_log(f"About to load data from source file path {args.data}")
    data = load_data(args.data, '/data')
    if data.shape[0]<10:
        send_log("Data appears to contain less than 10 records (Or a data processing error has occurred)")
        sys.exit(1)
    
    send_log(f"Data shape: {data.shape}")
    send_log(f"Data columns: {data.columns}")
    
    try:
        group1, group2, metadata, stat_tables_out, stat_plots_out, files_for_upload, tests_list = generate_summary_stats(data = data, s1 = args.sample1, s2 = args.sample2, missing_treatment = args.missing_treatment)
        send_log("Summary stats generated")
    except:
        sys.exit(1)
    
    norm_table_out, norm_file, norm_list = run_normal_tests(group1, group2, s1 = args.sample1, s2 = args.sample2, confidence = args.confidence, alternative = args.alternative)
    files_for_upload.append(norm_file)
    send_log("Norm tests run")
    
    npara_table_out, npara_file, npara_list = run_nonparametric_tests(group1, group2, s1 = args.sample1, s2 = args.sample2, confidence = args.confidence, alternative = args.alternative)
    files_for_upload.append(npara_file)
    send_log("Non-parametric tests run")
    
    mean_table_out, mean_file, mean_list = run_mean_tests(group1, group2, s1 = args.sample1, s2 = args.sample2, confidence = args.confidence, alternative = args.alternative)
    files_for_upload.append(mean_file)
    send_log("Mean tests run")
    
    assoc_table_out, assoc_file, assoc_list = run_association_tests(group1, group2, s1 = args.sample1, s2 = args.sample2, confidence = args.confidence, alternative = args.alternative, distribution = args.distribution, norm_list = norm_list)
    files_for_upload.append(assoc_file)
    send_log("Association tests run")
    
    list_for_report = tests_list + norm_list + npara_list + mean_list + assoc_list
    send_log(f"List for report: {list_for_report}")
    pdf_out, figures = generate_pdf(list_for_report)
    files_for_upload = files_for_upload + pdf_out
    
    send_log(f"Files for upload: {files_for_upload}")
    json_string = json.dumps(files_for_upload)
    with open("/app/results_for_upload.json", "w") as outfile:
        outfile.write(json_string)
        
    response_dict = generate_output_json(stat_tables_out, stat_plots_out, norm_table_out, npara_table_out, mean_table_out, assoc_table_out, figures)
    send_log(f"Response dict: {response_dict}")
    json_string2 = json.dumps(response_dict)
    with open("/app/results_for_payload.json", "w") as outfile:
        outfile.write(json_string2)