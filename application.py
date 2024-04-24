import argparse
import pandas as pd
import logging
import json

from app.summary_stats import generate_summary_stats
from app.stat_tests import run_normal_tests, run_nonparametric_tests, run_mean_tests, run_association_tests
from app.common_functions import generate_output_json

if __name__ == "__main__":
    
    import os
        
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
    parser.add_argument(
        "-o", "--output_folder", help="Output directory for model, predictions and fit metrics", type=str, required=False, default='output/'
    )
    args = parser.parse_args()
    
    output_dir = '/data/' + args.output_folder
    if not os.path.exists(output_dir):
        # Create the directory
        os.makedirs(output_dir)
    
    #data is mount point
    data = pd.read_csv('/data/' + args.data)
    
    group1, group2, metadata, stat_tables_out, stat_plots_out = generate_summary_stats(data = data, s1 = args.sample1, s2 = args.sample2, missing_treatment = args.missing_treatment, output = output_dir)
    print("Summary stats generated")
    
    norm_table_out = run_normal_tests(group1, group2, s1 = args.sample1, s2 = args.sample2, alternative = args.alternative, output = output_dir)
    print("Normal tests run")

    npara_table_out = run_nonparametric_tests(group1, group2, s1 = args.sample1, s2 = args.sample2, alternative = args.alternative, output = output_dir)
    print("Non-parametric tests run")
    
    mean_table_out = run_mean_tests(group1, group2, s1 = args.sample1, s2 = args.sample2, alternative = args.alternative, output = output_dir)
    print("Mean tests run")
    
    assoc_table_out = run_association_tests(group1, group2, s1 = args.sample1, s2 = args.sample2, alternative = args.alternative, distribution = args.distribution, output = output_dir)
    print("Association tests run")
    
    response_dict = generate_output_json(stat_tables_out, stat_plots_out, norm_table_out, npara_table_out, mean_table_out, assoc_table_out)
    
    json_string = json.dumps(response_dict)  # Optional: specify indentation
    os.chdir("/")
    with open("'/app/results_for_payload.json'", "w") as outfile:
        outfile.write(json_string)
    with open("'/app/results_for_upload.json'", "w") as outfile:
        outfile.write(json_string)
    
    print(os.listdir(args.output))