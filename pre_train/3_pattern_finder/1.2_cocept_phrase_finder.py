##############
# 递推所有上层concept
##############
import os, sys
sys.path.append("..")
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
# count = 0
for concept_id in noun_id_set:
    # count += 1
    # if count % 10000 == 0:
    #     print('reformed %s concepts' % count)
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

dict_file_path = 'data/3_phrase_pattern/relation_dict'
dict_file_path = os.path.join(root_path, dict_file_path)
with open(dict_file_path, 'w') as dict_file:
    for concept_id in final_dict:
        dict_file.write(str(concept_id) + '\t' + str(final_dict[concept_id]) + '\n')
