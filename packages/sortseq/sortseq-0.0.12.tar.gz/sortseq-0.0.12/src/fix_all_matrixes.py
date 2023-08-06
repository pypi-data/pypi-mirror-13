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
import glob
import sst.gauge_fix as gauge_fix



def main(myinput,dicttype):
    lin_seq_dict,lin_inv_dict = utils.choose_dict(dicttype)
    pair_seq_dict,pair_inv_dict = utils.choose_dict(dicttype,modeltype='NBR')
    filenames = glob.glob(myinput + '*')
    print filenames
    lin_headers = ['val_' + str(lin_inv_dict[i]) for i in range(len(lin_seq_dict))]
    pair_headers = ['val_' + str(pair_inv_dict[i]) for i in range(len(pair_seq_dict))]
    pd.set_option('max_colwidth',int(1e8))
    for fn in filenames:
        try:
            df = pd.io.parsers.read_csv(fn,delim_whitespace=True)
        except:
            print str(fn) + ' is not a dataframe'
        if set(lin_headers).issubset(df.columns):
            emat = np.array(df[lin_headers])
            emat = gauge_fix.fix_matrix(emat)
            df[lin_headers] = emat
        elif set(pair_headers).issubset(df.columns):
            emat = np.array(df[pair_headers])
            emat = gauge_fix.fix_neighbor(emat)
            df[pair_headers] = emat
        else:
            print str(fn) + 'is not a model'
            continue
        print 'converting ' + str(fn)
        outloc = open(fn + '.c','w')
        df.to_string(
            outloc, index=False,col_space=10,float_format=utils.format_string)
    return 0

# Define commandline wrapper
def wrapper(args):    
    # Run funciton

    output_df = main(args.i,args.type)
    
    
# Connects argparse to wrapper
def add_subparser(subparsers):
    p = subparsers.add_parser('fix_all_matrixes')
    p.add_argument(
        '-i','--i',default=False,help='''Read input from file instead 
        of stdin''')
    p.add_argument(
        '-t', '--type', choices=['dna','rna','protein'], default='dna')
    p.add_argument('-o', '--out', default=None)
    p.set_defaults(func=wrapper)
