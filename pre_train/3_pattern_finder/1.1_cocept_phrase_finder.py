##############
# 第一步 找出所有在kb的NN
##############

import json
import os, sys
# import sqlite3
# import pandas as pd
sys.path.append("..")
sys.path.append("../..")
from parser_class import Word, Parse_result
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
noun_id_dict = {}
count = 0
while line:
    count += 1
    if count % 1000 == 0:
        print('parsed %s sentence' % count)
        break
    line = line.strip().split('\t')
    pos_tags = json.loads(line[1].strip())
    pos_tags = stanford_simplify(pos_tags)
    for word, pos_tag in pos_tags:
        if pos_tag == 'NN':
            concept_ids = KB.get_word_ids(word, 0)
            for concept_id in concept_ids:
                if concept_id[0] not in noun_id_dict:
                    noun_id_dict[concept_id[0]] = 1

    line = file.readline()
file.close()

print(len(noun_id_dict))

noun_file_path = 'data/3_phrase_pattern/nouns'
noun_file_path = os.path.join(root_path, noun_file_path)
with open(noun_file_path, 'w') as noun_file:
    for concept_id in noun_id_dict:
        noun_file.write(str(concept_id) + '\n')


# 递推所有上层concept
def all_concept_id_in_dict(noun_id_set):
    if len(noun_id_set) == 0:
        result = True
    else:
        result = all([concept_id in noun_id_dict for concept_id in noun_id_set])
    return result


noun_id_set = set(noun_id_dict.keys())
next_level_concept_id_set = set()
for concept_id in noun_id_set:
    next_level_concept_ids = KB.get_concept_upper_relations(concept_id)
    for next_level_concept_id in next_level_concept_ids:
        next_level_concept_id_set.add(next_level_concept_id)
    noun_id_dict[concept_id] = next_level_concept_ids

level = 1
while not all_concept_id_in_dict(next_level_concept_id_set):
    level += 1
    print('dealing with the %s level concept' % level)
    print(len(noun_id_dict))
    next_next_level_concept_id_set = set()
    for next_level_concept_id in next_level_concept_id_set:
        if next_level_concept_id not in noun_id_dict:
            next_next_level_concept_ids = KB.get_concept_upper_relations(next_level_concept_id)
            for next_next_level_concept_id in next_next_level_concept_ids:
                next_next_level_concept_id_set.add(next_next_level_concept_id)
            noun_id_dict[next_level_concept_id] = next_next_level_concept_ids
    next_level_concept_id_set = next_next_level_concept_id_set


# 构建word 对应的上层concept表
def all_concept_id_in_set(noun_id_set, upper_concepts):
    if len(noun_id_set) == 0:
        result = True
    else:
        result = all([concept_id in upper_concepts for concept_id in noun_id_set])
    return result


final_dict = {}
for concept_id in noun_id_set:
    upper_concepts = set(noun_id_dict[concept_id])
    l2_concept_set = set(noun_id_dict[concept_id])
    l3_concept_set = set()
    for l2_single_concept in l2_concept_set:
        l3_single_concept_set = set(noun_id_dict[l2_single_concept])
        # upper_concepts = upper_concepts | l3_single_concept_set
        l3_concept_set = l3_concept_set | l3_single_concept_set

    while not all_concept_id_in_set(l3_concept_set, upper_concepts):
        upper_concepts = upper_concepts | l3_concept_set
        l4_concept_set = set()
        for l3_single_concept in (l3_concept_set-upper_concepts):
            l4_single_concept_set = set(noun_id_dict[l3_single_concept])
            # upper_concepts = upper_concepts | l3_single_concept_set
            l4_concept_set = l4_concept_set | l4_single_concept_set
        l3_concept_set = l4_concept_set

    upper_concepts = upper_concepts | l3_single_concept_set

    final_dict[concept_id] = list(upper_concepts)


total_concept_phrase = []
for i in range(len(lines)):
    if i % 3000 == 0:
        print('parsed %s sentence, total %s' % (i, len(lines)))

    line = lines[i].split('\t')
    parse_str = line[0]
    pos_tags = json.loads(line[1].strip())
    pos_tags = stanford_simplify(pos_tags)

    tmp_stamp = 0
    for i in range(len(pos_tags)):
        pos_tag = pos_tags[i]
        if pos_tag[0] in ['。', '！', '？', '?', '，', ',', ';', '；']:
            ss_parse_result = tuples2parse_result(pos_tags[tmp_stamp: i])
            tmp_stamp = i + 1
            total_concept_phrase += checkout_concept_phrase(ss_parse_result)
    if tmp_stamp < len(pos_tags):
        ss_parse_result = tuples2parse_result(pos_tags[tmp_stamp: len(pos_tags)])
        total_concept_phrase += checkout_concept_phrase(ss_parse_result)

with open('./init_data/all_concept_phrases', 'w') as f:
    for i in total_concept_phrase:
        f.write(json.dumps(i, ensure_ascii=False) + '\n')


# pandas排序去重，不能是json，直接读字符串就行, 写csv速度更快
# with open('./init_data/123') as f:
with open('./init_data/all_concept_phrases') as f:
    total_concept_phrase = []
    lines = f.readlines()
    for line in lines:
        line = line.strip()
        # concept_phrase = json.loads(line)
        total_concept_phrase.append(line)

    df_dict = {}
    df_dict['concept_phrase'] = total_concept_phrase
    df = pd.DataFrame(df_dict)
    df2 = df.concept_phrase.value_counts()
    # df2.to_csv('./init_data/123stat.csv')
    df3_dict = {'label': df2.index, 'count': df2.values}
    df3 = pd.DataFrame(df3_dict)
    with open('./init_data/all_concept_phrases_stat', 'w') as result_file:
        for i in range(len(df3)):
            result_file.write(df3['label'][i] + '\t' + str(df3['count'][i]) + '\n')
