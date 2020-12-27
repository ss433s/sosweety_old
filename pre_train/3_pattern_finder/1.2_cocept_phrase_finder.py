##############
# 递推所有上层concept
##############
import os, sys
sys.path.append("..")
sys.path.append("../..")
from kb import Knowledge_base

KB = Knowledge_base()

# 当前路径和项目root路径， 可以根据需求改变../..
this_file_path = os.path.split(os.path.realpath(__file__))[0]
root_path = os.path.abspath(os.path.join(this_file_path, "../.."))

noun_id_dict = {}
noun_file_path = 'data/3_phrase_pattern/nouns'
noun_file_path = os.path.join(root_path, noun_file_path)
with open(noun_file_path) as noun_file:
    for line in noun_file.readlines():
        concept_id = int(line.strip())
        noun_id_dict[concept_id] = 1

print(len(noun_id_dict))

next_level_concept_id_set = set()
for concept_id in noun_id_dict:
    next_level_concept_ids = KB.get_concept_upper_relations(concept_id)
    for next_level_concept_id in next_level_concept_ids:
        next_level_concept_id_set.add(next_level_concept_id)
    noun_id_dict[concept_id] = next_level_concept_ids

dict_file_path = 'data/3_phrase_pattern/relation_dict'
dict_file_path = os.path.join(root_path, dict_file_path)
with open(dict_file_path, 'w') as dict_file:
    for concept_id in noun_id_dict:
        dict_file.write(str(concept_id) + '\t' + str(noun_id_dict[concept_id]) + '\n')
