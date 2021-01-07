##############
# 第一步 找出所有在kb的NN
##############

import os

# 当前路径和项目root路径， 可以根据需求改变../..
this_file_path = os.path.split(os.path.realpath(__file__))[0]
root_path = os.path.abspath(os.path.join(this_file_path, "../.."))

stat_file_path = 'data/3_phrase_pattern/concept_phrase_stat'
stat_file_path = os.path.join(root_path, stat_file_path)
concept_phrase_file_path = 'data/3_phrase_pattern/concept_phrases'
concept_phrase_file_path = os.path.join(root_path, concept_phrase_file_path)

count = 0
c10 = 0
c100 = 0
key_example_dict = {}
key_value_dict = {}
with open(stat_file_path) as stat_file:
    line = stat_file.readline()
    while line:
        count += 1
        if count % 500000 == 0:
            print('count %s phrases' % count)
        line = line.strip().split('\t')
        if int(line[1]) > 10:
            c10 += 1
            key_example_dict[line[0]] = []
            key_value_dict[line[0]] = int(line[1])
        if int(line[1]) > 100:
            c100 += 1

        line = stat_file.readline()

print(c10, c100)

count = 0
with open(concept_phrase_file_path) as concept_phrase_file:
    line = concept_phrase_file.readline()
    while line:
        count += 1
        if count % 500000 == 0:
            print('count %s phrases' % count)
        line = line.strip().split('\t')
        concept_phrase = line[0]
        concept_example = line[1]
        if concept_phrase in key_value_dict and concept_example not in key_example_dict[concept_phrase] and len(key_example_dict[concept_phrase]) < 5:
            key_example_dict[concept_phrase].append(concept_example)

        line = concept_phrase_file.readline()

ordered_stat_file_path = 'data/3_phrase_pattern/ordered_concept_phrase_stat.csv'
ordered_stat_file_path = os.path.join(root_path, ordered_stat_file_path)

d_order = sorted(key_value_dict.items(), key=lambda x: x[1], reverse=True)
with open(ordered_stat_file_path, 'w') as ordered_stat_file:
    for key, value in d_order:
        ordered_stat_file.write(key + '\t' + str(value) + '\t' + str(key_example_dict[key]) + '\n')
