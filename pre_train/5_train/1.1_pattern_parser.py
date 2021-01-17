import os, sys
import json, time
sys.path.append("..")
sys.path.append("../..")
# 当前路径和项目root路径， 可以根据需求改变../..
this_file_path = os.path.split(os.path.realpath(__file__))[0]
root_path = os.path.abspath(os.path.join(this_file_path, "../.."))
sys.path.append(root_path)
from sParser.parser_class import Word, Parse_result
from sParser.sParser import fast_check_phrase, logic_check
from utils.utils import stanford_simplify


# 打开语料文件
file = open(sys.argv[1])

unsolved_file_path = sys.argv[1] + '_unsolved_ss'
unsolved_file = open(unsolved_file_path, 'w')

solved_file_path = sys.argv[1] + '_solved_ss'
solved_file = open(solved_file_path, 'w')

count = 0
total_ss = 0
parsed_ss = 0

line = file.readline()
while line:

    count += 1
    if count % 2000 == 0:
        print(time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime()))
        print('parsed %s sentence, total ~170000' % count)
        print('total ss is %s, parsed is %s' % (total_ss, parsed_ss))

    line = line.split('\t')
    pos_tags = json.loads(line[1].strip())
    pos_tags = stanford_simplify(pos_tags)

    tmp_stamp = 0
    ss = []
    for i in range(len(pos_tags)):
        pos_tag = pos_tags[i]
        if pos_tag[0] in ['。', '！', '？', '?', '，', ',', ';', '；']:
            ss.append(pos_tags[tmp_stamp: i])
            tmp_stamp = i + 1
    if tmp_stamp < len(pos_tags):
        ss.append(pos_tags[tmp_stamp: len(pos_tags)])
    # print(ss)

    for sub_sentence_pos_tags in ss:
        total_ss += 1

        contents = []
        for word_value, pos_tag in sub_sentence_pos_tags:
            word = Word(word_value, pos_tag)
            contents.append(word)
        parse_result = Parse_result(contents)
        all_results = fast_check_phrase(parse_result)
        if all_results == []:
            unsolved_file.write(json.dumps(sub_sentence_pos_tags, ensure_ascii=False) + '\t' + 'no_parse_result\n')
        else:
            # ##################
            # # with logic check
            # ##################
            # logic_check_result = logic_check(all_results[0])
            # # if len(logic_check_result) > 0 and all(logic_check_result):
            # if all(logic_check_result):
            #     # print(all_results[0])
            #     parsed_ss += 1
            #     solved_file.write(json.dumps(sub_sentence_pos_tags, ensure_ascii=False) + '\n')
            # else:
            #     unsolved_file.write(json.dumps(sub_sentence_pos_tags, ensure_ascii=False) + '\t' + 'logic_mistake\n')

            ##################
            # without logic check
            ##################
            solved_file.write(json.dumps(sub_sentence_pos_tags, ensure_ascii=False) + '\n')

    line = file.readline()

solved_file.close()
unsolved_file.close()
