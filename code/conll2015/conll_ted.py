#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 30 16:18:19 2019

@author: ida
"""

import pandas as pd

path = '/home/ida/Documents/Saarland/Research Immersion /Parser/conll2015_discourse/data/TED-data/'
list_of_dir = ['talk_1927_en', 'talk_1971_en', 'talk_1976_en', 'talk_1978_en', 'talk_2009_en', 'talk_2150_en_inter', 'talk_2150_en_intra']


outdf = pd.DataFrame(columns=['Offset-raw', 'filename', 'ConnSpanList'])

file = list_of_dir[0]
filepath = path + file +"/output.json"
f = open(filepath, 'r').read()
f_line = f.split("\n")
for each in f_line:
    if each["Type"] == "Explicit":
        outdf = outdf.append({'Offset-raw': each['conn_name'] , 'filename':file+'.txt', 'ConnSpanList':})