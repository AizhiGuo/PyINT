#! /usr/bin/env python
#################################################################
###  This program is part of PyINT  v1.0                      ### 
###  Copy Right (c): 2017, Yunmeng Cao                        ###  
###  Author: Yunmeng Cao                                      ###                                                          
###  Email : ymcmrs@gmail.com                                 ###
###  Univ. : Central South University & University of Miami   ###   
#################################################################

import numpy as np
import os
import sys  
import subprocess
import getopt
import time
import glob

def check_variable_name(path):
    s=path.split("/")[0]
    if len(s)>0 and s[0]=="$":
        p0=os.getenv(s[1:])
        path=path.replace(path.split("/")[0],p0)
    return path

def read_template(File, delimiter='='):
    '''Reads the template file into a python dictionary structure.
    Input : string, full path to the template file
    Output: dictionary, pysar template content
    Example:
        tmpl = read_template(KyushuT424F610_640AlosA.template)
        tmpl = read_template(R1_54014_ST5_L0_F898.000.pi, ':')
    '''
    template_dict = {}
    for line in open(File):
        line = line.strip()
        c = [i.strip() for i in line.split(delimiter, 1)]  #split on the 1st occurrence of delimiter
        if len(c) < 2 or line.startswith('%') or line.startswith('#'):
            next #ignore commented lines or those without variables
        else:
            atrName  = c[0]
            atrValue = str.replace(c[1],'\n','').split("#")[0].strip()
            atrValue = check_variable_name(atrValue)
            template_dict[atrName] = atrValue
    return template_dict


def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
    
def add_zero(s):
    if len(s)==1:
        s="000"+s
    elif len(s)==2:
        s="00"+s
    elif len(s)==3:
        s="0"+s
    return s


def usage():
    print('''
******************************************************************************************************
 
           Select interferometry pairs from time series SAR images
     
      usage:
   
            SelectPairs_Coherence.py projectName ifg_coherence.txt min_cor
      
      e.g.  SelectPairs_Coherence.py projectName coherence_spatialAverage.txt 0.6
          
            
*******************************************************************************************************
    ''')   
    
def main(argv):
    
    if len(sys.argv)==4:
        if argv[0] in ['-h','--help']: usage(); sys.exit(1)
        else: 
            projectName = sys.argv[1]
            TXT=sys.argv[2]
            MC=sys.argv[3]
    else:
        usage();sys.exit(1)
        
    scratchDir = os.getenv('SCRATCHDIR')
    templateDir = os.getenv('TEMPLATEDIR')
    templateFile = templateDir + "/" + projectName + ".template"
    templateContents=read_template(templateFile)
    processDir = scratchDir + '/' + projectName + "/PROCESS"
    IFG_PAIRS = scratchDir + '/' + projectName + "/PROCESS/ifg_coherence_" + MC 
    RUN_IFG = scratchDir + '/' + projectName + "/PROCESS/run_slc2ifg_coherence_" + MC 
    
    if os.path.isfile(IFG_PAIRS):
        os.remove(IFG_PAIRS)
    if os.path.isfile(RUN_IFG):
        os.remove(RUN_IFG)
    
    IFGLIST = glob.glob(processDir+'/*_' +projectName + '_*')
    LIST0=[]
    for kk in IFGLIST:
        SS = os.path.basename(kk)
        L0 = SS.split('_')[2]
        kk0 = SS.split(L0)[0]+ L0     
        LIST0.append(kk0)
    
    if not os.path.isdir(processDir):
        call_str='mkdir ' + processDir
        os.system(call_str)
    
    B =[]
    A = np.loadtxt(TXT,dtype=str)
    for kk in range(len(A[:,0])):
        CC = float(A[kk,1])
        if CC > float(MC):
            ff = A[kk,0]
            master = ff.split('-')[0]
            slave  = ff.split('-')[1]
            slave = str(int(slave))
            if len(slave)==5:
                slave = '0'+slave 
            SS = master + '-' + slave
            call_str = 'echo ' + SS + ' >>' + IFG_PAIRS
            os.system(call_str)
            
            STR = 'IFG' + '_' + projectName + '_' + master + '-' + slave + '_1000_1000'
            STR0 =  'IFG' + '_' + projectName + '_' + master + '-' + slave
        
            if not STR0 in LIST0:
                B.append(STR0)
                call_str = 'echo SLC2Ifg_Gamma.py ' + STR + ' >>' + RUN_IFG
                os.system(call_str)
                
                #call_str ='mkdir ' + processDir+'/' + STR
                #os.system(call_str)
                print('Add interferogram directory ' + STR + ' \n')
    print('%s interferograms are generated. ' % str(len(B)))

    sys.exit(1)
    
if __name__ == '__main__':
    main(sys.argv[:])

    
