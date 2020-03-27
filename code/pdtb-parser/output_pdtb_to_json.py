#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  7 12:50:27 2019

@author: ida
"""

import pandas as pd
import json
import re
import os
from string import punctuation

def extract_explicit(pdtb_result, file_name):
    
    ## for comparison of gold dataset
    slicing = pd.DataFrame(columns=['Offset-raw', 'filename', 'ConnSpanList'])    
    
    #for extracting the variable in json
    result = []
    for i in range(len(pdtb_result)):
        each_dict = {}
        explicit = {}
        if pdtb_result.loc[i, 0] == 'Explicit':
            explicit['Offset-raw'] = pdtb_result.loc[i, 5]
            explicit['filename'] = file_name
            explicit['ConnSpanList'] = pdtb_result.loc[i, 3]
            arg_index = {'Connective': [3, 5], 'Arg1': [22, 24], 'Arg2': [32, 34]}
            for idx in arg_index:
                each_dict[idx] = {'CharacterOffset': pdtb_result.loc[i, arg_index[idx][0]],
                                       'raw': pdtb_result.loc[i, arg_index[idx][1]]}
            result.append(each_dict)
            slicing = slicing.append(explicit, ignore_index=True)
    return slicing, result

#%%
def calculate_precision_recall_f1(true_label_df, predict_label_df):
    true_label_df['Offset-raw'] = true_label_df['Offset-raw'].str.lower()
    predict_label_df['Offset-raw'] = predict_label_df['Offset-raw'].str.lower()
    true_label_list = true_label_df.values.tolist()
    predict_label_list = predict_label_df.values.tolist()
    
    intersection = [value for value in predict_label_list if value in true_label_list]
    print('#intersection: ', len(intersection))
    
    if len(predict_label_df) != 0:
        precision = (len(intersection)/len(true_label_df))
        recall = (len(intersection)/len(predict_label_df))
        f1 = (2*precision*recall)/(precision+recall)
        print('Precision\t: ' + str(precision))
        print('Recall\t\t: ' + str(recall))
        print('F1-score\t: ' + str(f1))
        
        return true_label_list, predict_label_list, intersection
#%%
def evaluate_ted_pdtb():
    ted_path = "/home/ida/Documents/Saarland/ResearchImmersion/a_pdtb/TED-data/output/"
    
    file_names = ['talk_1927_en', 'talk_1971_en', 'talk_1976_en', 'talk_1978_en', 'talk_2009_en', 'talk_2150_en_inter', 'talk_2150_en_intra']
    
    ted_df = pd.DataFrame(columns=['Offset-raw', 'filename', 'ConnSpanList'])
    for each_file in file_names:
        filepath = ted_path + each_file + '.txt.pipe'
        f_pdtb = pd.read_table(filepath, sep='|', header=None)
        slicing, f_result = extract_explicit(f_pdtb, each_file)
        
        #append to the dataframe that is going to be compared
        ted_df = ted_df.append(slicing)
        
        #save the result as output file .json
        dest_path = ted_path + each_file + '.json'
        f = open(dest_path, 'w')
        f.write(json.dumps({each_file : f_result}))
        f.close()
        
    gold_path = '../../result-csv/ted_gold.csv'
    gold_df = pd.read_csv(gold_path, sep=',')
    true_label_list, predict_label_list, intersection = calculate_precision_recall_f1(gold_df, ted_df)
    
    return ted_df, gold_df, intersection

def extract_spice_pdtb():
    prev_path = "/home/ida/Documents/Saarland/ResearchImmersion/Parser/pdtb-parser/data/SPICE/"
    path = prev_path + "output/"
    fileext = ".txt.pipe"
    dest = "/home/ida/Documents/Saarland/ResearchImmersion/a_pdtb/SPICE/"
    df = pd.DataFrame(columns=['Offset-raw', 'filename', 'ConnSpanList'])
    for file in os.listdir(path):
        if file.endswith(fileext):
            filepath = os.path.join(path, file)
            filename = filepath.split("/")[-1].split(".")[0]
            print(">>>", filename)
            f_pdtb = pd.read_table(filepath, sep='|', header=None)
            slicing, f_result = extract_explicit(f_pdtb, filename)
            
            df = df.append(slicing, ignore_index=True)
            dest_path = dest + filename + '.json'
            f = open(dest_path, 'w')
            f.write(json.dumps({filename : f_result}))
            f.close()
        
    return df

def evaluate_spice_pdtb():
    prev_path = "/home/ida/Documents/Saarland/ResearchImmersion/Parser/pdtb-parser/data/SPICE/"
    path = prev_path + "output/"
    fileext = ".pipe"
    
    gold_path = "new_spice_output/spice_gold.csv"
    gold_df = pd.read_csv(gold_path)
    
    #find all file with .txt.pipe format
    pred_conn = pd.DataFrame(columns=['filename', 'conn', 'arg1', 'arg2'])
    found = False
    for file in os.listdir(path):
        if file.endswith(fileext):
            filepath = os.path.join(path, file)
            filename = filepath.split("/")[-1].split(".")[0]
            print(">>>", filename)
            file_text = open(prev_path+filename+".txt", "r").read()
            file_pdtb = pd.read_table(filepath, sep='|', header=None)
            
            gold_file = gold_df[gold_df['filename']==filename]
            for i in range(len(file_pdtb)):
                explicit = file_pdtb.loc[i][0]
                if explicit == "Explicit":
#                    print("yes")
                    conn = file_pdtb.loc[i][8]
                    arg1 = file_pdtb.loc[i][24]
                    arg2 = file_pdtb.loc[i][34]
                    pred_conn = pred_conn.append({'filename': filename, 'conn': conn, 'arg1': arg1, 'arg2': arg2}, ignore_index=True)
#                    print(conn, "\n", arg1, "\n", arg2)
                
            found = True
#        if found:
#            break

    #%%
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

    #%%
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
    
    return pred_conn, match_connective, gold_df

def evaluate_wsj23():
    wsj_outpath = "/home/ida/Documents/Saarland/ResearchImmersion/parser-result-master/23/output/"
    fileext = ".pipe"
    json_output_dest = "wsj_23_json_pdtb/"
    df = pd.DataFrame(columns=['Offset-raw', 'filename', 'ConnSpanList'])
    for file in os.listdir(wsj_outpath):
        if file.endswith(fileext):
            print(file)
            filename = file.split(".")[0]
            f_read = open(wsj_outpath+file, 'r').read()
            if len(f_read) != 0:
                f_pdtb = pd.read_table(wsj_outpath+file, sep='|', header=None, error_bad_lines=False)
                slicing, f_result = extract_explicit(f_pdtb, filename)
                
                #append to the dataframe that is going to be compared
                df = df.append(slicing)
            
                #save the result as output file .json
                dest_path = json_output_dest + filename + '.json'
                f = open(dest_path, 'w')
                f.write(json.dumps({filename : f_result}))
                f.close()
            else:
                print(">>>>>>>>kosongggg")
                
#        
    gold_path = 'gold_wsj_sec23.csv'
    gold_df = pd.read_csv(gold_path, sep=',')
    gold_new_df = pd.DataFrame()
    gold_new_df['Offset-raw']= gold_df['Connective']
    gold_new_df['filename']= gold_df['filename']
    gold_new_df['ConnSpanList']= gold_df['ConnSpan']
    
    pred_sort = df.sort_values(by=['filename', 'Offset-raw', 'ConnSpanList'])
    
    true, predict, intersection = calculate_precision_recall_f1(gold_new_df, pred_sort)
    fp = [value for value in predict if value not in true]
    fn = [value for value in true if value not in predict]
    
    return fp, fn, intersection

def evaluate_biodrb():
    raw_path = "/home/ida/Documents/Saarland/ResearchImmersion/Parser/pdtb-parser/data/BioDRB/"
    extracted_path = "/home/ida/Documents/Saarland/ResearchImmersion/Parser/pdtb-parser/data/BioDRB/output/"
    gold_path = "/home/ida/Documents/Saarland/ResearchImmersion/Parser/bio-parser/pdtb_vs_biodrb/bio_drb_gold/"
    
    ##take the gold first
    ##define empty dataframe to store explicit gold
    gold_df = pd.DataFrame(columns=['Offset-raw', 'filename', 'ConnSpanList'])

    for gold_file in os.listdir(gold_path):
        print(gold_file)
        filename = gold_file[:-5]
        gold_file_df = pd.read_table(gold_path + gold_file, sep='|', header=None)
        raw_text = open(raw_path + filename, 'r').read()
        
        for i in gold_file_df.index:
            if gold_file_df.loc[i][0] == 'Explicit':
                index_conns = gold_file_df.loc[i][1].split(";")
                index_split = [x.split("..") for x in index_conns]
                raw_conn = ';'.join([raw_text[int(x[0]): int(x[1])] for x in index_split])
#                print(raw_conn)
                gold_df = gold_df.append({'Offset-raw': raw_conn, 'filename': filename, 'ConnSpanList':gold_file_df.loc[i][1]}, ignore_index=True )

    ##take the result of the runned pdtb
    pred_df = pd.DataFrame(columns=['Offset-raw', 'filename', 'ConnSpanList'])
    for result_file in os.listdir(extracted_path):
        if result_file.endswith(".pipe"):
            print(result_file)
            filename = result_file[:-5]
            result_file_df = pd.read_table(extracted_path + result_file, sep='|', header=None)
            for i in result_file_df.index:
                if result_file_df.loc[i][0] == 'Explicit':
                    pred_df = pred_df.append({'Offset-raw': result_file_df.loc[i][5], 'filename': filename, 'ConnSpanList': result_file_df.loc[i][3]}, ignore_index=True)
                    
    #let's evaluate the result 
    gold_list = gold_df.values.tolist()
    pred_list = pred_df.values.tolist()
    
    intersection = [value for value in gold_list if value in pred_list]
    false_pos = [value for value in pred_list if value not in gold_list]
    false_neg = [value for value in gold_list if value not in pred_list]
    print(len(intersection), len(false_pos), len(false_neg))
    
    return gold_df, pred_df, intersection