import logging
import subprocess
import traceback
import time
import sys
import json
from os.path import exists
from sbioapputils.app_runner.app_runner_utils import AppRunnerUtils
from sbioapputils.app_runner.workflow_utils import parse_workflow, set_defaults, set_numeric, create_directories, validate_request, remove_empty_keys
from sbioapputils.app_runner.dev_utils import get_yaml, payload_from_yaml


def _process_stage(stage_name, stage_value, config):
    logging.info(f'Stage {stage_name} starting')
    start_time = time.time()
    sub_process_list = ['python', 'app/' + stage_value['file']]
    for key, value in config.items():
        sub_process_list.append("--" + key)
        sub_process_list.append(str(value))
    for key, value in config['input_files'].items():
        sub_process_list.append("--" + key)
        sub_process_list.append(str(value))
    logging.info(sub_process_list)
    process = subprocess.Popen(sub_process_list, stdout=subprocess.PIPE)
    while True:
        line = process.stdout.readline()
        if not line:
            break
        logging.info(line.rstrip())

    if process.returncode is not None:
        logging.info(f"Error occurred in subprocess {stage_name}")
        logging.info(process.returncode)
        raise Exception(f"Error occurred in subprocess {stage_name}, with code {process.returncode}")

    end_time = time.time()
    logging.info(f'Stage {stage_name} completed in {end_time - start_time} seconds')


def _upload_results(job_id: str):

    #reads payload json if generated by code, otherwise gets from yaml
    if (exists('/app/results_for_payload.json')) and (exists('/app/results_for_upload.json')):
        logging.info("Generating payload from custom json")
        with open('/app/results_for_payload.json', 'r') as f:
            results_for_payload = json.load(f)
        with open('/app/results_for_upload.json', 'r') as f:
            results_for_upload = json.load(f)
    else:
        logging.info("Generating payload from yaml file")
        results_for_payload, results_for_upload = payload_from_yaml('/app/workflow.yml')
    #results_for_payload = remove_empty_keys(results_for_payload)
    
    #upload results
    logging.info('Payload:')
    logging.info(results_for_payload)

    #AppRunnerUtils.upload_results(job_id, results_for_payload)
    logging.info('Uploading artifacts:')
    logging.info(results_for_upload)
    for element in results_for_upload:
        AppRunnerUtils.upload_file(job_id, element)
    AppRunnerUtils.set_job_completed(job_id, results_for_payload)


def main():
    job_log_file = 'job.log'
    AppRunnerUtils.set_logging(job_log_file)
    job_id = sys.argv[1]
    try:
        request = AppRunnerUtils.get_job_config(job_id)
        stages, parameters = parse_workflow(request)
        request = set_defaults(request, parameters, job_id)
        request = set_numeric(request, parameters)
        request = create_directories(request, parameters)
        logging.info('Workflow parsed')
        logging.info(f'Job config: {request}')
        
        output_errors = validate_request(request, parameters)
        if output_errors:
            raise Exception(f"Invalid json request:\n {output_errors}")
        
        AppRunnerUtils.set_job_running(job_id)
        logging.info(f'Job {job_id} is running')
        
        for stage_name, stage_value in stages.items():
            _process_stage(stage_name, stage_value, request)
        _upload_results(job_id)
        
    except Exception as e:
        err = str(e)
        AppRunnerUtils.set_job_failed(job_id, err)
        logging.error(traceback.format_exc())
        
    finally:
        # upload log files to S3
        AppRunnerUtils.upload_file(job_id, job_log_file)


if __name__ == '__main__':
    main()
