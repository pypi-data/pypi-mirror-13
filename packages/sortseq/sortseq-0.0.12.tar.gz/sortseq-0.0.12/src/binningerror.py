#!/usr/bin/env python

'''A script which calculates the number of each base at each position.'''
from __future__ import division
#Our standard Modules
import argparse
import numpy as np
import sys

import pandas as pd
import itertools
import scipy as sp
import sortseq.utils as utils
import sortseq.predictiveinfo as predictiveinfo
import sortseq.learn_matrix as learn_matrix



def main(df_for_err,dicttype,start=0,end=None):
    
    seq_dict,inv_dict = utils.choose_dict(dicttype)
    df_for_err['seq'] = df_for_err['seq'].str.slice(start,end)
    #if there are less than 7 bins, do all combos of 2, otherwise do 15
    col_headers = utils.get_column_headers(df_for_err)
    if len(col_headers) < 7:
         MI = np.zeros(int(sp.misc.comb(len(col_headers),2)))
         for i,col_pair in enumerate(itertools.combinations(col_headers,2)):            
              col_pair_list = list(col_pair)
              #Add sequences to list of columns to be passed to learn_matrix    
              col_pair_list.append('seq')
              model_df = learn_matrix.main(df_for_err[col_pair_list],'dna','iterative_LS')
              MI[i],std = predictiveinfo.main(df_for_err,model_df,no_err=True)
    else:
         MI = np.zeros(15)
         for i in range(15):
              col_pair_list = list(sp.random.choice(col_headers,5,replace=False))
              col_pair_list.append('seq')
              print df_for_err[col_pair_list]
              model_df = learn_matrix.main(df_for_err[col_pair_list],'dna','iterative_LS')
              MI[i],std = predictiveinfo.main(df_for_err,model_df,no_err=True)
              print MI
    print MI
    return pd.DataFrame([np.std(MI)])


# Define commandline wrapper
def wrapper(args):
    

    
    # Run funciton
    if args.i:
        df = pd.io.parsers.read_csv(args.i,delim_whitespace=True)
    else:
        df = pd.io.parsers.read_csv(sys.stdin,delim_whitespace=True)
    
    output_df = main(
        df,args.type,start=args.start,end=args.end)
    
    

    if args.out:
        outloc = open(args.out,'w')
    else:
        outloc = sys.stdout
    pd.set_option('max_colwidth',int(1e8))
    output_df.to_string(
        outloc, index=False,col_space=10,float_format=utils.format_string)

# Connects argparse to wrapper
def add_subparser(subparsers):
    p = subparsers.add_parser('binningerror')
    p.add_argument('-t', '--type', choices=['dna','rna','protein'], default='dna')
    p.add_argument(
        '-i', '--i', default=None,help='''Input file, otherwise input
        through the standard input.''')
    p.add_argument(
        '-s','--start',type=int,default=0,help ='''Position to start 
        your analyzed region''')
    p.add_argument(
        '-e','--end',type=int,default = None, help='''Position to end 
        your analyzed region''')
    p.add_argument('-o', '--out', default=None)
    p.set_defaults(func=wrapper)
