from __future__ import division
#Our standard Modules
import argparse
import numpy as np
import sys
import os
import pandas as pd
import sortseq.utils as utils
import csv, gzip, subprocess, sys, glob
from Bio import SeqIO


'''
def wrapper(args):
    filelist_df = pd.io.parsers.read_csv(args.i,delim_whitespace=True)
    pd.set_option('max_colwidth',int(1e8))    
    for item in filelist_df.iterrows():
        output_df = pd.DataFrame()
        temp_df = pd.DataFrame()
        output_df['seq'] = collatedmat(item[1]['file'])
        savefn = 'bin_' + str(item[1]['bin']) + '_' + item[1]['file']
        output_df.to_string(open(savefn,'w'), index=False,col_space=10,float_format=utils.format_string)
'''

def wrapper(args):
    filelist = glob.glob(args.i + '*')
    print os.path.join('args.i')
    print filelist
    pd.set_option('max_colwidth',int(1e8))    
    for item in filelist:
        if '.fastq' in item:
            isfastq = True
        else:
            isfastq = False
        savefn = item + '_seq.txt'
        print savefn
        f = open(savefn,'w')
        f.writelines(['seq','\n'])
        fastafile = open(item,'r')
        if isfastq:
            for record in SeqIO.parse(fastafile,'fastq'):
                 f.writelines([str(record.seq),'\n'])
        else:
            for record in SeqIO.parse(fastafile,'fasta'):
                 f.writelines([str(record.seq),'\n'])
        fastafile.close()
        
        f.close()

def add_subparser(subparsers):
    p = subparsers.add_parser('convert_fastq_to_seqs')
    p.add_argument(
        '-i','--i',default=False,help='''Read input from file instead 
        of stdin''')
    p.set_defaults(func=wrapper)
