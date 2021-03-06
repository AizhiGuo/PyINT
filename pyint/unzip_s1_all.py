#! /usr/bin/env python
#################################################################
###  This program is part of PyINT  v2.1                      ### 
###  Copy Right (c): 2017-2019, Yunmeng Cao                   ###  
###  Author: Yunmeng Cao                                      ###                                                          
###  Contact : ymcmrs@gmail.com                               ###  
#################################################################

import numpy as np
import os
import sys  
import getopt
import time
import glob
import argparse

import subprocess
from pyint import _utils as ut

def work(data0):
    cmd = data0[0]
    err_txt = data0[1]
    p = subprocess.run(cmd, shell=False,stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    stdout = p.stdout
    stderr = p.stderr
    
    if type(stderr) == bytes:
        aa=stderr.decode("utf-8")
    else:
        aa = stderr
        
    if aa:
        str0 = cmd[0] + ' ' + cmd[1] + ' ' + cmd[2] + ' ' + cmd[3] + '\n'
        #print(aa)
        with open(err_txt, 'a') as f:
            f.write(str0)
            f.write(aa)
            f.write('\n')

    return 
#########################################################################

INTRODUCTION = '''
-------------------------------------------------------------------   
       Unzip Sentinel-1 raw dataset for one project.
       [unzip does not need much CPU, so we can use parallel processing]
   
'''

EXAMPLE = '''
    Usage: 
            unzip_s1_all.py projectName
            unzip_s1_all.py projectName --parallel 4
-------------------------------------------------------------------  
'''


def cmdLineParse():
    parser = argparse.ArgumentParser(description='Unzip Sentinel-1 raw dataset for one project.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('projectName',help='projectName for processing.')
    parser.add_argument('--parallel', dest='parallelNumb', type=int, default=1, help='Enable parallel processing and Specify the number of processors.')
    
    inps = parser.parse_args()
    return inps


def main(argv):
    start_time = time.time()
    inps = cmdLineParse() 
    projectName = inps.projectName
    scratchDir = os.getenv('SCRATCHDIR')
    projectDir = scratchDir + '/' + projectName 
    downDir    = scratchDir + '/' + projectName + "/DOWNLOAD"
    raw_file_list = glob.glob(downDir + '/S1*.zip')
    
    slc_dir = scratchDir + '/' + projectName + '/SLC'
    if not os.path.isdir(slc_dir):
        os.mkdir(slc_dir)
    
    err_txt = scratchDir + '/' + projectName + '/unzip_s1_all.err'
    if os.path.isfile(err_txt): os.remove(err_txt)
        
    data_para = []
    for i in range(len(raw_file_list)):
        cmd0 = ['unzip',raw_file_list[i],'-d',downDir]
        data0 = [cmd0,err_txt]
        data_para.append(data0)
    
    ut.parallel_process(data_para, work, n_jobs=inps.parallelNumb, use_kwargs=False)
    os.chdir(downDir)
    print("Unzip Sentinel-1 raw dataset for project %s is done! " % projectName)
    ut.print_process_time(start_time, time.time())
    
    sys.exit(1)
    
if __name__ == '__main__':
    main(sys.argv[:])    
    