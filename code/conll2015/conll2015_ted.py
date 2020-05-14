#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 22 11:45:04 2020

@author: ida
"""

import os, re
import shutil
import pandas as pd
import json
from string import punctuation

def extracting_result(conll_input, conll_result, folder_name):
     #open input text and conll result 
    f_result = pd.read_json(conll_result, lines=True)
    
    #load input
    with open(conll_input) as f:
        f_input = json.load(f)
    
    #create dictionary of index and word from the file input and also the char offset
    word_index_dict = {}
    index = 0
    for sent in f_input[folder_name]['sentences']:
        for word in sent['words']:
            temp_dict = {}
            temp_dict['raw'] = word[0]
            temp_dict['offset'] = str(word[1]['CharacterOffsetBegin']+1) + '..' + str(word[1]['CharacterOffsetEnd']+1)
            word_index_dict[index] = temp_dict
            index += 1
            
    #extracting the output 
    result = []
    for x in range(len(f_result)):
        each_dict = {}
        if f_result.loc[x]['Type'] == 'Explicit':
            for idx in ['Connective', 'Arg1', 'Arg2']:
                each_dict[idx] = {'TokenList': f_result.loc[x][idx]['TokenList'],
                                       'raw': [word_index_dict[i]['raw'] for i in f_result.loc[x][idx]['TokenList']],
                                       'CharacterOffset': [word_index_dict[i]['offset'] for i in f_result.loc[x][idx]['TokenList']]}
            result.append(each_dict)          
    return result

def extracting_conn_only_from_result(result, file_name):
    conn_df = pd.DataFrame(columns=['Offset-raw', 'filename', 'ConnSpanList'])
    for each in result:
        list_ =  [each['Connective']['raw'][0], file_name, each['Connective']['CharacterOffset'][0]]
        conn_df.loc[len(conn_df)] = list_
#        print(list_)
    return conn_df

def organize_folder():
    path = "../../data/Ted-Talk/raw/"
    dest_path = "../../data/Ted-Talk/new_conll2015/"
    parses_path = "../../data/Ted-Talk/new_corenlp_output/"
    fileext = ".txt"
    
    for file in os.listdir(path):
        print(file)
        print(os.path.join(path, file).split("/")[-1])
#            f = open(os.path.join(path, file), 'r').read()
        filename = file.split(".")[0]
        
        main_dir = dest_path + filename
        raw_dir = main_dir + "/raw"
        print(raw_dir)
        try:
            os.mkdir(main_dir)
        except OSError:
            print("Creating directory %s, %s failed" % (main_dir, raw_dir))
        else:
            print("Successfully created %s, %s directory" %(main_dir, raw_dir))
            
        try:
            os.mkdir(raw_dir)
        except OSError:
            print("Creating directory %s, %s failed" % (main_dir, raw_dir))
        else:
            print("Successfully created %s, %s directory" %(main_dir, raw_dir))
       
        filename_raw = filename + fileext
        raw_src = path + filename_raw
        raw_dest = dest_path + filename + "/raw/"
        
        #convert the non-extension file to txt
        f_content = open(raw_src, 'r', encoding="utf-8", errors="ignore").read()
        f_new = open(raw_dest + filename + '.txt', 'w')
        f_new.write(f_content)
        f_new.close()
        
        filename_parses = filename + ".json"
        
        
        parses_src = parses_path + filename_parses
        parses_dest = dest_path + filename + "/pdtb-parses.json"
        
        print(parses_src, parses_dest)

        parses_newPath = shutil.copy(parses_src, parses_dest)
        
def run_conll2015():
    path = "../../data/Ted-Talk/raw/"
    conll_path = "../../data/Ted-Talk/new_conll2015/"
        
    for file in os.listdir(path):
        print(file)
        dir_path = conll_path + file.split(".")[0]
        command = "python2 conll2015_discourse/parser.py "+dir_path+" none "+dir_path
        os.system(command)
   
def evaluate_conll2015():
    conll_path = "../../data/Ted-Talk/new_conll2015/"
#    output_path = "../../data/Ted-Talk/new_conll2015/"
    
    df = pd.DataFrame(columns=['Offset-raw', 'filename', 'ConnSpanList'])
    not_found = []
    for file in os.listdir(conll_path):
        print(file)
        #open output from conll2015 run 
#        try:
        conll_input = conll_path + file.split(".")[0] + '/pdtb-parses.json'
        conll_result  = conll_path + file.split(".")[0] + '/output.json'  
        result = extracting_result(conll_input, conll_result, file )
#            result_path = output_path + file + '.json'
#            f = open(result_path, 'w')
#            f.write(json.dumps({file : result}))
#            f.close()
        result_conn = extracting_conn_only_from_result(result, file.split(".")[0])
        df = df.append(result_conn)
#        except:
#            not_found.append(file)
#            print(file, " is not found")
#            
    return df, not_found



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

if __name__ == "__main__":
#    organize_folder()
    # run_conll2015()
    df, not_found = evaluate_conll2015()
    ted_df = pd.read_csv("../../result-csv/ted_gold.csv")
    tpdf = calculate_precision_recall_f1(ted_df, df)
#    print("number of not found: ", len(not_found))
