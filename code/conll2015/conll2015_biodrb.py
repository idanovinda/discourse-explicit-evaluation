#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 27 19:32:53 2019

@author: ida
"""

import os
import shutil
import subprocess
import pandas as pd
import json


def organize_folder():
    raw_path = "../discourse-explicit/data/BioDRB/Genia Raw/"
    parses_path = "new_biodrb/"
    dest_path = "new_biodrb_conll2015/"
    
    for file in os.listdir(raw_path):
        filename = file[:-4]
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
       
        filename_raw = file
        filename_parses = filename + ".json"
        raw_src = raw_path + filename_raw
        raw_dest = dest_path + filename + "/raw"
        parses_src = parses_path + filename_parses
        parses_dest = dest_path + filename + "/pdtb-parses.json"
        
        raw_newPath = shutil.copy(raw_src, raw_dest)
        parses_newPath = shutil.copy(parses_src, parses_dest)
        
def run_conll2015():
    path = "new_biodrb_conll2015/"
    for file in os.listdir(path):
        print(file)
        file_path = path + file
        if 'output.json' not in os.listdir(file_path):
            print("nooo")
            command = "python2 ../Parser/conll2015_discourse/parser.py " + path + file + " none " + path + file
#            print(command)
            os.system(command)
        else:
            print(">>gut")


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

def extract_explicit():
    path = "bio-conll2015/raw_"
    all_explicit = []
    not_extracted = []
    for i in range(3,4):
        print(i)
        conll_input = path+str(i)+"/pdtb-parses.json"
        conll_result = path+str(i)+"/output.json"
        folder_name = "raw_"+str(i)
        try:
            result = extracting_result(conll_input, conll_result, folder_name)
            all_explicit.extend(result)
        except:
            not_extracted.append(i)
    return all_explicit, not_extracted


        
if __name__ == "__main__":
#    organize_folder()
#    print("Organize folder finished!")
    run_conll2015()
#    print("Finish running conll2015 parser")
#    all_explicit, not_extracted = extract_explicit()
    print("Finish extract explicit")
   