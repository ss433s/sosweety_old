##############
# 第一步 找出所有在kb的NN
##############

import json
import os, sys
# import sqlite3
# import pandas as pd
sys.path.append("..")
sys.path.append("../..")
from kb import Knowledge_base
from utils.utils import stanford_simplify


# 当前路径和项目root路径， 可以根据需求改变../..
this_file_path = os.path.split(os.path.realpath(__file__))[0]
root_path = os.path.abspath(os.path.join(this_file_path, "../.."))

# 打开语料文件
file_path = 'data/corpus/baidu_ie_competition/parse_file_total'
file_path = os.path.join(root_path, file_path)
file = open(file_path)

KB = Knowledge_base()
cutoff = 1000

line = file.readline()
noun_id_set = set()
word2id_dict = {}
count = 0
while line:
    count += 1
    if count % 5000 == 0:
        print('parsed %s sentence' % count)
    line = line.strip().split('\t')
    pos_tags = json.loads(line[1].strip())
    pos_tags = stanford_simplify(pos_tags)
    for word, pos_tag in pos_tags:
        if pos_tag == 'NN':
            concept_ids = KB.get_word_ids(word, 0)
            word2id_dict[word] = concept_ids
            for concept_id in concept_ids:
                noun_id_set.add(concept_id[0])

    line = file.readline()
file.close()

print(len(noun_id_set))

noun_file_path = 'data/3_phrase_pattern/nouns'
noun_file_path = os.path.join(root_path, noun_file_path)
with open(noun_file_path, 'w') as noun_file:
    for concept_id in noun_id_set:
        noun_file.write(str(concept_id) + '\n')

noun2id_file_path = 'data/3_phrase_pattern/noun2id'
noun2id_file_path = os.path.join(root_path, noun2id_file_path)
with open(noun2id_file_path, 'w') as noun2id_file:
    for word in word2id_dict:
        noun2id_file.write(word + '\t' + str(word2id_dict[word]) + '\n')
