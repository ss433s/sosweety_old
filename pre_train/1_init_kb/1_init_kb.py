import os, sys
import sqlite3
import json

sys.path.append("..")
# import pandas as pd
# import numpy as np
# from sParser import hanlp_parse
# from knowledgebase import Concept, Method

# 数据库路径
db_path = 'data/knowledgebase/knowledgebase.db'

#########################################
# 用于init kb的文件列表, 通常包括spo file和kb relation file(有少量错误)
# 关于数据太大的问题，可以尝试取交集
# 或者只保留下一步需要用到的数据的方法
#########################################
spo_prefix = 'data/spo_and_pattern'
spo_files = ['nsubj_pr_stat', 'dobj_pr_stat', 'amod_pr_stat']
# spo_files = ['nsubj_test', 'dobj_test']

kb_prefix = 'data/kb_relations'
kb_files = ['pedia_relation', 'pkubase', 'wiki_relation']
# kb_files = ['sql_test']

# 百度信息抽取比赛实体列表
baidu_ie_entity_file = '/data/corpus/baidu_ie_competition/known_entities'

# 当前路径和项目root路径
this_file_path = os.path.split(os.path.realpath(__file__))[0]
# 可以根据需求改变../..
root_path = os.path.abspath(os.path.join(this_file_path, "../.."))

# concept_words = {}
# method_words = {}

concept_set = set()
method_set = set()

# 读取spo file中的concept和method
for spo_file in spo_files:
    spo_file_path = os.path.join(root_path, spo_prefix, spo_file)
    with open(spo_file_path) as spo_file_handler:
        line = spo_file_handler.readline()
        while line:
            line_list = line.strip().split('\t')
            words = line_list[0].split('|')

            # 确定concept和method， 未来可能变动很大
            if 'amod' in spo_file:
                concept_word = words[1]
            else:
                concept_word = words[0]
            if 'nsubj' in spo_file or 'dobj' in spo_file:
                method_word = words[1]

            # method_words[method_word] = 1
            # concept_words[concept_word] = 1
            concept_set.add(concept_word)
            method_set.add(method_word)

            line = spo_file_handler.readline()

# 读取kb file中的concept
for kb_file in kb_files:
    kb_file_path = os.path.join(root_path, kb_prefix, kb_file)
    with open(kb_file_path) as kb_file_handler:
        line = kb_file_handler.readline()
        while line:
            words = line.strip().split('\t')
            concept_set.add(words[0])
            if len(words) > 1:
                concept_set.add(words[1])

            line = kb_file_handler.readline()

print(len(concept_set))


###################
# 初始化数据库
###################
kb_db_conn = sqlite3.connect(os.path.join(root_path, db_path))
print("Open database successfully")

cur = kb_db_conn.cursor()

create_concept_tbl_sql = '''CREATE TABLE Concept_tbl
       (Concept_id INT PRIMARY KEY     NOT NULL,
       Word           TEXT    NOT NULL,
       Methods        TEXT,
       Properties     TEXT);'''

create_method_tbl_sql = '''CREATE TABLE Method_tbl
       (Method_id INT PRIMARY KEY     NOT NULL,
       Word           TEXT    NOT NULL,
       Objects        TEXT,
       Code        TEXT);'''

create_fact_tbl_sql = '''CREATE TABLE Fact_tbl
       (Fact_id INT PRIMARY KEY     NOT NULL,
       Concept1       INT    NOT NULL,
       Restriction1   TEXT    NOT NULL,
       Concept2       INT    NOT NULL,
       Restriction2   TEXT    NOT NULL,
       Relation       INT    NOT NULL,
       Relation_restriction   TEXT    NOT NULL,
       Time       TEXT,
       Location   TEXT,
       Confidence  REAL       NOT NULL);'''

create_word_tbl_sql = '''CREATE TABLE Word_tbl
       (ID INTEGER PRIMARY KEY AUTOINCREMENT    NOT NULL,
       Word           TEXT    NOT NULL,
       Item_id        TEXT    NOT NULL,
       Type     TEXT    NOT NULL,
       Frequece  INT    NOT NULL,
       Confidence REAL NOT NULL);'''

create_concept_relation_tbl_sql = '''CREATE TABLE Concept_relation_tbl
       (ID INT PRIMARY KEY     NOT NULL,
       Concept1       INT    NOT NULL,
       Concept2       INT    NOT NULL,
       Relation_type  INT    NOT NULL);'''

cur.execute(create_concept_tbl_sql)
cur.execute(create_method_tbl_sql)
cur.execute(create_fact_tbl_sql)
cur.execute(create_word_tbl_sql)
cur.execute(create_concept_relation_tbl_sql)

kb_db_conn.commit()
print("Create database successfully")


###################
# 导入数据库
###################

# 导入concept和method
concept_word2id_dict = {}
for index, concept in enumerate(concept_set):
    if index % 1000000 == 0:
        print('create %s concepts' % index)
    concept_word2id_dict[concept] = index
    insert_concept_sql = "INSERT INTO Concept_tbl (Concept_id, Word) \
        Values (?, ?)"
    insert_word_sql = "INSERT INTO Word_tbl (Word, Item_id, Type, Frequece, Confidence) \
        Values (?, ?, 'concept', 0, 0.9)"
    cur.execute(insert_concept_sql, (index, concept))
    cur.execute(insert_word_sql, (concept, index))
del concept_set

method_word2id_dict = {}
for index, method in enumerate(method_set):
    if index % 10000000 == 0:
        print('create %s methods' % index)
    method_word2id_dict[method] = index
    insert_method_sql = "INSERT INTO Method_tbl (Method_id, Word) \
        Values (?, ?)"
    insert_word_sql = "INSERT INTO Word_tbl (Word, Item_id, Type, Frequece, Confidence) \
        Values (?, ?, 'method', 0, 0.9)"
    cur.execute(insert_method_sql, (index, method))
    cur.execute(insert_word_sql, (method, index))
del method_set

kb_db_conn.commit()


# 建立index
create_index_sql = 'CREATE INDEX Word_index ON Method_tbl (Word);'
cur.execute(create_index_sql)
create_index_sql = 'CREATE INDEX Word_index ON Concept_tbl (Word);'
cur.execute(create_index_sql)
create_index_sql = 'CREATE INDEX Word_index ON Word_tbl (Word);'
cur.execute(create_index_sql)
create_index_sql = 'CREATE INDEX Word_index ON Word_tbl (Item_id);'
cur.execute(create_index_sql)
kb_db_conn.commit()


# 根据method 更新关联的concept
# 如果spo文件有重复，会导致部分内容重复 tofix

for spo_file in spo_files:
    spo_file_path = os.path.join(root_path, spo_prefix, spo_file)

    # 主谓关系提取concept的methods列表
    if 'nsubj' in spo_file:
        concept_method_dict = {}
        with open(spo_file_path) as spo_file_handler:
            line = spo_file_handler.readline()
            while line:
                line_list = line.strip().split('\t')
                words = line_list[0].split('|')

                subj = words[0]
                method = words[1]
                method_id = method_word2id_dict[method]
                if subj in concept_method_dict:
                    concept_method_dict[subj].append(method_id)
                else:
                    concept_method_dict[subj] = [method_id]
                line = spo_file_handler.readline()

            count = 0
            for subj in concept_method_dict:
                concept_id = concept_word2id_dict[subj]
                count += 1
                if count % 10000 == 0:
                    print('update %s spo' % count)
                update_sql = "UPDATE Concept_tbl set Methods = ? where Concept_id=?"
                cur.execute(update_sql, (json.dumps(concept_method_dict[subj]), concept_id))
            kb_db_conn.commit()

    # 动宾关系提取methods的obj列表
    if 'dobj' in spo_file:
        method_concept_dict = {}
        with open(spo_file_path) as spo_file_handler:
            line = spo_file_handler.readline()
            while line:
                line_list = line.strip().split('\t')
                words = line_list[0].split('|')

                obj = words[0]
                method = words[1]
                obj_id = concept_word2id_dict[obj]
                if method in method_concept_dict:
                    method_concept_dict[method].append(obj_id)
                else:
                    method_concept_dict[method] = [obj_id]
                line = spo_file_handler.readline()

            count = 0
            for method in method_concept_dict:
                count += 1
                if count % 100 == 0:
                    print('update %s spo' % count)
                update_sql = "UPDATE Method_tbl set Objects = ? where Word= ?"
                # print(update_sql)
                cur.execute(update_sql, (json.dumps(method_concept_dict[method]), method))
            kb_db_conn.commit()

kb_db_conn.close()

'''
# 写入文件
with open('../data/fake_database/Word_table', 'w') as f:
    f.write('# word  concept_id  Type    freq   Confidence\n')
    for concept in concepts:
        tmp_list = [concept.word, concept.concept_id, 'concept', 0, 0.9]
        f.write(json.dumps(tmp_list, ensure_ascii=False) + '\n')
    for method in methods:
        tmp_list = [method.word, method.method_id, 'method', 0, 0.9]
        f.write(json.dumps(tmp_list, ensure_ascii=False) + '\n')
'''
