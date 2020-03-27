#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 25 12:32:21 2020

@author: ida
"""

import pandas as pd


if __name__ == "__main__":
#    methods = ['pdtb', 'conll2015', 'syntactic', 'heuristic']
    methods = ['syntactic']
    dataset = 'ted'
    
    #specify directories of each file
    path = "../result-csv/"
    
    result_dict = {}
    
    not_detected_dict = {}
    for each in methods:
        
        gold = pd.read_csv (path + dataset + "_gold.csv")['Offset-raw'].str.lower()
        pred = pd.read_csv (path + dataset + "_pred_" + each + ".csv")['Offset-raw'].str.lower()
        tp = pd.read_csv ( path + dataset + "_truepositive_" + each + ".csv" ) ['Offset-raw'].str.lower()
        not_detect = list(set(gold)-set(pred))
        not_detect.sort()
        not_detected_dict[each] = not_detect
    
    not_detected_df = pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in not_detected_dict.items()]))
        