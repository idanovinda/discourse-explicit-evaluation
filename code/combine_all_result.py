#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 24 11:08:19 2020

@author: ida
"""

import pandas as pd

if __name__ == "__main__":
    methods = ['pdtb', 'conll2015', 'syntactic', 'heuristic']
    dataset = 'spice'
    
    #specify directories of each file
    path = "../result-csv/"
    
    result_dict = {}
    
    for each in methods:
        if ((each == 'conll2015') and (dataset == 'wsj_23' or dataset == 'biodrb')):
            gold = pd.read_csv (path + dataset + "_gold_conll2015.csv")['Offset-raw'].str.lower()
            gold = pd.Series([x.strip() for x in gold]).value_counts()
            pred = pd.read_csv (path + dataset + "_pred_" + each + ".csv")['Offset-raw'].str.lower().value_counts()
        else:
            gold = pd.read_csv (path + dataset + "_gold.csv")['Offset-raw'].str.lower()
            gold = pd.Series([x.strip() for x in gold]).value_counts()
            pred = pd.read_csv (path + dataset + "_pred_" + each + ".csv")['Offset-raw'].str.lower().value_counts()
        tp = pd.read_csv ( path + dataset + "_truepositive_" + each + ".csv" ) ['Offset-raw'].str.lower().value_counts()
#        fp = pd.read_csv ( path + dataset + "_falsepositive_" + each + ".csv" ) ['Offset-raw'].str.lower().value_counts()
#        fn = pd.read_csv ( path + dataset + "_falsenegative_" + each + ".csv" ) ['Offset-raw'].str.lower().value_counts()
        
        for idx in tp.index:
            if idx.strip() not in result_dict:
                result_dict[idx.strip()] = {}
                result_dict[idx.strip()][each + "_TP"] = tp.loc[idx]
            else:
                result_dict[idx.strip()][each + "_TP"] = tp.loc[idx]
                
        for idx in gold.index:
            if idx.strip() not in result_dict:
                result_dict[idx.strip()]={}
                result_dict[idx.strip()][each + "_GS"] = gold.loc[idx]
            else:
                result_dict[idx.strip()][each + "_GS"] = gold.loc[idx]
                
        for idx in pred.index:
            if idx.strip() not in result_dict:
                result_dict[idx.strip()]={}
                result_dict[idx.strip()][each + "_PR"] = pred.loc[idx]
            else:
                result_dict[idx.strip()][each + "_PR"] = pred.loc[idx]
        
#        for idx in tp.index:
#            if idx not in result_dict:
#                result_dict[idx] = {}
#                result_dict[idx][each + "_FP"] = fp.loc[idx]
#            else:
#                result_dict[idx][each + "_FP"] = fp.loc[idx]
#        
#        for idx in fn.index:
#            if idx not in result_dict:
#                result_dict[idx] = {}
#                result_dict[idx][each + "_FN"] = fn.loc[idx]
#            else:
#                result_dict[idx][each + "_FN"] = fn.loc[idx]

    df = pd.DataFrame.from_dict(result_dict, orient='index')
    pr_df = pd.DataFrame()
    for each in methods:
        colname_p = each+'_P'
        colname_r = each+'_R'
        pr_df[colname_p] = df[each+'_TP']/df[each+'_GS']
        pr_df[colname_r] = df[each+'_TP']/df[each+'_PR']
        

    df.fillna(0, inplace=True)
    for each in methods:
        fn = df[each+"_GS"] - df[each+"_TP"]
        fp = df[each+"_PR"] - df[each+"_TP"]
        df[each+"_FN"] = fn
        df[each+"_FP"] = fp
    
    
#    df.fillna('-', inplace=True)
    pr_df.fillna('-', inplace=True)
    pr_df = pr_df.sort_index()
    df = df.sort_index()
    df = df[['pdtb_TP', 'pdtb_FP', 'pdtb_FN',
             'conll2015_TP', 'conll2015_FP', 'conll2015_FN',
             'syntactic_TP', 'syntactic_FP', 'syntactic_FN',
             'heuristic_TP', 'heuristic_FP', 'heuristic_FN']]
    
    df.to_csv("../result-csv/combine/"+dataset+"_combine.csv")
    pr_df.to_csv("../result-csv/combine/"+dataset+"_combine_pr.csv")