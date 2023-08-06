#!/usr/bin/env python

'''A script which returns the mutual information between the predictions of a
    model and a test data set.'''

from __future__ import division
#Our standard Modules
import argparse
import numpy as np
import scipy as sp
import sys
import pandas as pd
#Our miscellaneous functions
#This module will allow us to easily tally the letter counts at a particular position

import sortseq.utils as utils
import sortseq.Models as Models
import sortseq.simulate_evaluate as simulate_evaluate
import sortseq.EstimateMutualInfoforMImax as EstimateMutualInfoforMImax


def main(
        data_df,model_df,dicttype='dna',exptype=None,modeltype='LinearEmat',
        start=0,end=None,no_err=False):
    if (start != 0 or end):
        data_df.loc[:,'seq'] = data_df.loc[:,'seq'].str.slice(start,end)
    col_headers = utils.get_column_headers(data_df)
    if 'ct' not in data_df.columns:
                data_df['ct'] = data_df[col_headers].sum(axis=1)
    data_df = data_df[data_df.ct != 0]        
    if not end:
        seqL = len(data_df['seq'][0]) - start
    else:
        seqL = end-start
    data_df = data_df[data_df.seq.apply(len) == (seqL)]
    #data_df.reset_index(inplace=True,drop=True)    
    
    if modeltype == 'LinearEmat' or modeltype=='Neighbor':
        data_df['val'] = simulate_evaluate.main(
            data_df,[model_df],dicttype,modeltype=modeltype,is_df=True)        
    else:
        raise ValueError('Cannot handle other model types at the moment. Sorry!')
    #go from a dataframe of counts in each bin to one long vector of expression.
    '''long_expression,batch = utils.expand_weights_array(
        data_df['val'],np.array(data_df[col_headers]))
    rankexpression,rankbatch = utils.shuffle_rank(long_expression,batch)'''
    df_sorted = data_df.sort(columns='val')
    df_sorted.reset_index(inplace=True)
    df_sorted[col_headers] = df_sorted[col_headers].div(df_sorted['ct'],axis=0)
    #MI = EstimateMutualInfoforMImax.alternate_calc_MI(rankexpression,rankbatch)
    MI = EstimateMutualInfoforMImax.alt2(df_sorted)
    if no_err:
        Std = np.NaN
    else:
        data_df_for_sub = data_df.copy()
        sub_MI = np.zeros(15)
        for i in range(15):
            sub_df = data_df_for_sub.sample(int(len(data_df_for_sub.index)/2))
            sub_df.reset_index(inplace=True)
            sub_MI[i],sub_std = main(
                sub_df,model_df,dicttype=dicttype,modeltype=modeltype,no_err=True)
        Std = np.std(sub_MI)
    return MI,Std
     
def wrapper(args):
    
    data_df = pd.io.parsers.read_csv(args.dataset,delim_whitespace=True)    	    
    # Take input from standard input or through the -i flag.
    if args.model:
        model_df = pd.io.parsers.read_csv(args.model,delim_whitespace=True)
    else:
        model_df = pd.io.parsers.read_csv(sys.stdin,delim_whitespace=True)
    MI,Std = main(
        data_df,model_df,dicttype=args.type,exptype=args.exptype,start=args.start,
        end=args.end,modeltype=args.modeltype,no_err=args.no_err)
    output_df = pd.DataFrame([MI],columns=['info'])
    output_df = pd.concat([output_df,pd.Series(Std,name='err')],axis=1)
  
    if args.out:
        outloc = open(args.out,'w')
    else:
        outloc = sys.stdout
    pd.set_option('max_colwidth',int(1e8))
    output_df.to_string(
        outloc, index=False,col_space=10,float_format=utils.format_string)

# Connects argparse to wrapper
def add_subparser(subparsers):
    p = subparsers.add_parser('predictiveinfo')
    p.add_argument('-ds','--dataset')
    p.add_argument(
        '-mt','--modeltype',default='LinearEmat',
        choices=['LinearEmat','Neighbor'],help='''Type of model to be evaluated''')
    p.add_argument(
        '-expt','--exptype',default=None,choices=[None,'sortseq','selex',
        'dms','mpra'])
    p.add_argument(
        '-t', '--type', choices=['dna','rna','protein'], default='dna')
    p.add_argument(
        '--no_err',action='store_true',help='''Flag to use if you do not want to
        calculate error''')
    p.add_argument(
        '-s','--start',type=int,default=0,help ='''Position to start your 
        analyzed region''')
    p.add_argument(
        '-e','--end',type=int,default = None, 
        help='''Position to end your analyzed region''')
    p.add_argument(
        '-m', '--model', default=None,help='''Model file, otherwise input
        through the standard input.''')            
    p.add_argument('-o', '--out', default=None)
    p.set_defaults(func=wrapper)
