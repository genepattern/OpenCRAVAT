#!/usr/bin/env python
# -*- coding: utf-8 -*-

import warnings

warnings.filterwarnings('ignore')

__tool_name__='OpenCRAVAT'
import argparse
import os
import sys
import requests
import time
import shutil
from requests.auth import HTTPBasicAuth


print('- OpenCravat Module - remote API -',flush=True)
    
def run_opencravat(input_file='example_input', username='', password='', annotators='["clinvar", "ncbigene"]', base_url='https://run.opencravat.org'):
    login_url = f'{base_url}/server/login'
    submit_url = f'{base_url}/submit/submit'
    session = requests.Session()
    print(f'Logging in...')
    print("annotating with "+ annotators, flush=True)
    s = session.get(login_url, auth=HTTPBasicAuth(username, password))
    print("Login succesful... trying " + submit_url)

    s = session.post(submit_url, files={'file_0': open(input_file)}, data={'options': '{"annotators": ['+annotators+'], "reports": ["text"], "assembly": "hg38", "note": "test run"}'})
    print("job submitted")
    jobid = s.json()['id']
    print(f'Job submitted. Job ID={jobid}')
    status_url = f'{base_url}/submit/jobs/{jobid}/status'

    while True:
        r = session.get(status_url)
        if r.json()['status'] != 'Finished':
            #uio.status = 'Running'
            print(f'Waiting for the job to finish...', flush=True)
            time.sleep(5)
        else:
            break

    report_url = f'{base_url}/submit/jobs/{jobid}/reports/tsv'
    report_list_url = f'{base_url}/submit/jobs/{jobid}/reports'
    s = session.get(report_list_url)
    if 'tsv' not in s.json():
        #uio.status = 'Generating Report'
        print(f'Generating a TSV report...')
        s = session.post(report_url)
        if s.json() == 'done':
            #uio.status = 'Success'
            print(f'TSV report generation is done.')
    s = session.get(report_url, stream=True)
    wf = open(f'{jobid}.tsv.zip', 'wb')
    shutil.copyfileobj(s.raw, wf)
    del s
    wf.close()
    # https://run.opencravat.org/result/index.html?job_id=
    index  = open(f'{jobid}.html', 'w')
    index.write("<html><head><meta http-equiv=\"refresh\" content=\"0; url=https://run.opencravat.org/result/index.html?job_id="+jobid+"\"/></head></html>")
    index.close()


def main():
    parser = argparse.ArgumentParser(description='%s Parameters' % __tool_name__ ,formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-i", "--input-file", dest="input_filename",default = None, help="input file name", metavar="FILE")
    parser.add_argument("-user",dest="user",  default='',  help="OpenCravat account User name")
    parser.add_argument("-pass",dest="ocpassword", default='',  help="OpenCravat account password")   

    for x in range(1,21):
        parser.add_argument("-ann"+str(x), "--annotators"+str(x), dest="ann"+str(x),default = '', help="annotator ")

    args = parser.parse_args()
    print(args)    
    print('Starting procedure...')
    workdir = "./"
    annotators = [] 
    
    # collect all the annotators, split on the comma and make into lists which we concatenate    
    for x in range(1,4):
        annlist = eval("args.ann"+str(x)+"")
        moreanns = list(filter(lambda x: x != "", annlist.split(',')))
        annotators = annotators + moreanns
 
    # remove duplicates 
    annotators = list(set(annotators))
    
    if len(annotators) == 0:
        print("No OpenCRAVAT annotators selected.  Exitting.")
        exit(999)

    # now format the list of annotators the way the web service likes it
    m = map(lambda x: "\"" +x + "\"", annotators) 
    annString = ",".join(list(m))
    print("AnnString is " + annString)

    run_opencravat(input_file=args.input_filename, username=args.user , password=args.ocpassword ,  annotators=annString, base_url='https://run.opencravat.org')




    print('Finished computation.')

if __name__ == "__main__":
    main()
