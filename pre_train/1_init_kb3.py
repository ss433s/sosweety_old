import json
from knowledgebase import word2id_dict, concepts, Concept

with open('./init_data/card_relation_uniq') as test_file:
    concept_relations_file = open('../data/fake_database/Concept_relation_table', 'a')
    concept_file = open('../data/fake_database/Concept_table', 'a')
    word_file = open('../data/fake_database/Word_table', 'a')
    lines = test_file.readlines()
    for i in range(len(lines)):
        if i % 1000 == 0:
            print(i)

        line = lines[i].strip().split('\t')

        if line[0] in word2id_dict:
            if line[1] in word2id_dict:
                concept_relations_file.write(str(word2id_dict[line[0]][0][0]) + '\t' + str(word2id_dict[line[1]][0][0]) + '\t0\n')
            else:
                number = len(concepts)
                concept = Concept(number, line[1], [], [])
                concepts[number] = concept
                word2id_dict[line[1]] = [[number, 'concept', 0, 0.9]]

                concept_file.write(str(number) + '\t' + line[1] + '\t[]\t[]\n')
                concept_relations_file.write(str(word2id_dict[line[0]][0][0]) + '\t' + str(number) + '\t0\n')
                tmp_json = [line[1], number, 'concept', 0, 0.9]
                word_file.write(json.dumps(tmp_json, ensure_ascii=False) + '\n')

    word_file.close()
    concept_file.close()
    concept_relations_file.close()

with open('../data/fake_database/Concept_relation_table') as f:
    lines = f.readlines()

# todo 优化为set 速度太慢
with open('../data/fake_database/Concept_relation_table', 'w') as f:
    new_lines = []
    for line in lines:
        if line not in new_lines:
            f.write(line)
            new_lines.append(line)
