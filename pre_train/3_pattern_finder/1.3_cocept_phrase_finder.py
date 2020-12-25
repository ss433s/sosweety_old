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

# 准备关系字典和上位词set
all_upper_concepts_set = set()
relation_dict = {}
dict_file_path = 'data/3_phrase_pattern/relation_dict'
dict_file_path = os.path.join(root_path, dict_file_path)
with open(dict_file_path) as dict_file:
    for line in dict_file.readlines():
        line = line.strip().split('\t')
        upper_concepts = eval(line[1])
        relation_dict[line[0]] = upper_concepts
        for concept in upper_concepts:
            all_upper_concepts_set.add(concept)

# 准备noun2id字典
word2id_dict = {}
noun2id_file_path = 'data/3_phrase_pattern/noun2id'
noun2id_file_path = os.path.join(root_path, noun2id_file_path)
with open(noun2id_file_path) as noun2id_file:
    lines = noun2id_file.readlines()
    for line in lines:
        line = line.strip().split('\t')
        word2id_dict[line[0]] = eval(line[1])

# 准备所有的上位词的feature字典
all_features = {}
for concept in all_upper_concepts_set:
    feature = {}
    word = KB.get_concept_word(concept)
    feature['concept'] = concept
    feature['word'] = word
    all_features[concept] = feature


# 强行遍历各种可能性2-3个词
def checkout_concept_phrase(pos_tags):

    def create_features_for_item(item):

        # 当前词自身作为feature
        item_raw_feature = {'word': item[0]}
        item_all_features = [item_raw_feature]
        # 获取当前词对应的所有concept id
        item_concepts = word2id_dict[item[0]]
        # 获取当前词所有的上位feature
        for concept in item_concepts:
            # 这个concept id 有上位关系
            concept_id = concept[0]
            if concept_id in relation_dict:
                # 将所有上位关系加入item_all_features
                upper_concepts = relation_dict[concept_id]
                for upper_concept in upper_concepts:
                    item_all_features.append(all_features[upper_concept])
        return item_all_features

    concept_phrases = []
    for i in range(len(pos_tags)-1):
        item = pos_tags[i]
        next_item = pos_tags[i+1]
        if item[1] == 'NN' and next_item[1] == 'NN':
            item_concept_phrases = []
            # 获取两个词的所有feature
            item_all_features = create_features_for_item(item)
            next_item_all_features = create_features_for_item(next_item)
            # 交叉组合所有feature
            for feature1 in item_all_features:
                for feature2 in next_item_all_features:
                    item_concept_phrases.append([feature1, feature2])

            concept_phrases += item_concept_phrases

            if i < len(pos_tags) - 2:
                next_next_item = pos_tags[i+2]
                if next_next_item[1] == 'NN':
                    next_next_item_all_features = create_features_for_item(next_next_item)
                    for phrase in item_concept_phrases:
                        for feature3 in next_next_item_all_features:
                            phrase3 = phrase.append(feature3)
                            concept_phrases.append(phrase3)
    return concept_phrases


# 找phrase
lines = file.readlines()
total_concept_phrase = []
for i in range(len(lines)):
    if i % 100 == 0:
        print('parsed %s sentence, total %s' % (i, len(lines)))
    if i == 100:
        break
    line = lines[i].split('\t')
    parse_str = line[0]
    pos_tags = json.loads(line[1].strip())
    pos_tags = stanford_simplify(pos_tags)
    total_concept_phrase += checkout_concept_phrase(pos_tags)


# 写入文件
concept_phrase_file_path = 'data/3_phrase_pattern/concept_phrases'
concept_phrase_file_path = os.path.join(root_path, concept_phrase_file_path)
with open(concept_phrase_file_path, 'w') as concept_phrase_file:
    lines = concept_phrase_file.readlines()
    for line in lines:
        line = line.strip().split('\t')
        word2id_dict[line[0]] = eval(line[1])

'''
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
'''
