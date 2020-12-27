##############
# 第一步 找出所有在kb的NN
##############

import os


# 当前路径和项目root路径， 可以根据需求改变../..
this_file_path = os.path.split(os.path.realpath(__file__))[0]
root_path = os.path.abspath(os.path.join(this_file_path, "../.."))


concept_phrases = {}
concept_phrase_file_path = 'data/3_phrase_pattern/concept_phrases'
concept_phrase_file_path = os.path.join(root_path, concept_phrase_file_path)

stat_file_path = 'data/3_phrase_pattern/concept_phrase_stat'
stat_file_path = os.path.join(root_path, stat_file_path)

count = 0
with open(concept_phrase_file_path) as concept_phrase_file:
    line = concept_phrase_file.readline()
    while line:
        count += 1
        if count % 500000 == 0:
            print('count %s phrases' % count)
        line = line.strip()
        if line in concept_phrases:
            concept_phrases[line] += 1
        else:
            concept_phrases[line] = 1

        line = concept_phrase_file.readline()

print(len(concept_phrases))

with open(stat_file_path, 'w') as stat_file:
    for key, value in concept_phrases.items():
        stat_file.write(key + '\t' + str(value) + '\n')
