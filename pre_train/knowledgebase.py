import sys
sys.path.append("..")


###################
# 定义和读取知识库
###################
class Concept(object):
    def __init__(self, concept_id, word, methods, properties):
        self.concept_id = concept_id
        self.word = word
        self.methods = methods
        self.properties = properties


# 读取concept表 concepts为字典 key为concept_id 值是Concept类
with open('./fake_database/Concept_table') as concept_table_file:
    concepts = {}
    lines = concept_table_file.readlines()
    del(lines[0])
    for line in lines:
        line = line.strip().split()
        if len(line) > 1:
            concept = Concept(int(line[0]), line[1], line[2], line[3])
            concepts[concept.concept_id] = concept

# 读取synonym 表（实体链接表） 构建word2concept dict （method待定）
with open('./fake_database/Synonym_table') as synonym_table_file:
    word2concept_dict = {}
    lines = synonym_table_file.readlines()
    del(lines[0])
    for line in lines:
        line = line.strip().split()
        if len(line) > 1:
            if line[3] == 'concept':
                if line[0] in word2concept_dict:
                    word2concept_dict[line[0]].append([int(line[1]), float(line[4])])
                else:
                    word2concept_dict[line[0]] = [[int(line[1]), float(line[4])]]
            elif line[3] == 'method':
                pass


# 读取concept relation 表 构建concept_relation 字典  key为concept1_id 值为 [concept2_id, type]
with open('./fake_database/Concept_relation_table') as concept_relation_table_file:
    concept_relations = {}
    lines = concept_relation_table_file.readlines()
    del(lines[0])
    for line in lines:
        line = line.strip().split()
        if len(line) > 1:
            if line[0] in concept_relations:
                concept_relations[int(line[0])].append([int(line[1]), int(line[2])])
            else:
                concept_relations[int(line[0])] = [[int(line[1]), int(line[2])]]


class Knowledge_base(object):
    # def __init__(self):

    # 判定一个词语是否属于某种concept，不递归，多义词返回concept_id
    def word_belong_to_concept(self, word, concept_id):
        result = []
        if word in word2concept_dict:
            concept_ids = word2concept_dict[word]
            for concept1_id, confidence in concept_ids:
                if concept1_id in concept_relations:
                    concept2s = concept_relations[concept1_id]
                    for concept2_id, _ in concept2s:
                        if concept2_id == concept_id:
                            result.append([concept1_id, confidence])
        return result



# test
if __name__ == '__main__':
    KB = Knowledge_base()
    rst = KB.word_belong_to_concept("北京大学", 0)
    print(rst)
