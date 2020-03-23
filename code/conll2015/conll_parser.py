#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pycorenlp import StanfordCoreNLP
import json
import os
import sys
from xmltodict import parse
import re
import spacy

def text_parser(text):
    nlp_wrapper = StanfordCoreNLP('http://localhost:9000')
    annot_text = nlp_wrapper.annotate(text, properties={
      'annotators': 'tokenize,ssplit,pos,depparse,parse',
      'outputFormat': 'xml'})
    print('parsing text finished!')
    return annot_text

def xml2json(xmlstring):
	"""Convert xmlstring from StanfordCoreNLP to json format"""
	temp_dict = parse(xmlstring)
#	print temp_dict
	new_dict = {}
	new_dict['sentences'] = []
	for i, sentence in enumerate(temp_dict['root']['document']['sentences']['sentence']):
#		if i <= 1:
#			continue
		s = {}
		s['parsetree'] = sentence['parse'].replace("ROOT", "")
		if 'dep' in sentence['dependencies'][0]:
			s['dependencies'] = extract_dependency_triplets(sentence['dependencies'][0]['dep'])
		else:
			s['dependencies'] = []

		s['words'] = []
		#if there are no multiple entries. the xmltodict does not give out a list.
		if not isinstance(sentence['tokens']['token'], list):
			sentence['tokens']['token'] = [sentence['tokens']['token']]
		for word in sentence['tokens']['token']:
			word_info = {}
			token = word['word']
			word_info['PartOfSpeech'] = word['POS']
			word_info['CharacterOffsetBegin'] = int(word['CharacterOffsetBegin'])
			word_info['CharacterOffsetEnd'] = int(word['CharacterOffsetEnd'])
			s['words'].append((token, word_info))

		new_dict['sentences'].append(s)

	return new_dict

def extract_dependency_triplets(dependency_list):
	new_relations = []
	#if there are no multiple entries. the xmltodict does not give out a list.
	if not isinstance(dependency_list, list):
		dependency_list = [dependency_list]

	for relation in dependency_list:
		new_relation = (relation['@type'],
				'%s-%s' % (relation['governor']['#text'], relation['governor']['@idx']),
				'%s-%s' % (relation['dependent']['#text'], relation['dependent']['@idx']))
		new_relations.append(new_relation)
	return new_relations
#%%
def splitted_string(string):
    splitted = []
    max_length = 10000
    paragraph = string.split("\n\n")
    onefile = ""
    for par in paragraph: 
        #split paragraph into sentences
        sents = par.split('.')
#        print(sents)
#        print(onefile)
        for sent in sents:
            if sent != "":
#                print("sent\t", sent)
                new_len = len(onefile) + len(sent) + 1
                if len(sent) > max_length:
                    print(len(sent))
                if len(onefile) == 0:
                    onefile = sent + '. '
                elif  new_len < max_length:
                    onefile = onefile + sent + '. '
                else:
                    splitted.append(onefile)
                    onefile = sent
        onefile = onefile + "\n\n"
    splitted.append(onefile)
    return splitted
#%%
def run_biodrb():
    fileext = '.txt'
    path = "bio-cut/"
    parser_output_path = "bio-cut-parses/"
    
    for file in os.listdir(path):
        if file.endswith(fileext):
            print(os.path.join(path, file).split("/")[-1])
            f = open(os.path.join(path, file), 'r').read()
            filename = os.path.join(path, file).split("/")[1][:-4]

            print(filename)
            output_filepath = parser_output_path + os.path.join(path, file).split("/")[-1][:-4] + '.json'
            print(output_filepath)
            anot_f = text_parser(f)
            print("Finished parsing")
            result_json = xml2json(anot_f)
            output = json.dumps({filename: result_json})
            output = re.sub(" +", " ", re.sub(r"(?<!\\)\\n|\n", " ", output))
            f_out = open(output_filepath, "w")
            f_out.write(output)
            f_out.close()
        
    
def run_spice():
    fileext = '.txt'
    path = "new_spice_output/"
    parser_output_path = "new_spice_output/stanfordNLP_output/"
    
    for file in os.listdir(path):
        if file.endswith(fileext):
            print(os.path.join(path, file).split("/")[-1])
            f = open(os.path.join(path, file), 'r').read()
            filename = os.path.join(path, file).split("/")[1][:-4]

            print(filename)
            output_filepath = parser_output_path + os.path.join(path, file).split("/")[-1][:-4] + '.json'
            print(output_filepath)
            anot_f = text_parser(f)
            print("Finished parsing")
            result_json = xml2json(anot_f)
            output = json.dumps({filename: result_json})
            output = re.sub(" +", " ", re.sub(r"(?<!\\)\\n|\n", " ", output))
            f_out = open(output_filepath, "w")
            f_out.write(output)
            f_out.close()
                    
def run_biodrb_one(number):
    filename = "raw_"+str(number)
    in_path = "bio-cut/"+filename+".txt"
    out_path = filename+".json"
    f = open(in_path, "r").read()
    f = remove_space(f)
    anot_f = text_parser(f)
    result_json = xml2json(anot_f)
    output = json.dumps({filename: result_json})
    output = re.sub(" +", " ", re.sub(r"(?<!\\)\\n|\n", " ", output))
    f_out = open(out_path, "w")
    f_out.write(output)
    f_out.close()

def remove_space(file):
    newfile = file.replace(". ", ".")
    return newfile

def run_wsj_23():
    path = "wsj_23_conll2015/conll2015/wsj_2300/raw/"
    dest = "wsj_23_conll2015/"
    i = 1
    
    extracted_files = [x.split(".")[0] for x in os.listdir(dest)]
    
    for file in os.listdir(path):
        print(file, i)
        i+=1
#        if file not in extracted_files:
        f = open(path+file, 'r', encoding="ascii", errors="backslashreplace").read()
        output_filepath = dest + file + '.json'
        anot_f = text_parser(f)
        print("Finished parsing")
        result_json = xml2json(anot_f)
        output = json.dumps({file: result_json})
        output = re.sub(" +", " ", re.sub(r"(?<!\\)\\n|\n", " ", output))
        f_out = open(output_filepath, "w")
        f_out.write(output)
        f_out.close()


#%%
if __name__=="__main__":
      
    path = "/home/ida/Documents/Saarland/ResearchImmersion/Parser/bio-parser/BioDRB/GeniaRaw/Genia/"
    output_path = "new_biodrb/"
    
    for file in os.listdir(path):
        filename = file[:-4]
        print(filename)
        output_file = output_path + filename +".json"
#        print(output_file)
        f = open(path+file, 'r').read()
        # print(">>>>", len(f))
        if (filename + '.json') not in os.listdir(output_path):
            try:
                
                anot_f = text_parser(f)
                print("Finished parsing")
                result_json = xml2json(anot_f)
                output = json.dumps({filename: result_json})
                output = re.sub(" +", " ", re.sub(r"(?<!\\)\\n|\n", " ", output))
                f_out = open(output_file, "w")
                f_out.write(output)
                f_out.close()
            except:
                print("the file is too long...")

            
            
