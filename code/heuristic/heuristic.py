#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 29 10:21:35 2019

@author: ida
"""

import pandas as pd
import re
import os
import spacy
import numpy as np
from string import punctuation

def calculate_precision_recall_f1(true_label_df, predict_label_df):
    
    for i in range(len(true_label_df)):
        true_label_df.loc[i]['Offset-raw'] = true_label_df.loc[i]['Offset-raw'].lower()
    
    true_label_list = true_label_df[['Offset-raw', 'filename', 'ConnSpanList']].values.tolist()
        
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
        
        return true_label_list, predict_label_list, intersection
    
def evaluate_ted():
    gold_path = "../Result/ted_gold.csv"
    path = "../Data/TED-data/"
    file_ext = ".txt"
    
    #open the gold label
    gold_label = pd.read_csv(gold_path)
    gold_conn_single_words = []
    gold_conn_multi_words = []
    for i in range(len(gold_label)):
        conn = gold_label.loc[i]['Offset-raw'].lower()
        if ((len(conn.split(" ")) == 1) & (conn not in gold_conn_single_words)):
            gold_conn_single_words.append(conn)
        elif ((len(conn.split(" "))> 1)&(conn not in gold_conn_multi_words)):
            gold_conn_multi_words.append(conn)

    nlp = spacy.load("en")
    outdf = pd.DataFrame(columns=['Offset-raw', 'filename', 'ConnSpanList'])
    for file in os.listdir(path):
        if file.endswith(".txt"):
            filename = os.path.join(path, file).split("/")[-1].replace("_", "-")
            print(filename)
            each_f = open(os.path.join(path, file), 'r').read()
            doc = nlp(each_f)
            for word in doc:
                if word.text.lower() in gold_conn_single_words:
                    outdf = outdf.append({'Offset-raw':word.text.lower(), 'filename': filename, 'ConnSpanList':str(word.idx)+".."+str(word.idx+len(word.text))}, ignore_index=True)
            for sent in doc.sents:
                for conn in gold_conn_multi_words:
                    if conn in str(sent).lower():
#                        print(conn, str(sent))
                        conn_tokens = [x.text for x in nlp(conn)]
                        for word in sent:
                            if (word.text.lower() == conn_tokens[0]):
#                                print('pernah kesini ga?')
                                outdf = outdf.append({'Offset-raw':conn, 'filename': filename, 'ConnSpanList':str(word.idx)+".."+str(word.idx+len(conn))}, ignore_index=True)
                                
                    
    true_label, predict_label, intersection = calculate_precision_recall_f1(gold_label, outdf)       
    not_detect = [value for value in true_label if value not in predict_label]
    false_detect = [value for value in predict_label if value not in true_label]
    
    return true_label, predict_label, intersection, not_detect, false_detect
    
def evaluate_spice():
    path = "new_spice_output/"
    fileext = ".txt"
    
    gold_path = pd.read_csv('new_spice_output/spice_gold.csv')
    all_gold = list(set([x.lower().strip() for x in list(gold_path['conn'].unique())]))
    
    nlp = spacy.load("en")
    
    
    pred_conn = []
    for file in os.listdir(path):
        if file.endswith(fileext):
            print(os.path.join(path, file).split("/")[-1])
            f = open(os.path.join(path, file), 'r').read()
            filename = os.path.join(path, file).split("/")[1][:-4]
            
            doc = nlp(f)
            
            for sent in doc.sents:
                for word in sent:
                    if word.text.lower().strip() in all_gold:
                        pred_conn.append([filename, word.text.lower().strip(), str(sent)])

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
    match_conn = []
    i = 0
    not_found = []
    for filename in gold_dict: 
        for conn in gold_dict[filename]:
            for gold_sent in gold_dict[filename][conn]:
                found = False
                for pred_sent in pred_dict[filename][conn]:
                    if pred_sent.split(". ")[-1] in gold_sent:
                        match += 1
                        found = True
                        match_conn.append(conn)
                        break
                if found == False:
                    not_found.append(conn)
                i+=1
                if i%100 == 0:
                    print(i)
                    
    return pred_conn, match_conn, not_found, all_gold

def evaluate_wsj():
    gold_path = "../Result/wsj_23_gold.csv"
    path = "../23_raw/"

    #open the gold label
    gold_label = pd.read_csv(gold_path)
    gold_conn_single_words = []
    gold_conn_multi_words = []
    for i in range(len(gold_label)):
        conn = gold_label.loc[i]['Offset-raw'].lower()
        if ((len(conn.split(" ")) == 1) & (conn not in gold_conn_single_words)):
            gold_conn_single_words.append(conn)
        elif ((len(conn.split(" "))> 1)&(conn not in gold_conn_multi_words)):
            gold_conn_multi_words.append(conn)

    nlp = spacy.load("en")
    outdf = pd.DataFrame(columns=['Offset-raw', 'filename', 'ConnSpanList'])
    for file in os.listdir(path):
        filename = os.path.join(path, file).split("/")[-1]
        print(filename)
        each_f = open(os.path.join(path, file), 'r', encoding="ascii", errors="backslashreplace").read()
        doc = nlp(each_f)
        for word in doc:
            if word.text.lower() in gold_conn_single_words:
                outdf = outdf.append({'Offset-raw':word.text.lower(), 'filename': filename, 'ConnSpanList':str(word.idx)+".."+str(word.idx+len(word.text))}, ignore_index=True)
        for sent in doc.sents:
            for conn in gold_conn_multi_words:
                if conn in str(sent).lower():
#                        print(conn, str(sent))
                    conn_tokens = [x.text for x in nlp(conn)]
                    for word in sent:
                        if (word.text.lower() == conn_tokens[0]):
#                                print('pernah kesini ga?')
                            outdf = outdf.append({'Offset-raw':conn, 'filename': filename, 'ConnSpanList':str(word.idx)+".."+str(word.idx+len(conn))}, ignore_index=True)
                                
                    
    true_label, predict_label, intersection = calculate_precision_recall_f1(gold_label, outdf)       
    not_detect = [value for value in true_label if value not in predict_label]
    false_detect = [value for value in predict_label if value not in true_label]
    
    
    return intersection

if __name__ == "__main__":
#    true_label, predict_label, intersection, not_detect = evaluate_ted()
    
    gold_path = "/home/ida/Documents/Saarland/ResearchImmersion/Data/BioDRB_explicit.txt"
    path = "clean_biodrb.txt"
    
    gold_label = pd.read_csv(gold_path, sep="|", header=None)
    
    all_gold = []
    gold_conn_single_words = []
    gold_conn_multi_words = []
    for i in range(len(gold_label)):
        conn = gold_label.loc[i][1].lower()
        if ((len(conn.split(" ")) == 1) and (len(conn.split(";"))==1) and (len(conn.split("-"))==1) and (len(conn.split("."))==1) and (len(conn.split("/"))==1) and (conn not in gold_conn_single_words)):
            gold_conn_single_words.append(conn)
        elif(((len(conn.split(" ")) > 1) or (len(conn.split(";")) > 1) or (len(conn.split("-"))>1) or (len(conn.split("."))>1) or (len(conn.split("/"))>1)) and (conn not in gold_conn_multi_words)):
                gold_conn_multi_words.append(conn)
                
    gold_conn_multi_words.append('1 hr.after')

    nlp = spacy.load("en")
    file = open(path, 'r').read()
    
    doc = nlp(file)

    outdf = pd.DataFrame(columns = ['Conn', 'FullSentence', 'Arg1', 'Arg2'])
    prev_sent = ""
    for sent in doc.sents:
        words = [x.text.lower() for x in sent]
        for i in range(len(words)):
            if "." in words[i]:
                words[i] = words[i].split(".")[-1]
            if words[i] in gold_conn_single_words:
                outdf = outdf.append({'Conn': words[i], 'FullSentence': str(sent), 'Arg1': str(sent[0:i]), 'Arg2': str(sent[i+1:len(words)])}, ignore_index=True)
        for conn in gold_conn_multi_words:
            if ";" in conn:
                conns = conn.split(";")
                result = [x in str(sent).lower() for x in conns]
                if np.prod(result) == 1 :
                    if len(result) > 1:
                        split_by_first_conn = str(sent).lower().split(conns[0])[1].split(conns[1])
                        arg1 = split_by_first_conn[0].strip()
                        arg2 = ' '.join(split_by_first_conn[1:]).strip()
                        outdf = outdf.append({'Conn': conn, 'FullSentence': str(sent), 'Arg1': arg1, 'Arg2': arg2}, ignore_index=True)
            elif (conn in str(sent).lower()):
#                print(conn)
                split_by_conn = str(sent).lower().split(conn)
                if len(split_by_conn) == 2:
                    arg1 = split_by_conn[0].strip()
                    arg2 = ' '.join(split_by_conn[1:]).strip()
                    outdf = outdf.append({'Conn': conn, 'FullSentence': str(sent), 'Arg1': arg1, 'Arg2': arg2}, ignore_index=True)
                else:
                    for i in range(len(split_by_conn) - 1):
                        arg1 = split_by_conn[i].strip()
                        arg2 = split_by_conn[i+1].strip()
                        outdf = outdf.append({'Conn': conn, 'FullSentence': str(sent), 'Arg1': arg1, 'Arg2': arg2}, ignore_index=True)
        prev_sent = str(sent)
                
    gold_label = pd.read_csv(gold_path, sep="|", header=None)
    all_gold =gold_conn_multi_words +gold_conn_single_words
    for i in range(len(gold_label)):
        gold_label.loc[i][1] = gold_label.loc[i][1].lower()
        

    all_gold = gold_conn_multi_words + gold_conn_single_words

    i = 1
    tuples = []
    for each in all_gold:
        if each == '1 hr. after':
            predict_slice_idx = list(outdf.loc[outdf['Conn']=='1 hr.after'].index) 
        else:
            predict_slice_idx = list(outdf.loc[outdf['Conn']==each].index) 
        gold_slice_idx =  list(gold_label.loc[gold_label[1]==each].index)
        for gold_idx in gold_slice_idx:
            gold_first = gold_label.loc[gold_idx][4].lower().strip()
#            gold_first_tokens = [x.text for x in nlp(gold_first) if x.text != " "]
            gold_second = gold_label.loc[gold_idx][5].lower().strip()
#            gold_second_tokens = [x.text for x in nlp(gold_second) if x.text != " "]
            print(">>", gold_idx, ">>>", i)
#            print(str(gold_second))
#            print(gold_first, '\n',gold_second)
            for pred_idx in predict_slice_idx:
                pred_first = re.sub(r'\[[^)]*\]', '', outdf.loc[pred_idx]['Arg1']).lower().strip(punctuation).replace("\n", " ").strip()
                pred_second = re.sub(r'\[[^)]*\]', '', outdf.loc[pred_idx]['Arg2']).lower().strip(punctuation).replace("\n", " ").strip()
                pred_full = re.sub(r'\[[^)]*\]', '', outdf.loc[pred_idx]['FullSentence']).lower().strip(punctuation).strip()
                pred_first_second = pred_first + " " + pred_second
#                pred_full_tokens = [x.text for x in nlp(pred_full)]
#                pred_first_tokens = [x.text for x in nlp(pred_first)]
#                pred_second_tokens = [x.text for x in nlp(pred_second)]
#                print(pred_first, pred_second, pred_full)
#                print(set(gold_second_tokens) - set(pred_full_tokens))
                if ((pred_first in gold_first and pred_first != "") or (pred_second in gold_second and pred_second!= "") or 
                    gold_first[:60] in pred_full or gold_second[:60] in pred_full or 
                    pred_first_second in gold_first or pred_first_second in gold_first or 
                    gold_first[:60] in pred_first_second or gold_second[:60] in pred_first_second):
                    print("kesatu", gold_idx, pred_idx, i)
                    tuples.append([gold_idx, pred_idx])
#                    gold_slice_idx.remove(gold_idx)
                    predict_slice_idx.remove(pred_idx)
                    break
#                else:
#                    if (len(set(gold_second_tokens) - set(pred_full_tokens)) == 0 or len(set(gold_first_tokens) - set(pred_full_tokens)) ==0):
#                        print("kedua", gold_idx, pred_idx)
#                        tuples.append([gold_idx, pred_idx])
#    #                    gold_slice_idx.remove(gold_idx)
#                        predict_slice_idx.remove(pred_idx)
#                        break
#                    elif (len(set(gold_first_tokens[:5]) - set(pred_full_tokens)) == 0 or len(set(gold_second_tokens[:5]) - set(pred_full_tokens)) == 0):
#                        print("ketiga", gold_idx, pred_idx)
#                        tuples.append([gold_idx, pred_idx])
#    #                    gold_slice_idx.remove(gold_idx)
#                        predict_slice_idx.remove(pred_idx)
#                        break
            i+=1