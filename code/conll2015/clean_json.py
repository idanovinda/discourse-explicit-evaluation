#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 09:09:22 2020

@author: idanovinda
"""


import json
import pandas as pd
import re


conll_input = "../../data/Ted-Talk/conll2015/talk_1927_en/pdtb-parses.json"
with open(conll_input) as f:
    f_input = json.load(f)
    
dumps = json.dumps(f_input)
    
clean_input = re.sub(" +", " ", re.sub(r"(?<!\\)\\n|\n", " ", dumps))

# output_filepath = "../../data/Ted-Talk/conll2015/talk_1927-pdtb-parses.json"
# f_out = open(output_filepath, "w")
# f_out.write(clean_input)
# f_out.close()
#%%
new_conll_input = "../../data/Ted-Talk/new_conll2015/talk_1927_en/pdtb-parses.json"
with open(new_conll_input) as f:
    new_f_input = json.load(f)
    
new_dumps = json.dumps(new_f_input)

