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
import sortseq.gauge_fix as gauge_fix
from Bio import Seq

# Define commandline wrapper
def wrapper(args):    
    # Run funciton
    if args.i:
        df = pd.io.parsers.read_csv(args.i,delim_whitespace=True)
    else:
        df = pd.io.parsers.read_csv(sys.stdin,delim_whitespace=True)

    headers = utils.get_column_headers(df)
    df['ct'] = df[headers].sum(axis=1)
    df = df[['ct'] + headers + ['seq']]
    if args.out:
        outloc = open(args.out,'w')
    else:
        outloc = sys.stdout
    

    pd.set_option('max_colwidth',int(1e8))
    
    df.to_string(
        outloc, index=False,col_space=10,float_format=utils.format_string)
# Connects argparse to wrapper
def add_subparser(subparsers):
    p = subparsers.add_parser('format_old_to_new')
    p.add_argument(
        '-i','--i',default=False,help='''Read input from file instead 
        of stdin''')
    p.add_argument('-t','--type',default='dna',choices=['dna','rna','protein'])
    p.add_argument('-o', '--out', default=None)
    p.set_defaults(func=wrapper)
