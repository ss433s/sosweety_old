import os
import sqlite3

# from kb_class import Concept, Method, Fact


# 当前路径和项目root路径， 可以根据需求改变../..
this_file_path = os.path.split(os.path.realpath(__file__))[0]
root_path = os.path.abspath(os.path.join(this_file_path, ".."))

# 数据库路径 诡异的bug 不能在vscode的目录里
root_path_up = os.path.abspath(os.path.join(root_path, ".."))
db_path = 'data/knowledgebase/knowledgebase.db'
new_db_path = os.path.join(root_path_up, db_path)

kb_db_conn = sqlite3.connect(new_db_path)
print("Opened database successfully")
cur = kb_db_conn.cursor()


class Knowledge_base(object):

    # 查询concept word
    def get_concept_word(self, concept_id):
        select_sql = "SELECT Word FROM Concept_tbl where Concept_id=?"
        result = cur.execute(select_sql, (str(concept_id))).fetchall()
        if len(result) == 0:
            return None
        else:
            word = result[0][0]
            return word

    # 查询一个concept id 的上位concept
    # 仅限一度查询
    def get_concept_upper_relations(self, concept_id):
        select_sql = "SELECT Concept2 FROM Concept_relation_tbl where Concept1=?"
        result = cur.execute(select_sql, [str(concept_id)]).fetchall()
        if len(result) == 0:
            return None
        else:
            upper_relations = result
            return upper_relations

    # 添加词
    #
    def add_word(self, word, word_type):
        select_sql = "SELECT Item_id FROM Word_tbl where Word=? and Type = ?"
        result = cur.execute(select_sql, (word, word_type)).fetchall()
        if len(result) == 0:
            if word_type == 0:
                insert_concept_sql = "INSERT INTO Concept_tbl (Word) Values (?)"
                insert_concept_result = cur.execute(insert_concept_sql, [word])
                concept_id = insert_concept_result.lastrowid
                insert_word_sql = "INSERT INTO Word_tbl (Word, Item_id, Type, Frequece, Confidence) \
                    Values (?, ?, 0, 0, 0.9)"
                cur.execute(insert_word_sql, [word, concept_id])
                kb_db_conn.commit()
                return concept_id

            elif word_type == 1:
                insert_method_sql = "INSERT INTO Method_tbl (Word) Values (?)"
                insert_method_result = cur.execute(insert_method_sql, [word])
                method_id = insert_method_result.lastrowid
                insert_word_sql = "INSERT INTO Word_tbl (Word, Item_id, Type, Frequece, Confidence) \
                    Values (?, ?, 1, 0, 0.9)"
                cur.execute(insert_word_sql, [word, method_id])
                kb_db_conn.commit()
                return method_id

            else:
                raise Exception('No such word type')
        else:
            return -1

    # 查询一个词的所有对应id
    # 参数为 word， word_type为可选，可以知道只查询指定类型的word对应的id
    # 返回结果为【item_id, word_type】的list
    def get_word_ids(self, word, word_type=None):

        final_list = []
        if word_type is not None:
            select_sql = "SELECT Item_id FROM Word_tbl where Word=? and Type=?"
            result = cur.execute(select_sql, (word, word_type)).fetchall()
            for item in result:
                final_list.append([item[0], word_type])
        else:
            select_sql = "SELECT Item_id, Type FROM Word_tbl where Word=?"
            result = cur.execute(select_sql, [word]).fetchall()
            for item in result:
                final_list.append([item[0], item[1]])

        return final_list


'''
    # 判定一个词语是否属于某种concept，不递归，多义词返回concept_id
    def word_belong_to_concept(self, word, concept_id):
        result = []
        if word in word2id_dict:
            word_ids = word2id_dict[word]
            for concept1_id, word1_type, freq, confidence in word_ids:
                if word1_type == 'concept' and concept1_id in concept_relations:
                    concept2s = concept_relations[concept1_id]
                    for concept2_id, word2_type, _, _ in concept2s:
                        if word2_type == 'concept' and concept2_id == concept_id:
                            result.append([concept1_id, freq, confidence])
        return result

    # 检查所有词表,返回一段文字的匹配词列表
    def checkout_words(self, text):
        word_set = set()
        matched_words = []
        for word in word2id_dict:
            word_set.add(word)

        actree = ahocorasick.Automaton()
        for word in word_set:
            actree.add_word(word, word)
        actree.make_automaton()
        rst = actree.iter(text)
        for actree_word in rst:
            matched_words.append(actree_word[1])
        return matched_words

'''


class K_point(object):
    # type 包括 concept， method， fact， word等
    # content 格式为字典
    # content 包括id的话，为更新属性, 不包含为新增
    # fact 需先处理concept入库问题  必须先传入concept 再生出fact 然后传入fact
    def __init__(self, k_type, content):
        self.k_type = k_type
        self.content = content


# test
if __name__ == '__main__':
    KB = Knowledge_base()
    rst = KB.get_concept_word(0)
    rst = KB.get_concept_upper_relations(0)
    # rst = KB.add_word('asasadadsa', 1)
    rst = KB.get_word_ids('人口')
    rst = KB.word_belong_to_concept("北京大学", 0)
    k_point = K_point('concept', {'concept_id': 2, 'properties': [5]})
    # k_point = K_point('concept', {'word': '南京', 'methods': [0]})
    # fact = Fact(1)
    # k_point = K_point('fact', {'fact': fact})
    KB.merge([k_point])
    # print(facts)
    # print(rst)
