#!/usr/bin/env python

'''A script which calculates the total sequence dependent information available
     in a sublibrary.''' 
from __future__ import division
import argparse
import numpy as np
import sys

import sortseq.utils as utils
import pandas as pd
import sortseq.Sublib as Sublib
import sortseq.nsbestimator as nsb

def main(df,mpra):
    
    nbins = 0    
    include = True
    
    column_headers = utils.get_column_headers(df)
    seqs_arr = np.array(df[column_headers])
    
    pbatch = np.sum(seqs_arr,axis=1)
    totalseqs = np.sum(pbatch)
    originalent = nsb.S(pbatch,np.sum(pbatch),len(pbatch))
    partialent = 0
    V = 0
    
    for z in range(len(column_headers)):
         partialent = partialent + np.sum(seqs_arr[:,z])/totalseqs*nsb.S(seqs_arr[:,z],np.sum(seqs_arr[:,z]),len(seqs_arr[:,z]))
         V = V + np.sum(seqs_arr[:,z])/totalseqs*nsb.dS(seqs_arr[:,z],np.sum(seqs_arr[:,z]),len(seqs_arr[:,z]))
    MI = float(originalent - partialent)
    V = np.sqrt(float(V))
    
    
    #Determine Expression Cutoffs for bins
     
    
    return MI,np.sqrt(V)

# Define commandline wrapper
def wrapper(args):
    mpra = args.ReporterArray
    # Run funciton
    if args.i:
        df = pd.io.parsers.read_csv(args.i,delim_whitespace=True)
    else:
        df = pd.io.parsers.read_csv(sys.stdin,delim_whitespace=True)
    
    df['seq'] = df['seq'].str.slice(args.start,args.end)
    
    df = utils.collapse_further(df)
    
    MI,V = main(df,mpra)
    output_df = pd.DataFrame(pd.Series(MI,name='MI'))
    output_df = pd.concat([output_df, pd.Series(V,name='Var')],axis=1)
    
    output_df.columns = ['MI','std']
    
    if args.out:
        outloc = open(args.out,'w')
    else:
        outloc = sys.stdout
    pd.set_option('max_colwidth',int(1e8))
    output_df.to_string(outloc, index=False,col_space=10,float_format=utils.format_string)

# Connects argparse to wrapper
def add_subparser(subparsers):
    p = subparsers.add_parser('totalinfo')
    p.add_argument(
        '-i', '--i', default=None,help='''Input file, otherwise input
        through the standard input.''')
    p.add_argument('-mpra','--ReporterArray',default=False,help='''Is the
                experiment a massively parallel reporter assay? Default=False''')
    p.add_argument('-s','--start',type=int,default=0)
    p.add_argument('-e','--end',type=int,default=None)
    p.add_argument('-o', '--out', default=None)
    p.set_defaults(func=wrapper)
