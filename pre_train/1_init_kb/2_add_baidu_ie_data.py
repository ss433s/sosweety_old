import os, sys
import json
import sqlite3
sys.path.append("..")


# 当前路径和项目root路径， 可以根据需求改变../..
this_file_path = os.path.split(os.path.realpath(__file__))[0]
root_path = os.path.abspath(os.path.join(this_file_path, "../.."))

# 数据库路径 诡异的bug 不能在vscode的目录里
root_path_up = os.path.abspath(os.path.join(root_path, ".."))
db_path = 'data/knowledgebase/knowledgebase.db'
new_db_path = os.path.join(root_path_up, db_path)

kb_db_conn = sqlite3.connect(new_db_path)
print("Opened database successfully")
cur = kb_db_conn.cursor()


def get_word_id(word):
    select_sql = "SELECT Item_id FROM Word_tbl where Word=? and type=0"
    result = cur.execute(select_sql, [word]).fetchall()
    if len(result) == 0:
        insert_concept_sql = "INSERT INTO Concept_tbl (Word) Values (?)"
        insert_concept_result = cur.execute(insert_concept_sql, [word])
        concept_id = insert_concept_result.lastrowid
        insert_word_sql = "INSERT INTO Word_tbl (Word, Item_id, Type, Frequece, Confidence) \
            Values (?, ?, 0, 0, 0.9)"
        cur.execute(insert_word_sql, [word, concept_id])
        return concept_id
    else:
        concept_id = result[0][0]
        return concept_id


# 百度信息抽取比赛实体列表
baidu_ie_entity_file = 'data/corpus/baidu_ie_competition/known_entities'
baidu_ie_corpus_file = 'data/corpus/baidu_ie_competition/train_data.json'
baidu_ie_corpus_file = os.path.join(root_path, baidu_ie_corpus_file)

# 导入上下位关系
# todo 导入fact
with open(baidu_ie_corpus_file) as train_file:

    line = train_file.readline()
    count = 0
    while line:
        count += 1
        if count % 10000 == 0:
            print('insert %s spo' % count)
        data = json.loads(line)
        for spo in data['spo_list']:
            object_id = get_word_id(spo['object'])
            object_type_id = get_word_id(spo['object_type'])
            subject_id = get_word_id(spo['subject'])
            subject_type_id = get_word_id(spo['subject_type'])
            insert_concept_sql = "INSERT INTO Concept_relation_tbl (Concept1, Concept2, Relation_type) \
                                    Values (?, ?, 0)"
            cur.execute(insert_concept_sql, (object_id, object_type_id))
            cur.execute(insert_concept_sql, (subject_id, subject_type_id))
        line = train_file.readline()

    kb_db_conn.commit()
