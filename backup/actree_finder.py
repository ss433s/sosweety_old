import ahocorasick
import time
import json

print(time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime()))
with open('./init_data/all_entities_uniq') as test_file:
    lines = test_file.readlines()
    actree = ahocorasick.Automaton()
    for line in lines:
        line = line.strip()
        actree.add_word(line, line)
    actree.make_automaton()

print(time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime()))

with open('./init_data/parse_file_total') as parse_file:
    with open('./init_data/used_entities_total', 'w') as used_entities_file:
        lines = parse_file.readlines()

        for i in range(len(lines)):
        # for i in range(5000):
            if i % 1000 == 0:
                print(i)
            line = lines[i].split('\t')
            pos_tags = json.loads(line[1].strip())
            sentence = []
            for i in range(len(pos_tags)):
                pos_tag = pos_tags[i]
                sentence.append(pos_tag[0])
            text = ''.join(sentence)
            rst = actree.iter(text)
            for actree_word in rst:
                used_entities_file.write(actree_word[1] + '\n')

print(time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime()))
