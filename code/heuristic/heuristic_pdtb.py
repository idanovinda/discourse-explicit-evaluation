#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 17 09:35:56 2020

@author: ida
"""

import pandas as pd
import re
import os
import spacy
import numpy as np
from string import punctuation


def calculate_precision_recall_f1(true_label_df, predict_label_df):
    
    
    true_label_df['Offset-raw'] = true_label_df['Offset-raw'].str.lower()
    true_label_df['filename'] = true_label_df['filename'].apply(str)
    
    true_label_list = true_label_df.values.tolist()
    
    predict_label_df['Offset-raw'] = predict_label_df['Offset-raw'].str.lower()    
    predict_label_list = predict_label_df.values.tolist()
    
    intersection = [value for value in predict_label_list if value in true_label_list]
    
    if len(predict_label_df) != 0:
        precision = (len(intersection)/len(predict_label_df))
        recall = (len(intersection)/len(true_label_df))
        f1 = (2*precision*recall)/(precision+recall)
        print('True Positive\t: ', str(len(intersection)))
        print('False Positive\t: ', str(len(predict_label_df) - len(intersection)))
        print('False Negative\t: ', str(len(true_label_df) - len(intersection)))
        print('Precision\t: ' + str(precision))
        print('Recall\t\t: ' + str(recall))
        print('F1-score\t: ' + str(f1))
        
    tpdf = pd.DataFrame(intersection, columns=['Offset-raw', 'filename', 'ConnSpanList'])
    return tpdf
    

def run_heuristic_pdtb(path):
    
    connective_path = '../../data/pdtb-annotation-manual.csv'
    
    nlp = spacy.load("en")
    
    connective_list = pd.read_csv(connective_path)['connective'].values.tolist()
    
    
    pred_conn = []
    for file in os.listdir(path):
        try:
            f = open(path+file, "r").read()
        except:
            f = open(path+file, 'r', encoding="utf-8", errors="replace").read()
        doc = nlp(f)
        filename = file.split(".")[0]
#        print(filename)
        found = False
        for sent in doc.sents:
#            print(sent)
            for conn in connective_list:
                conn_list = conn.split(';')
                if len(conn_list) == 1:
                    word_list = conn_list[0].split(" ")
                    if len(word_list) == 1:
                        for word in sent:
                            if word.text.lower()==conn_list[0]:
                                pred_conn.append([word.text.lower(), filename, str(word.idx)+".."+str(word.idx+len(word.text))])
                    else:
                        sent_split = sent.text.lower().split(conn_list[0])
                        cur_len = 0
                        for i in range(len(sent_split)-1):
                            cur_len += len(sent_split[i])
                            pred_conn.append([conn_list[0], filename, str(doc[sent.start].idx+cur_len)+".."+str(doc[sent.start].idx+cur_len+len(conn_list[0]))])
                            cur_len += len(conn_list[0])
                else:
                    sent_words = [x.text.lower() for x in sent]
#                    print(sent_words)
                    intersection = list(set(sent_words).intersection(set(conn_list)))
                    if len(intersection) == 2:
#                        print(intersection)
                        first_part_idx = len(sent.text.lower().split(conn_list[0]+" ")[0])
                        second_part_idx = len(sent.text.lower().split(conn_list[1]+" ")[0])
                        if first_part_idx < second_part_idx:
                            pred_conn.append([conn, filename, str(doc[sent.start].idx+first_part_idx)+".."+str(doc[sent.start].idx+first_part_idx+len(intersection[0]))+
                                              ";"+str(doc[sent.start].idx+second_part_idx)+".."+str(doc[sent.start].idx+second_part_idx+len(intersection[1]))])
                        else:
                            pred_conn.append([conn, filename, str(doc[sent.start].idx+second_part_idx)+".."+str(doc[sent.start].idx+second_part_idx+len(intersection[1]))+
                                              ";"+str(doc[sent.start].idx+first_part_idx)+".."+str(doc[sent.start].idx+first_part_idx+len(intersection[0]))])
                        found = True
#                        break
#                if found:
#                    break
#            if found:
#                break
    pred_df = pd.DataFrame(pred_conn, columns = ['Offset-raw', 'filename', 'ConnSpanList'])
    
    return pred_df
#%%
def extract_spice_pred(pred_df):
    nlp = spacy.load("en")
    raw_path = "../../data/SPICE/raw/"
    
    all_pred = pd.DataFrame()
    for each_file in pred_df['filename'].unique():
#        print(each_file)
        raw_file_path = raw_path + each_file + '.txt'
        pred_file = pred_df[pred_df['filename']==each_file]
        pred_file['start'] = [int(pred_file.loc[x, 'ConnSpanList'].split("..")[0]) for x in pred_file.index]
        pred_file = pred_file.sort_values(['start']).reset_index()
        try:
            f_string = open(raw_file_path, 'r').read()
        except:
            f_string = open(raw_file_path, 'r', encoding="utf-8", errors="replace").read()
        doc = nlp(f_string.strip())
        
        docs = [sent for sent in doc.sents]
        results = []
        doc_pivot = 0
        pred_pivot = 0
        while pred_pivot != len(pred_file):
            if (len(doc[:docs[doc_pivot].end].text) > pred_file.loc[pred_pivot]['start']):
                results.append(docs[doc_pivot].text)
                pred_pivot += 1
            else:
                doc_pivot += 1
        pred_file['fullSent'] = results
        all_pred = all_pred.append(pred_file, ignore_index=True)
    return all_pred

def evaluate_spice(gold_df, pred_conn):

    print('Evaluating result...')
    pred_conn = extract_spice_pred(pred_conn)
    
    pred_dict = {}
    for i in range(len(pred_conn)):
        filename = pred_conn.loc[i]["filename"]
        conn = pred_conn.loc[i]["Offset-raw"].lower().strip()
        fullSent = pred_conn.loc[i]["fullSent"].lower().strip(punctuation).strip()
        if filename not in pred_dict:
            pred_dict[filename] = {}
            pred_dict[filename][conn] = [fullSent]
        elif conn not in pred_dict[filename]:
            pred_dict[filename][conn] = [fullSent]
        else:
            pred_dict[filename][conn].append(fullSent)

    #create dictionary from the gold:
    gold_dict = {}
    for i in gold_df.index:
        filename = gold_df.loc[i]['filename']
        conn = gold_df.loc[i]['Offset-raw'].lower().strip()
        fullSent = gold_df.loc[i]['fullSent'].lower().strip(punctuation).strip()
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
                            if (pred_sent in gold_sent or pred_sent in gold_sent):
                                match_connective.append([filename, conn, pred_sent])
                                found = True
                                break
                if found == False:
                    not_found.append(conn)
                i+=1
#                if i%100 == 0:
#                    print(i)               
    
    prec = len(match_connective)/len(pred_conn)
    rec = len(match_connective)/len(gold_df)
    print("precision\t: ", prec)
    print("recall\t: " , rec)
    print("f1-score\t: ", 2*prec*rec/(prec+rec))
    
    tpdf = pd.DataFrame(match_connective, columns=['filename', 'Offset-raw', 'fullSent'])
    
    return gold_df, tpdf, pred_conn

#%%
def get_false_negatif_connective(pred, gold):
    pred_list = pred['Offset-raw'].apply(str).str.lower().values.tolist()
    gold_list = gold['Offset-raw'].apply(str).str.lower().values.tolist()
    
    diff = list(set(gold_list) - set(pred_list))
    
    return diff
    

#%%
if __name__ == "__main__":
    biopath = "../../data/BioDRB/Genia Raw/"
    tedpath = "../../data/Ted-Talk/raw/"
    wsjpath = "../../data/wsj_23/raw/"

#    print("Evaluate biodrb...")
#    pred_bio = run_heuristic_pdtb(biopath)
#    gold_bio = pd.read_csv("../../result-csv/biodrb_gold.csv")
#    tp_bio = calculate_precision_recall_f1(gold_bio, pred_bio)
#    
#    print("Evaluate ted...")
#    pred_ted = run_heuristic_pdtb(tedpath) 
#    gold_ted = pd.read_csv("../../result-csv/ted_gold.csv")
#    tp_ted = calculate_precision_recall_f1(gold_ted, pred_ted)
#    
#    print("Evaluate wsj...")
#    pred_wsj = run_heuristic_pdtb(wsjpath)
#    gold_wsj = pd.read_csv("../../../Result_v2/wsj_23_gold.csv")
#    tp_wsj = calculate_precision_recall_f1(gold_wsj, pred_wsj)
#%%
    print("Evaluate spice...")
    spicepath = "../../data/SPICE/raw/"
    pred_spice = run_heuristic_pdtb(spicepath)
    gold_spice = pd.read_csv("../../result-csv/spice_gold.csv")
    gold, tp_spice, pred = evaluate_spice(gold_spice, pred_spice)