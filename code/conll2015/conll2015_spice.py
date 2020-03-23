#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 18 19:28:30 2019

@author: ida
"""
import os
import shutil
import pandas as pd
import json
from string import punctuation

def organize_folder():
    path = "new_spice_output/"
    dest_path = "new_spice_output/conll2015/"
    parses_path = "new_spice_output/stanfordNLP_output/"
    fileext = ".txt"
    
    for file in os.listdir(path):
        if file.endswith(fileext):
            print(os.path.join(path, file).split("/")[-1])
#            f = open(os.path.join(path, file), 'r').read()
            filename = os.path.join(path, file).split("/")[1][:-4]
            
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
           
            filename_raw = filename + ".txt"
            filename_parses = filename + ".json"
            raw_src = path + filename_raw
            raw_dest = dest_path + filename + "/raw"
            parses_src = parses_path + filename_parses
            parses_dest = dest_path + filename + "/pdtb-parses.json"
            
            print(parses_src, parses_dest)
            
            raw_newPath = shutil.copy(raw_src, raw_dest)
            parses_newPath = shutil.copy(parses_src, parses_dest)
            

def run_conll2015():
    path = "new_spice_output/"
    conll_path = "new_spice_output/conll2015/"
    fileext = '.txt'
    
    for file in os.listdir(path):
        if file.endswith(fileext):
            filename = os.path.join(path, file).split("/")[1][:-4]
            print(filename)
            src_path = conll_path + filename
            dest_path = conll_path + filename
            command = "python2 ../Parser/conll2015_discourse/parser.py "+src_path+" none "+dest_path
#            print(command)
            os.system(command)
            
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

def extract_spice_conll2015():
    path = "new_spice_output/"
    conll_path = "new_spice_output/conll2015/"
    fileext = ".txt"
    

    for file in os.listdir(path):
        if file.endswith(fileext):
            filename = os.path.join(path, file).split("/")[1][:-4]
            print(filename)
            conll_input = conll_path + filename + '/pdtb-parses.json'
            conll_result = conll_path + filename + '/output.json'
            result = extracting_result(conll_input, conll_result, filename)
            result_path = conll_path + "JSON Result/" + filename + '.json'
            f = open(result_path, 'w')
            f.write(json.dumps({filename : result}))
            f.close()

def evaluate_spice_conll2015():
    path = "new_spice_output/"
    conll_path = "new_spice_output/conll2015/"
    fileext = ".txt"
    
    gold_path = "new_spice_output/spice_gold.csv"
    gold_df = pd.read_csv(gold_path)
    
    pred_conn = pd.DataFrame(columns=['filename', 'conn', 'arg1', 'arg2'])
    found = False
    for file in os.listdir(path):
        if file.endswith(fileext):
            filename = os.path.join(path, file).split("/")[1][:-4]
            print(filename)
            conll_input = conll_path + filename + '/pdtb-parses.json'
            conll_result = conll_path + filename + '/output.json'
            result = extracting_result(conll_input, conll_result, filename)
            found = True
            
            for i in range(len(result)):
                conn = ' '.join(result[i]['Connective']['raw']).strip()
                arg1 = ' '.join(result[i]['Arg1']['raw']).strip()
                arg2 = ' '.join(result[i]['Arg2']['raw']).strip()
                pred_conn = pred_conn.append({'filename': filename, 'conn': conn,
                                              'arg1': arg1, 'arg2': arg2}, ignore_index = True)

#%%        
    pred_dict = {}
    for i in range(len(pred_conn)):
        filename = pred_conn.loc[i]["filename"]
        conn = pred_conn.loc[i]["conn"].lower().strip()
        arg1 = pred_conn.loc[i]["arg1"]
        arg2 = pred_conn.loc[i]['arg2']
        if filename not in pred_dict:
            pred_dict[filename] = {}
            pred_dict[filename][conn] = [{'arg1': arg1.strip(punctuation).strip(), 'arg2': arg2.strip(punctuation).strip()}]
        elif conn not in pred_dict[filename]:
            pred_dict[filename][conn] = [{'arg1': arg1.strip(punctuation).strip(), 'arg2': arg2.strip(punctuation).strip()}]
        else:
            pred_dict[filename][conn].append({'arg1': arg1.strip(punctuation).strip(), 'arg2': arg2.strip(punctuation).strip()})

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
    
        
    match = 0
    match_conn = []
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
                                match += 1
                                found = True
                                match_conn.append([conn, filename, arg1, arg2])
                                break
                if found == False:
                    not_found.append(conn)
                i+=1
                if i%100 == 0:
                    print(i)
    return pred_conn, match_conn, gold_df