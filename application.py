import argparse
import pandas as pd
import logging

from app.summary_stats import generate_summary_stats
from app.stat_tests import run_normal_tests, run_nonparametric_tests, run_mean_tests, run_association_tests

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
        "-o", "--output_folder", help="Output directory for model, predictions and fit metrics", type=str, required=False, default='output/'
    )
    args = parser.parse_args()
    
    if not os.path.exists('/data/' + args.output_folder):
        # Create the directory
        os.makedirs('/data/' + args.output_folder)
    
    #data is mount point
    data = pd.read_csv('/data/' + args.data)
    
    group1, group2, metadata = generate_summary_stats(data = data, s1 = args.sample1, s2 = args.sample2, missing_treatment = args.missing_treatment, output = args.output_folder)
    logging.info("Summary stats generated")
    
    run_normal_tests(group1, group2, s1 = args.sample1, s2 = args.sample2, alternative = args.alternative, output = args.output_folder)
    logging.info("Normal tests run")
    
    run_nonparametric_tests(group1, group2, s1 = args.sample1, s2 = args.sample2, alternative = args.alternative, output = args.output_folder)
    logging.info("Non-parametric tests run")
    
    run_mean_tests(group1, group2, s1 = args.sample1, s2 = args.sample2, alternative = args.alternative, output = args.output_folder)
    logging.info("Mean tests run")
    
    run_association_tests(group1, group2, s1 = args.sample1, s2 = args.sample2, alternative = args.alternative, distribution = args.distribution, output = args.output_folder)
    logging.info("Association tests run")
    