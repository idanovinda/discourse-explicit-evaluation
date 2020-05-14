#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 15 00:49:24 2020

@author: idanovinda
"""

import pandas as pd

if __name__ == "__main__":
    connective = "as"
    dataset = "ted"
    raw_dir = "../data/Ted-Talk/raw/"
    
    gold = pd.read_csv("../result-csv/"+dataset+"_gold.csv")
    pred_conll = pd.read_csv("../result-csv/"+dataset+"_pred_conll2015.csv")
    
    gold_connective = gold[gold["Offset-raw"]==connective]
    pred_conll_connective = pred_conll[pred_conll["Offset-raw"]==connective]
    
    gold_pred = gold_connective.append(pred_conll_connective, ignore_index=True)