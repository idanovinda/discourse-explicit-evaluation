#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 11 13:33:45 2019

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
    for each_conj in dependency_patterns:
        for each_pattern in dependency_patterns[each_conj]:
            try:
                if each_pattern['flip']:
                    patterns.append([each_conj, each_pattern['S1'], each_pattern['S2'], each_pattern['POS']])
            except:
                patterns.append([each_conj, each_pattern['S2'], each_pattern['S1'], each_pattern['POS']])
    return patterns

def calculate_precision_reacall_f1(true_label_df, predict_label_df):
    true_label_list = true_label_df.values.tolist()
    predict_label_list = predict_label_df.values.tolist()
    
    intersection = [value for value in predict_label_list if value in true_label_list]
    
    precision = (len(intersection)/len(predict_label_df))
    recall = (len(intersection)/len(true_label_df))
    f1 = (2*precision*recall)/(precision+recall)
    print('True positive\t: ' + str(len(intersection)))
    print('False positive\t: ' + str(len(predict_label_df) - len(intersection)))
    print('False negative\t: ' + str(len(true_label_df) - len(intersection)))
    print('Precision\t: ' + str(precision))
    print('Recall\t\t: ' + str(recall))
    print('F1-score\t: ' + str(f1))
    
    return intersection        
    
def find_pattern_ted(filepath, file):
    nlp = spacy.load("en")
    f_string = open(filepath, 'r', encoding="ascii", errors="backslashreplace").read()
    match_pattern = []
    all_conj = []
    patterns = extract_pattern(en_dependency_patterns)
    doc = nlp(f_string)
    match_words = []
    for word in doc:
        if word.text.lower() in en_dependency_patterns:
            match_words.append([word.text, word.dep_, word.head.dep_, word.tag_, word.idx])
            all_conj.append([word.text, word.dep_, word.head.dep_, word.tag_, word.idx])
    
    for pattern in match_words:
        to_match = [pattern[0].lower(), pattern[1], pattern[2], pattern[3]]
        if to_match in patterns:
            offset = str(pattern[4]) + ".." + str(pattern[4] + len(pattern[0]))
            match_pattern.append([pattern[0], file, offset])
    
    return match_pattern

def find_pattern_biodrb(filepath):
    nlp = spacy.load("en")
    f_string = open(filepath, 'r').read()
    all_conj = []
    patterns = extract_pattern(en_dependency_patterns)
    match_sents = []
    doc = nlp(f_string)
#    match_words = []
    for sent in doc.sents:
#        print(sent)
        for word in sent:
            if word.text.lower() in en_dependency_patterns:
                pattern = [word.text.lower(), word.dep_, word.head.dep_, word.tag_]
                if pattern in patterns:
                    match_sents.append([word.text, str(sent)])
            all_conj.append([word.text, word.dep_, word.head.dep_, word.tag_, word.i])
    
#    for pattern in match_sents:
#        to_match = [pattern[0].lower(), pattern[1], pattern[2], pattern[3]]
#        if to_match in patterns:
#            print(to_match)
#            prev_words = str(doc[pattern[4]-2]) + ' ' + str(doc[pattern[4]-1])
#            next_words = str(doc[pattern[4]+1]) + ' ' + str(doc[pattern[4]+2])
#            match_pattern.append([pattern[0], file, prev_words, next_words])
#    
    return match_sents, all_conj

def evaluate_explicit_ted():
    filenames = ['talk_1927_en', 'talk_1971_en', 'talk_1976_en', 'talk_1978_en', 'talk_2009_en', 'talk_2150_en_inter', 'talk_2150_en_intra']

    match_pattern_all = []
    for filename in filenames:
        filepath = '/home/ida/Documents/Saarland/ResearchImmersion/a_conll2016/TED-data/' + filename + '/raw/'+ filename + '.txt'
        
        file = re.sub("_", "-", filename) + ".txt"
        print(file)
        match_pattern_all.extend(find_pattern_ted(filepath, file))
    #open the gold dataset 
    gold_path = '/home/ida/Documents/Saarland/ResearchImmersion/Result/ted_gold.csv'
    gold_df = pd.read_csv(gold_path)
    match_df = pd.DataFrame(match_pattern_all, columns=['Offset-raw', 'filename', 'ConnSpanList'])
    intersection = calculate_precision_reacall_f1(gold_df, match_df)
    
    return match_df, intersection, gold_df

def evaluate_explicit_biodrb():
    biodrb_filepath = '/home/ida/Documents/Saarland/ResearchImmersion/Preprocessing/clean_biodrb.txt'
#    f_gold = pd.read_csv('/home/ida/Documents/Saarland/ResearchImmersion/Data/BioDRB_explicit.txt', sep="|", header=None)
     #find all .txt extension:
    i = 0
    match_all_pattern = []
    
    match_pattern, all_conj = find_pattern_biodrb(biodrb_filepath)
#    all_conj_all = []
#    for file in os.listdir(biodrb_filepath):
#        if file.endswith(".txt"):
#            i+=1
#            print(i)
#            filepath = os.path.join(biodrb_filepath, file)
#            
#            match_pattern, all_conj = find_pattern_biodrb(filepath, file)
#            match_all_pattern.extend(match_pattern)
#            all_conj_all.extend(all_conj)
#            
    return match_pattern

 
def run_spice():
    path = "new_spice_output/"
    fileext = ".txt"
    
    gold_path = pd.read_csv('new_spice_output/spice_gold.csv')
    all_gold = list(set([x.lower().strip() for x in list(gold_path['conn'].unique())]))
    
    nlp = spacy.load("en")
    patterns = extract_pattern(en_dependency_patterns)
    pred_conn = []
    i = 1
    pred_conn = []
    for file in os.listdir(path):
        if file.endswith(fileext):
            print(os.path.join(path, file).split("/")[-1])
            f = open(os.path.join(path, file), 'r').read()
            filename = os.path.join(path, file).split("/")[1][:-4]
            
            doc = nlp(f)
            match_conn = []
            for sent in doc.sents:
                for word in sent:
                    if word.text.lower() in en_dependency_patterns:
                        to_match = [word.text.lower(), word.dep_, word.head.dep_, word.tag_]
                        print(to_match)
                        if to_match in patterns:
                            pred_conn.append([filename, word.text.lower(), str(sent).strip(punctuation).strip()])
        
    #evaluate the result on gold 
    
    #create dictionary from the result 
    pred_dict = {}
    for i in range(len(pred_conn)):
        filename = pred_conn[i][0]
        conn = pred_conn[i][1]
        fullSent = pred_conn[i][2]
        if filename not in pred_dict:
            pred_dict[filename] = {}
            pred_dict[filename][conn] = [fullSent.strip(punctuation).strip()]
        elif conn not in pred_dict[filename]:
            pred_dict[filename][conn] = [fullSent.strip(punctuation).strip()]
        else:
            pred_dict[filename][conn].append(fullSent.strip(punctuation).strip())

    #create dictionary from the gold:
    gold_dict = {}
    for i in range(len(gold_path)):
        filename = gold_path.loc[i]['filename']
        conn = gold_path.loc[i]['conn'].lower().strip()
        fullSent = gold_path.loc[i]['fullSent']
        if filename not in gold_dict:
            gold_dict[filename] = {}
            gold_dict[filename][conn] = [fullSent]
        elif conn not in gold_dict[filename]:
            gold_dict[filename][conn] = [fullSent]
        else:
            gold_dict[filename][conn].append(fullSent)
            
    match = 0
    i = 0
    match_conn = []
    for filename in gold_dict: 
        for conn in gold_dict[filename]:
            for gold_sent in gold_dict[filename][conn]:
                if conn in pred_dict[filename]:
                    for pred_sent in pred_dict[filename][conn]:
                        if pred_sent.split(". ")[-1] in gold_sent:
                            match += 1
                            match_conn.append(conn)
                            break
                i+=1
                print(i)
    return pred_conn, match_conn

def evaluate_wsj():
    path = "../23_raw/"
    match_pattern_all = []
    for file in os.listdir(path):       
        filename = os.path.join(path, file).split("/")[-1]
        print(filename)
        match_pattern_all.extend(find_pattern_ted(path+file, filename))
    #open the gold dataset 

    gold_path = '../Result/wsj_23_gold.csv'
    gold_df = pd.read_csv(gold_path)
    match_df = pd.DataFrame(match_pattern_all, columns=['Offset-raw', 'filename', 'ConnSpanList'])
    intersection = calculate_precision_reacall_f1(gold_df, match_df)
    
    return gold_df, match_df, intersection

def evaluate_biodrb():
   
   #open the bio gold 
    f_gold = pd.read_csv('/home/ida/Documents/Saarland/ResearchImmersion/Data/BioDRB_explicit.txt', sep="|", header=None)
    #pre processing gold 
    match_explicit = evaluate_explicit_biodrb()
    #take the last 2 word and 

    outdf = pd.DataFrame(columns=['Conn', 'Sentence', 'Arg1', 'Arg2'])
    for each in match_explicit:
        pred_sent = each[1].lower()
        pred_first = pred_sent.split(each[0].lower())[0].strip(punctuation).strip()
        pred_second = pred_sent.split(each[0].lower())[1].strip(punctuation).strip()
        outdf = outdf.append({'Conn': each[0].lower(), 'Sentence': pred_sent, 'Arg1': pred_first, 'Arg2': pred_second}, ignore_index=True)
        
# Lowering the gold dataset 
    for i in range(len(f_gold)):
        f_gold.loc[i][1] = f_gold.loc[i][1].lower()

    #exact match
    unique_connective = list(outdf['Conn'].unique())
    tuples = []
    not_found = []
    k = 1
    for each in unique_connective:
        pred_idx = list(outdf.loc[outdf['Conn']==each].index)
        gold_idx = list(f_gold.loc[f_gold[1]==each].index)
  
        for j in gold_idx:
            found = False
            gold_first = f_gold.loc[j][4].lower().strip(punctuation).strip()
            gold_second = f_gold.loc[j][5].lower().strip(punctuation).strip()
            for i in pred_idx:
                pred_sent = outdf.loc[i]['Sentence']
                pred_first = outdf.loc[i]['Arg1'] 
                pred_second = outdf.loc[i]['Arg2']
                if (gold_first in pred_sent or gold_second in pred_sent or pred_second in gold_second or (pred_first!= "" and pred_first in gold_first)):
                    tuples.append([i, j])
                    print(">>>", i, k)
                    found = True
                    break
            if found== False:
                not_found.append(j)
            k+=1
            

                