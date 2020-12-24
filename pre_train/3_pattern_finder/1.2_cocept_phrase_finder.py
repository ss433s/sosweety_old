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

# 阈值
cutoff = 1000


# parse result构建
def tuples2parse_result(tuples):
    content = []
    for word in tuples:
        tmp_word = Word(word[0], word[1])
        content.append(tmp_word)
    parse_result = Parse_result(content)
    return parse_result


# 强行遍历各种可能性2-3个词
def checkout_concept_phrase(parse_result):

    def create_feature(word_relation):
        feature = {}
        feature['concept'] = word_relation[0]
        feature['word'] = KB.get_concept_word(word_relation[0])
        return feature

    concept_phrases = []
    for i in range(len(parse_result.contents)-1):
        item = parse_result.contents[i]
        next_item = parse_result.contents[i+1]
        item_concept_phrases = []
        phrase_str = '|'.join([item.pos_tag, next_item.pos_tag])
        if phrase_str in phrase_strs:
            word_relations = get_word_relations(item.value)
            if len(word_relations) > 0:
                next_word_relations = get_word_relations(next_item.value)
                for word_relation in word_relations:
                    feature1 = create_feature(word_relation)
                    for next_word_relation in next_word_relations:
                        feature2 = create_feature(next_word_relation)
                        # concept_phrase = [feature1, feature2, item.value, next_item.value]
                        concept_phrase = [feature1, feature2]
                        item_concept_phrases.append(concept_phrase)
                    feature2 = {}
                    feature2['word'] = next_item.value
                    # item_concept_phrases.append([feature1, feature2, item.value, next_item.value])
                    item_concept_phrases.append([feature1, feature2])
        if i < len(parse_result.contents) - 2:
            item_concept_phrases3 = []
            next_next_item = parse_result.contents[i+2]
            phrase_str = '|'.join([item.pos_tag, next_item.pos_tag, next_next_item.pos_tag])
            if phrase_str in phrase_strs:
                next_next_word_relations = get_word_relations(next_next_item.value)
                for concept_phrase in item_concept_phrases:
                    for word_relation in next_next_word_relations:
                        feature3 = create_feature(word_relation)
                        # concept_phrase3 = concept_phrase + [feature3, next_next_item.value]
                        concept_phrase3 = concept_phrase + [feature3]
                        item_concept_phrases3.append(concept_phrase3)
                    feature3 = {}
                    feature3['word'] = next_next_item.value
                    # item_concept_phrases3.append(concept_phrase + [feature3, next_next_item.value])
                    item_concept_phrases3.append(concept_phrase + [feature3])
                item_concept_phrases += item_concept_phrases3
        concept_phrases += item_concept_phrases

    return concept_phrases


line = file.readline()
noun_id_dict = {}
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
            for concept_id in concept_ids:
                if concept_id[0] not in noun_id_dict:
                    noun_id_dict[concept_id[0]] = 1

    line = file.readline()

print(len(noun_id_dict))

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
