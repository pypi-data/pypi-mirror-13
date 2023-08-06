#!/usr/bin/env python

'''Script with find the probabilities of any one base being mutated to any other.
    This could reveal biases in the mutation rate.'''
from __future__ import division
#Our standard Modules
import argparse
import numpy as np
import sys

import pandas as pd
import sortseq.utils as utils
from Bio import Seq



def main(df,dicttype):
    seq_dict,inv_dict=utils.choose_dict(dicttype)
    rename_dict = {'ct_'+str(inv_dict[i]):str(inv_dict[i]) for i in range(0,len(seq_dict))}
    column_headers = [str(inv_dict[i]) for i in range(0,len(seq_dict))]
    df.rename(inplace=True,columns={'pos':'# POSITION'})
    df.rename(inplace=True,columns=rename_dict)
    df['WT'] = df[column_headers].idxmax(axis=1)
    #reorder columns
    first_row = '# POSITION WT' + ''.join([' ' + column_headers[i] for i in range(len(seq_dict))]) +'\n'
    df = df[['# POSITION','WT'] + column_headers]
    return df,first_row

# Define commandline wrapper
def wrapper(args):    
    # Run funciton
    if args.i:
        df = pd.io.parsers.read_csv(args.i,delim_whitespace=True)
    else:
        df = pd.io.parsers.read_csv(sys.stdin,delim_whitespace=True)

    output_df,first_row = main(df,args.type)
    if args.out:
        outloc = open(args.out,'w')
    else:
        outloc = sys.stdout
    outloc.write(first_row)

    pd.set_option('max_colwidth',int(1e8))
    
    output_df.to_string(
        outloc, index=False,justify='left',float_format=utils.format_string,header=False)
# Connects argparse to wrapper
def add_subparser(subparsers):
    p = subparsers.add_parser('format_for_dms')
    p.add_argument(
        '-i','--i',default=False,help='''Read input from file instead 
        of stdin''')
    p.add_argument('-t','--type',default='dna',choices=['dna','rna','protein'])
    p.add_argument('-o', '--out', default=None)
    p.set_defaults(func=wrapper)
