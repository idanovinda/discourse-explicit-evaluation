#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import pandas as pd
import spacy
import re
import os

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
#    file_name = re.sub("_", "-", file_name) + '.txt'
    for each in result:
        list_ =  [each['Connective']['raw'][0], file_name, each['Connective']['CharacterOffset'][0]]
        conn_df.loc[len(conn_df)] = list_
#        print(list_)
    return conn_df
    
def calculate_precision_reacall_f1(true_label_df, predict_label_df):
    true_label_df['Offset-raw'] = true_label_df['Offset-raw'].str.lower()
    predict_label_df['Offset-raw'] = predict_label_df['Offset-raw'].str.lower()
    
    true_label_list = true_label_df.values.tolist()
    predict_label_list = predict_label_df.values.tolist()
    
    intersection = [value for value in predict_label_list if value in true_label_list]
    
    precision = (len(intersection)/len(true_label_df))
    recall = (len(intersection)/len(predict_label_df))
    f1 = (2*precision*recall)/(precision+recall)
    print('Precision\t: ' + str(precision))
    print('Recall\t\t: ' + str(recall))
    print('F1-score\t: ' + str(f1))
    
    return intersection

def evaluate_ted_conll2015():
    ##set up the path for parsed word
    folder_path = '/home/ida/Documents/Saarland/ResearchImmersion/Parser/conll2015_discourse/data/TED-data/'
#    folder_name = ['talk_1927_en']
    folder_name = ['talk_1927_en', 'talk_1971_en', 'talk_1976_en', 'talk_1978_en', 'talk_2009_en', 'talk_2150_en_inter', 'talk_2150_en_intra']
    
    ted_df = pd.DataFrame(columns=['Offset-raw', 'filename', 'ConnSpanList'])
    for each_folder in folder_name:
        conll_input = folder_path +each_folder + '/pdtb-parses.json'
        conll_result  = folder_path + each_folder + '/output.json'  
        result = extracting_result(conll_input, conll_result, each_folder)
        result_path = folder_path + each_folder + '.json'
#        f = open(result_path, 'w')
#        f.write(json.dumps({each_folder : result}))
#        f.close()
        result_conn = extracting_conn_only_from_result(result, each_folder)
        ted_df = ted_df.append(result_conn)

    #open the gold dataset
    gold_path = '../../result-csv/ted_gold.csv'
    gold_df = pd.read_csv(gold_path)
    
    return ted_df, gold_df

def evaluate_biodrb_or_wsj(dataname):
    if dataname == 'biodrb':
        conll_path = 'new_biodrb_conll2015/'
        gold_path = '../Result/biodrb_gold_conll2015.csv'
    elif dataname == 'wsj23':
        conll_path = 'wsj_23_conll2015/conll2015/'
        gold_path = '../Result/wsj_23_gold_conll2015.csv'
    
    not_found = []
    pred_df = pd.DataFrame(columns=['Offset-raw', 'filename', 'ConnSpanList'])
    for folder in os.listdir(conll_path):
        print(folder)
        if 'output.json' in os.listdir(conll_path+folder):
            conll_input = conll_path + folder + '/pdtb-parses.json'
            conll_result = conll_path + folder + '/output.json'
            result = extracting_result(conll_input, conll_result, folder)
            result_conn = extracting_conn_only_from_result(result, folder)
            pred_df = pred_df.append(result_conn)
        else:
            print(">>>>not found")
            not_found.append(folder)
    gold_df = pd.read_csv(gold_path)
    
    
    #the result of conll2015 is shifted by 1
    #so before we are evaluating them, we should process them before
    #rename filename first
    new_offsets = []
    pred_df = pred_df.reset_index(drop=True)
    for i in pred_df.index:
        offset_list = pred_df.loc[i]['ConnSpanList'].split('..')
        offset = str(int(offset_list[0])-1) + '..' + str(int(offset_list[1])-1)
        new_offsets.append(offset)
    pred_df['ConnSpanList'] = new_offsets
        
    if dataname == 'wsj23':     
        pred_df['filename'] = [x[:-4].replace("-", "_") for x in pred_df['filename']]
        
    tp = calculate_precision_reacall_f1(gold_df, pred_df)
#    
    return pred_df, gold_df, tp, not_found