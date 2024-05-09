import sys
import os
import openai
from openai.error import APIError, InvalidRequestError
from time import sleep
from common_functions import load_key
from custom_logging import send_log


# read Open AI API key
openai.api_key = load_key()
model = "gpt-3.5-turbo"
outputs = 1
temperature = 0.25
delay = 5


import os

# Disable printing
def blockPrint():
    sys.stdout = open(os.devnull, 'w')

# Restore printing
def enablePrint():
    sys.stdout = sys.__stdout__


def interpret_stats(table):
    messages = [{'role':"system", "content": "I generated some descriptive statistics relating to a dataset. How can I interpret them?"}]
    messages.append({"role": "user", "content": table.to_string()})
    response = openai.ChatCompletion.create(
                model=model,
                messages = messages,
                n=outputs,
                temperature = temperature
                )
    sleep(delay)
    return response['choices'][0]['message']['content']
    
def interpret_tests(table, confidence, distribution = None, norm_outcome = 'none specified.'):
    if distribution == None:
        messages = [{'role':"system", "content": f"I have run some hypothesis tests. How can I interpret the following results, given a confidence level of {round(100*confidence,1)}%"}]
    else:
        messages = [{'role':"system", "content": f'''I have run some hypothesis tests. The distribution is expected to be {distribution}.
Tests were run to determine if the data had a normal distribution, with the following outcome: {norm_outcome}
How can I interpret the following results, given a confidence level of {round(100*confidence,1)}%, while taking into account the outcome of the tests for normality (i.e. should I trust some of these statistics?)'''}]
    messages.append({"role": "user", "content": table.to_string()})
    response = openai.ChatCompletion.create(
                model=model,
                messages = messages,
                n=outputs,
                temperature = temperature
                )
    sleep(delay)
    return response['choices'][0]['message']['content']
    

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, Image, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from PIL import Image as PI
from math import floor
from pandas import MultiIndex


def get_image_dimensions(image_path):
    with PI.open(image_path) as img:
        width, height = img.size
    return width, height

    
def generate_pdf(test_list, output = "outputs/"):
    try:
        blockPrint()
        output_file = output + 'superbio_report.pdf'
        doc = SimpleDocTemplate(output_file, pagesize=A4)
        text_only_file = output + 'text_only_report.pdf'
        text_doc = SimpleDocTemplate(text_only_file, pagesize=A4)
        
        styles = getSampleStyleSheet()
        content = []
        text_only = []
        
        for tests in test_list:
            #add header+table, image, interpretation
            if tests['type'] =='header':
                p = Paragraph(f"<b>{tests['description']}</b>", styles["Heading1"])
                content.append(p)
                text_only.append(p)
            elif tests['type'] =='table':
                metrics_array_of_arrays = []
                metrics_df = tests['object'].round(3)
                if isinstance(metrics_df.columns, MultiIndex):
                    first_level = list(metrics_df.columns.get_level_values(0))
                    metrics_array_of_arrays.append([''] + first_level)
                    metrics_df.columns = metrics_df.columns.get_level_values(1)
                    metrics_array_of_arrays.append(["Test"]+metrics_df.columns.tolist())
                else:
                    metrics_array_of_arrays.append(["Test"]+metrics_df.columns.tolist())
                for index, row in metrics_df.iterrows():
                    row_values = [index]
                    row_values.extend(row.values.tolist())
                    metrics_array_of_arrays.append(row_values)
                table = Table(metrics_array_of_arrays, style=[('GRID', (0,0), (-1,-1), 1, colors.black)])
                content.append(Spacer(1, 16))
                content.append(table)
                content.append(Spacer(1, 16))
            #add images after tables
            elif tests['type'] =='image':
                width, height = get_image_dimensions(tests['object'])
                pil_image = Image(tests['object'], width=floor((200/height)*width), height=200)
                content.append(pil_image)
            #add interpretation as final part of section
            elif tests['type'] =='interpretation':
                lines = tests['object'].split("\n")
                for line in lines:
                    paragraph = Paragraph(line, styles["Normal"])
                    content.append(paragraph)
                    text_only.append(paragraph)
                    #content.append(Spacer(1, 4))
                content.append(Spacer(1, 32))
            #run every iteration for now, to pinpoint the error
        doc.build(content)
        text_doc.build(text_only)
        
        figures = [{'file': output + 'superbio_report.pdf',
                           'title': 'Superbio Report'}]
        enablePrint()
        
    except Exception as e:
        enablePrint()
        send_log("Stat test report generation error")
        send_log(f"{e}")
        send_log(str(tests))
        send_log(str(content))
        figures = [{'file': output + 'superbio_report.pdf',
                           'title': 'Superbio Report'}]
    
    return [output + 'superbio_report.pdf'], figures