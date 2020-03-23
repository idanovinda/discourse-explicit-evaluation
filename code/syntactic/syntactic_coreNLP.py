#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 14 15:19:16 2020

@author: ida
"""

import pandas as pd
import json
import spacy
import re
import os
from string import punctuation

#give the pattern of each explicit word
en_dependency_patterns = {
  # S2 ~ S2 head (full S head) ---> connective
  "after": [
    {"S1": "advcl", "S2": "mark", "POS": "IN"},
    {"S1": "acl", "S2": "mark", "POS": "IN"},
  ],
  "also": [
    {"S1": "advcl", "S2": "advmod", "POS": "RB"},
  ],
  "although": [
    {"S1": "advcl", "S2": "mark", "POS": "IN"},
  ],
  "and": [
    {"S1": "conj", "S2": "cc", "POS": "CC", "flip": True},
  ],
  "as": [
    {"S1": "advcl", "S2": "mark", "POS": "IN"},
  ],
  "before": [
    {"S1": "advcl", "S2": "mark", "POS": "IN"},
  ],
  "but": [
    {"S1": "conj", "S2": "cc", "POS": "CC", "flip": True},
  ],
  "so": [
    # {"S1": "parataxis", "S2": "dep", "POS": "IN", "flip": True},
    {"S1": "advcl", "S2": "mark", "POS": "IN"},
    {"S1": "advcl", "S2": "mark", "POS": "RB"},
  ],
  "still": [
    {"S1": "parataxis", "S2": "advmod", "POS": "RB", "acceptable_order": "S1 S2"},
    {"S1": "dep", "S2": "advmod", "POS": "RB", "acceptable_order": "S1 S2"},
  ],
  "though": [
    {"S1": "advcl", "S2": "mark", "POS": "IN"},
  ],
  "because": [
    {"S1": "advcl", "S2": "mark", "POS": "IN"},
  ],
  "however": [
    {"S1": "parataxis", "S2": "advmod", "POS": "RB"},
    # {"S1": "ccomp", "S2": "advmod", "POS": "RB"}, ## rejecting in favor of high precision
  ],
  "if": [
    {"S1": "advcl", "S2": "mark", "POS": "IN"},
  ],
  "meanwhile": [
    {"S1": "parataxis", "S2": "advmod", "POS": "RB"},
  ],
  "while": [
    {"S1": "advcl", "S2": "mark", "POS": "IN"},
  ],
  "for example": [
    {"S1": "parataxis", "S2": "nmod", "POS": "NN", "head": "example"},
  ],
  "then": [
    {"S1": "parataxis", "S2": "advmod", "POS": "RB", "acceptable_order": "S1 S2"},
  ],
  "when": [
    {"S1": "advcl", "S2": "advmod", "POS": "WRB"},
  ],
}


def extract_pattern(dependency_patterns):
    patterns = []
    conn = []
    for each_conj in dependency_patterns:
        for each_pattern in dependency_patterns[each_conj]:
#            try:
#                if each_pattern['flip']:
#                    patterns.append([each_conj, each_pattern['S1'], each_pattern['S2'], each_pattern['POS']])
#                    conn.append(each_conj)
#            except:
            patterns.append([each_conj, each_pattern['S2'], each_pattern['S1'], each_pattern['POS']])
            conn.append(each_conj)
    return patterns, conn

def run_syntactic(filepath):
    patterns, conn = extract_pattern(en_dependency_patterns)
    conn.append('for')
    
    pred_df = pd.DataFrame(columns=['Offset-raw', 'filename', 'ConnSpanList'])
    all_connectives = []
    for filename in os.listdir(filepath):
#        print(filename)
#        all_connectives = []
        json_path = filepath + filename + '/pdtb-parses.json'
        with open(json_path) as f:
            f_input = json.load(f)
        for sent in f_input[filename]['sentences']:
            temp_dict = {}
            for word in sent['dependencies']:
                temp_dict[word[2]] = {'dep':word[0], 'head':word[1], 'pos':sent['words'][int(word[2].split("-")[-1])-1][1]['PartOfSpeech'], 
                                     'begin': sent['words'][int(word[2].split("-")[-1])-1][1]['CharacterOffsetBegin'], 
                                     'end': sent['words'][int(word[2].split("-")[-1])-1][1]['CharacterOffsetEnd']}
            
            for word in temp_dict:
                norm_word = ' '.join(word.split('-')[:-1]).lower()
                if norm_word in conn:  
                    if temp_dict[word]['head'] != 'ROOT-0':
                        pattern = []
                        if norm_word == 'for':
                            if temp_dict[word]['head'] == 'example':
                                pattern = ['for example', temp_dict[word]['dep'], temp_dict[temp_dict[word]['head']]['dep'], temp_dict[word]['pos']]
                                if pattern not in all_connectives:
                                    all_connectives.append(pattern)
                        else:
                            pattern = [norm_word, temp_dict[word]['dep'], temp_dict[temp_dict[word]['head']]['dep'], temp_dict[word]['pos']]
                            if pattern not in all_connectives:
                                all_connectives.append(pattern)
                        if pattern in patterns:
                            word_span = str(temp_dict[word]['begin']) + '..' + str(temp_dict[word]['end'])
                            pred_df = pred_df.append({'Offset-raw':norm_word, 
                                                      'filename':filename, 
                                                      'ConnSpanList': word_span}, ignore_index=True)
                    else:
                        pattern = [norm_word, temp_dict[word]['dep'], 'root', temp_dict[word]['pos']]
                        if pattern not in all_connectives:
                            all_connectives.append(pattern)
    pd_all_connectives = pd.DataFrame(all_connectives, columns = ['conn', 'dep-1', 'dep-2', 'POS']).sort_values(by=['conn'])
    print('Finish the extraction')
    return pred_df, pd_all_connectives
#%%
def evaluate(gold_df, pred_df):
    print('Evaluating result...')
    ##choose pred that the connective are covered by the syntactic parser only 
    slicing_gold_idx = []
    for i in gold_df.index:
        if gold_df.loc[i]['Offset-raw'] in en_dependency_patterns.keys():
            slicing_gold_idx.append(i)
    
    pred = pred_df.values.tolist()
    new_gold = gold_df.loc[slicing_gold_idx]
    gold = new_gold.values.tolist()
    tp = [value for value in gold if value in pred]
    fn = [value for value in gold if value not in pred]
    fp = [value for value in pred if value not in gold]
    
    prec = len(tp)/len(pred)
    rec = len(tp)/len(gold)
    print('Precision\t: ', prec)
    print('Recall\t\t: ', rec)
    print('F1 score \t: ', 2*prec*rec/(prec+rec))
    
    tpdf = pd.DataFrame(tp, columns=['Offset-raw', 'filename', 'ConnSpanList'])
    
    return new_gold, tpdf

def evaluate_spice(gold_df, pred_conn):
    print('Evaluating result...')
    
    #choose pred that the connective are covered by the syntactic parser only 
    slicing_gold_idx = []
    for i in gold_df.index:
        if gold_df.loc[i]['conn'] in en_dependency_patterns.keys():
            slicing_gold_idx.append(i)
    
    gold_df = gold_df.loc[slicing_gold_idx]
    
    pred_dict = {}
    for i in range(len(pred_conn)):
        filename = pred_conn.loc[i]["filename"]
        conn = pred_conn.loc[i]["conn"]
        arg1 = str(pred_conn.loc[i]["arg1"]).strip(punctuation).strip()
        arg2 = str(pred_conn.loc[i]['arg2']).strip(punctuation).strip()
        if filename not in pred_dict:
            pred_dict[filename] = {}
            pred_dict[filename][conn] = [{'arg1': arg1, 'arg2': arg2}]
        elif conn not in pred_dict[filename]:
            pred_dict[filename][conn] = [{'arg1': arg1, 'arg2': arg2}]
        else:
            pred_dict[filename][conn].append({'arg1': arg1, 'arg2': arg2})

    #create dictionary from the gold:
    gold_dict = {}
    for i in range(len(gold_df)):
        filename = gold_df.loc[i]['filename']
        conn = gold_df.loc[i]['conn'].lower().strip()
        fullSent = gold_df.loc[i]['fullSent']
        if filename not in gold_dict:
            gold_dict[filename] = {}
            gold_dict[filename][conn] = [fullSent]
        elif conn not in gold_dict[filename]:
            gold_dict[filename][conn] = [fullSent]
        else:
            gold_dict[filename][conn].append(fullSent)

    match_connective = []
    i = 0
    not_found = []
    for filename in gold_dict: 
        for conn in gold_dict[filename]:
            for gold_sent in gold_dict[filename][conn]:
                found = False
                if filename in pred_dict:
                    if conn in pred_dict[filename]:
                        for pred_sent in pred_dict[filename][conn]:
                            arg1 = pred_sent["arg1"]
                            arg2 = pred_sent["arg2"]
                            if (arg1 in gold_sent or arg2 in gold_sent):
                                match_connective.append([filename, conn, arg1, arg2])
                                found = True
                                break
                if found == False:
                    not_found.append(conn)
                i+=1
                if i%100 == 0:
                    print(i)               
    
    return gold_df, match_connective
    
#%%
if __name__ == "__main__":
    
    patterns, conns = extract_pattern(en_dependency_patterns)
    
#    
#    ted_filepath = '/home/ida/Documents/Saarland/ResearchImmersion/a_conll2015/TED-data/'
#    biodrb_filepath = 'new_biodrb_conll2015/'
#    wsj_filepath = 'wsj_23_conll2015/conll2015/'
#    
#    ted_gold = pd.read_csv('../Result_v2/ted_gold.csv')
#    ted_gold['Offset-raw'] = ted_gold['Offset-raw'].str.lower()
#    
#    wsj_gold = pd.read_csv('../Result/wsj_23_gold.csv')
#    wsj_gold['Offset-raw'] = wsj_gold['Offset-raw'].str.lower()
#    
#    biodrb_gold = pd.read_csv('../Result_v2/biodrb_gold.csv')
#    biodrb_gold['Offset-raw'] = biodrb_gold['Offset-raw'].str.lower()
#    biodrb_gold['filename'] = biodrb_gold['filename'].apply(str)
#    
#    
#    pred_ted, conn_ted = run_syntactic(ted_filepath)
#    pred_biodrb, conn_biodrb = run_syntactic(biodrb_filepath)
#    pred_wsj, conn_wsj = run_syntactic(wsj_filepath)
#
#    
#    new_gold_ted, tp_ted = evaluate(ted_gold, pred_ted)
#    new_gold_wsj, tp_wsj = evaluate(wsj_gold, pred_wsj)
#    new_gold_biodrb, tp_biodrb = evaluate(biodrb_gold, pred_biodrb)
    
#%%%
    #extract connective from SPICE
    spice_filepath = 'new_spice_output/conll2015/'
    pred_spice, conn_spice = run_syntactic(spice_filepath)
    spice_gold = pd.read_csv("../Result_v2/spice_gold.csv")
    #%%
    new_gold_spice, tp_spice = evaluate_spice(spice_gold, pred_spice)