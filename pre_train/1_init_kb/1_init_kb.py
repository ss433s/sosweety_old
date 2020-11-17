import json
import sys, os
sys.path.append("..")
# import pandas as pd
# import numpy as np
# from sParser import hanlp_parse
# from knowledgebase import Concept, Method

# 用于init kb的文件列表, 通常包括spo file和kb relation file
# 关于数据太大的问题，可以尝试取交集
# 或者只保留下一步需要用到的数据的方法
spo_prefix = '/data/spo_and_pattern'
spo_files = ['nsubj_pr_stat', 'dobj_pr_stat', 'amod_pr_stat']

kb_prefix = '/data/kb_relations'
kb_files = ['pedia_relation', 'pkubase', 'wiki_relation']

this_file_path = os.path.split(os.path.realpath(__file__))[0]
# 可以根据需求改变../..
root_path = os.path.abspath(os.path.join(os.getcwd(), "../.."))

concepts = []
methods = []
method_words = []
concept_dict = {}

with open('./init_data/final_entities') as test_file:
    lines = test_file.readlines()
    for i in range(len(lines)):
        line = lines[i].strip('\n')
        concept = Concept(i, line, [], [])
        concept_dict[line] = concept
        concepts.append(concept)


# 主|谓
with open('../data/datasets/nsubj_pr_stat') as nsubj_file:
    lines = nsubj_file.readlines()
    for i in range(len(lines)):
        if i % 50000 == 0:
            print(i)
        line = lines[i].strip().split('\t')
        words = line[0].split('|')
        subj = words[0]
        verb = words[1]
        if verb not in method_words:
            method_index = len(methods)
            method = Method(method_index, verb)
            method_words.append(verb)
            methods.append(method)
        else:
            method_index = method_words.index(verb)
        try:
            concept_dict[subj].methods.append(method_index)
        except Exception:
            continue


# 宾语 | 动词
# with open('../data/datasets/dobj_pr_stat') as dobj_file:
#     lines = dobj_file.readlines()
#     for i in range(len(lines)):
#         if i % 5000 == 0:
#             print(i)
#         line = lines[i].strip().split('\t')
#         words = line[0].split('|')
#         obj = words[0]
#         verb = words[1]
#         if verb not in method_words:
#             method_index = len(methods)
#             method = Method(method_index, verb)
#             method_words_array = np.append(method_words_array, verb)
#             methods.append(method)
#         if obj not in concept_words:
#             concept = Concept(len(concepts), obj, [], [])
#             concepts.append(concept)
#             concept_words_array = np.append(concept_words_array, obj)


# 形容词|名词
# with open('../data/datasets/amod_pr_stat') as amod_file:
#     lines = amod_file.readlines()
#     for i in range(len(lines)):
#         if i % 5000 == 0:
#             print(i)
#         line = lines[i].strip().split('\t')
#         words = line[0].split('|')
#         adj = words[0]
#         noun = words[1]

#         if noun not in concept_words:
#             concept = Concept(len(concepts), noun, [], [])
#             concepts.append(concept)
#             concept_words_array = np.append(concept_words_array, noun)


# 写入文件
update_list = [['Concept', concepts], ['Method', methods]]
for file_pre, file_list in update_list:
    file_name = '../data/fake_database/' + file_pre + '_table'
    # with open(file_name, 'r') as f:
    #     line1 = f.readline()
    with open(file_name, 'w') as f:
        heads = []
        for k, _ in vars(file_list[0]).items():
            heads.append(k)
        heads_str = '#' + '\t'.join(heads)
        f.write(heads_str + '\n')
        for i in file_list:
            value_list = []
            for k, v in vars(i).items():
                if v is not None:
                    if isinstance(v, str):
                        value_list.append(v)
                    else:
                        value_list.append(json.dumps(v, ensure_ascii=False))
                else:
                    value_list.append('-')
            f.write('\t'.join(value_list) + '\n')

with open('../data/fake_database/Word_table', 'w') as f:
    f.write('# word  concept_id  Type    freq   Confidence\n')
    for concept in concepts:
        tmp_list = [concept.word, concept.concept_id, 'concept', 0, 0.9]
        f.write(json.dumps(tmp_list, ensure_ascii=False) + '\n')
    for method in methods:
        tmp_list = [method.word, method.method_id, 'method', 0, 0.9]
        f.write(json.dumps(tmp_list, ensure_ascii=False) + '\n')


# # 导入辞海数据
# df = pd.read_csv('init_data/cihai.csv', header=None)
# # print(df.iloc[0, 2])
# # for i in range(len(df)):
# for i in range(1, 2):
#     text = df.iloc[i, 2]
#     text = text.split('<br>')
#     if len(text) > 1:
#         text = text[1]
#         print(text)
#         s = hanlp_parse(text)
#         print(s)
#     if i > 10:
#         break
