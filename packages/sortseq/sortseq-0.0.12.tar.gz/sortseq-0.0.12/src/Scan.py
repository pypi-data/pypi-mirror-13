#!/usr/bin/env python

'''A script which produces linear energy matrix models for a given data set.'''
from __future__ import division
#Our standard Modules
import argparse
import numpy as np
import scipy as sp
import sys
#Our miscellaneous functions
import pandas as pd
import sortseq.utils as utils
import sortseq.Models as Models

def main(wtseq,model,dicttype,modeltype='LinearEmat',is_df=True):
    if modeltype == 'LinearEmat':
        mymodel = Models.LinearModel(model,dicttype,is_df=is_df)
    elif modeltype == 'Neighbor':
        mymodel = Models.NeighborModel(model,dicttype,is_df=is_df)
    
    
    seqs = []
    for i in range(len(wtseq)-len(model.index)):
        seqs.append(wtseq[i:i+len(model.index)])
    seqs_series = pd.DataFrame(seqs,columns={'seq'})
    
    energy = pd.Series(mymodel.genexp(seqs),name='val')
    pos = pd.Series(range(len(wtseq)-len(model.index)),name='start')
    length = pd.Series([len(model.index) for i in range(len(seqs_series))],name='length')
    
    
    output_df = pd.concat([seqs_series,energy,pos,length],axis=1)
    output_df.sort(columns='val',inplace=True)
    return output_df

def wrapper(args):
    model = pd.io.parsers.read_csv(args.model,delim_whitespace=True)
    output_df = main(args.wtseq,model,args.type,modeltype=args.modeltype)

    if args.out:
        outloc = open(args.out,'w')
    else:
        outloc = sys.stdout
    pd.set_option('max_colwidth',int(1e8))
    output_df.to_string(
        outloc, index=False,col_space=10,float_format=utils.format_string)

    


# Connects argparse to wrapper
def add_subparser(subparsers):
    p = subparsers.add_parser('Scan')
    p.add_argument(
        '-w','--wtseq',type=str,default=None,
        help ='Wild Type sequence')
    p.add_argument(
        '-m','--model', help='model to use')
    p.add_argument(
        '-t', '--type', choices=['dna','rna','protein'], default='dna')
    p.add_argument('-mt','--modeltype',default='LinearEmat')
    p.add_argument('-o', '--out', default=None)
    p.set_defaults(func=wrapper)
