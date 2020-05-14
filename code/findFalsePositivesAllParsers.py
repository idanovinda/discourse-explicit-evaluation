#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 12:36:46 2020

@author: idanovinda
"""


import pandas as pd
import spacy

nlp = spacy.load("en")

def get_fp(csv_dir, dataset_name, parser_name):
    gold = pd.read_csv(csv_dir + dataset_name + "_gold.csv")
    pred = pd.read_csv(csv_dir + dataset_name + "_pred_" + parser_name + ".csv")
    
    gold_list = gold.values.tolist()
    pred['filename'] = pred['filename'].apply(str)
    pred_list = pred.values.tolist()
    
    fp = [value for value in pred_list if value not in gold_list]
    
    return fp

def get_fp_all(csv_dir, dataset_name):
    fp_pdtb = get_fp(csv_dir, dataset_name, "pdtb")
    fp_conll = get_fp(csv_dir, dataset_name, "conll2015")
    fp_heu = get_fp(csv_dir, dataset_name, "heuristic")
    fp_syn = get_fp(csv_dir, dataset_name, "syntactic")
    
    fp_pdtb_conll = [value for value in fp_pdtb if value in fp_conll]
    fp_pdtb_conll_heu = [value for value in fp_pdtb_conll if value in fp_heu]
    fp_all = [value for value in fp_pdtb_conll_heu if value in fp_syn]
    
    return fp_all


def get_fp_without_conll2015(csv_dir, dataset_name):
    fp_pdtb = get_fp(csv_dir, dataset_name, "pdtb")
    fp_conll = get_fp(csv_dir, dataset_name, "conll2015")
    fp_heu = get_fp(csv_dir, dataset_name, "heuristic")
    fp_syn = get_fp(csv_dir, dataset_name, "syntactic")
    
    fp_pdtb_heu = [value for value in fp_pdtb if value in fp_heu]
    fp_all = [value for value in fp_pdtb_heu if value in fp_syn]
    
    return fp_conll, fp_all

def get_raw_text(fp_all, raw_dir, file_ext):
    if len(fp_all) == 0:
        return []
    else:
        fp_all_df = pd.DataFrame(fp_all, columns=['Offset-raw', 'filename', 'ConnSpanList'])
        ConnSpanList_start = []
        ConnSpanList_end = []
        for i in fp_all_df.index:
            ConnSpanList_split = fp_all_df.loc[i, 'ConnSpanList'].split("..")
            ConnSpanList_start.append(ConnSpanList_split[0])
            ConnSpanList_end.append(ConnSpanList_split[1])
        
        fp_all_df["ConnSpanListStart"] = ConnSpanList_start
        fp_all_df["ConnSpanListEnd"] = ConnSpanList_end
        fp_all_df = fp_all_df.sort_values(['filename', 'ConnSpanListStart']).reset_index()
        
        raw_results = []
        
        curr_file = fp_all_df.loc[0, 'filename']
        curr_file_raw = open(raw_dir + str(curr_file) + file_ext, "r").read()
        doc = nlp(curr_file_raw)
        for i in fp_all_df.index:
            if fp_all_df.loc[i, 'filename'] != curr_file:
                curr_file = fp_all_df.loc[i, 'filename']
                curr_file_raw = open(raw_dir + str(curr_file) + file_ext, "r", encoding="utf-8", errors="ignore").read()
                doc = nlp(curr_file_raw)
            for sent in doc.sents:
                if sent.start_char <= int(fp_all_df.loc[i, 'ConnSpanListStart']) and sent.end_char >= int(fp_all_df.loc[i, 'ConnSpanListEnd']):
                    raw_results.append([fp_all_df.loc[i, 'Offset-raw'], 
                                        fp_all_df.loc[i, 'ConnSpanList'],
                                        str(sent.start_char) + ".." + str(sent.end_char),
                                        sent.text])
                    break
        
        raw_results_df = pd.DataFrame(raw_results, columns=['Offset-raw', 'ConnSpanList', 'RawTextSpan', 'RawText'])
        
        return raw_results_df


if __name__ == "__main__":
    dataset_name = "ted"
    csv_dir = "../result-csv/"
    raw_dir = "../data/Ted-Talk/raw/"
    file_ext = ".txt"
    
    fp_all = get_fp_all(csv_dir, dataset_name)
    raw_results = get_raw_text(fp_all, raw_dir, file_ext)
    
    fp_biodrb = get_fp_all(csv_dir, "biodrb")
    raw_biodrb = get_raw_text(fp_biodrb, "../data/BioDRB/Genia Raw/", ".txt")
    
    fp_wsj = get_fp_all(csv_dir, "wsj_23")
    raw_wsj = get_raw_text(fp_wsj, "../data/wsj_23/raw/", "")
    
    fp_conll, fp_biodrb_without_conll = get_fp_without_conll2015(csv_dir, "biodrb")
    raw_biodrb_without_conll = get_raw_text(fp_biodrb_without_conll, "../data/BioDRB/Genia Raw/", ".txt")
    
#%%
    # gold = pd.read_csv("../result-csv/biodrb_gold.csv")
    # pred_conll = pd.read_csv("../result-csv/biodrb_pred_conll2015.csv")
    # new_filename = []
    # for i in pred_conll.index:
    #     new_filename.append(pred_conll.loc[i, 'filename'].split(".")[0])
    # pred_conll['filename'] = new_filename
    