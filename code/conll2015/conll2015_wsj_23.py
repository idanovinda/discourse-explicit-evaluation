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
    path = "/home/ida/Documents/Saarland/ResearchImmersion/23_raw/"
    dest_path = "wsj_23_conll2015/conll2015/"
    parses_path = "wsj_23_conll2015/stanfordNLP_output/"
    fileext = ""
    
    for file in os.listdir(path):
        print(file)
        print(os.path.join(path, file).split("/")[-1])
#            f = open(os.path.join(path, file), 'r').read()
        filename = file
        
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
        f_content = open(raw_src, 'r', encoding="ascii", errors="backslashreplace").read()
        f_new = open(raw_dest + filename + '.txt', 'w')
        f_new.write(f_content)
        f_new.close()
        
        filename_parses = filename + ".json"
        
        
        parses_src = parses_path + filename_parses
        parses_dest = dest_path + filename + "/pdtb-parses.json"
        
        print(parses_src, parses_dest)

        parses_newPath = shutil.copy(parses_src, parses_dest)
        
def run_conll2015():
    path = "/home/ida/Documents/Saarland/ResearchImmersion/23_raw/"
    conll_path = "wsj_23_conll2015/conll2015/"
        
    for file in os.listdir(path):
        print(file)
        dir_path = conll_path + file
        command = "python2 ../Parser/conll2015_discourse/parser.py "+dir_path+" none "+dir_path
        os.system(command)
   
def evaluate_conll2015():
    conll_path = "wsj_23_conll2015/conll2015/"
    output_path = "wsj_23_conll2015/conll2015_output_arg/"
    
    df = pd.DataFrame(columns=['Offset-raw', 'filename', 'ConnSpanList'])
    not_found = []
    for file in os.listdir(conll_path):
        print(file)
        #open output from conll2015 run 
        try:
            conll_input = conll_path +file + '/pdtb-parses.json'
            conll_result  = conll_path + file + '/output.json'  
            result = extracting_result(conll_input, conll_result, file)
            result_path = output_path + file + '.json'
            f = open(result_path, 'w')
            f.write(json.dumps({file : result}))
            f.close()
            result_conn = extracting_conn_only_from_result(result, file)
            df = df.append(result_conn)
        except:
            not_found.append(file)
            print(file, " is not found")
            
    return df, not_found

if __name__ == "__main__":
    
    df, not_found = evaluate_conll2015()
    print("number of not found: ", len(not_found))
