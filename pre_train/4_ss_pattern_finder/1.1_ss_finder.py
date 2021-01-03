import os, sys
import json
import time
sys.path.append("..")
sys.path.append("../..")
from sParser.parser_class import Word, Parse_result
from sParser.sParser import fast_check_parse_result
from utils.utils import stanford_simplify


# 当前路径和项目root路径， 可以根据需求改变../..
this_file_path = os.path.split(os.path.realpath(__file__))[0]
root_path = os.path.abspath(os.path.join(this_file_path, "../.."))

# 打开语料文件
# 此处为预处理好的百度信息抽取比赛语料
file_path = 'data/corpus/baidu_ie_competition/parse_file_total'
file_path = os.path.join(root_path, file_path)
file = open(file_path)

ss_pattern_dir = 'data/4_ss_pattern'
ss_pattern_dir = os.path.join(root_path, ss_pattern_dir)
if not os.path.exists(ss_pattern_dir):
    os.mkdir(ss_pattern_dir)
ss_pattern_file_path = 'ss_patterns_raw'
ss_pattern_file_path = os.path.join(ss_pattern_dir, ss_pattern_file_path)
ss_pattern_file = open(ss_pattern_file_path, 'w')


print(time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime()))


def tuples2parse_result(tuples):
    content = []
    for word in tuples:
        tmp_word = Word(word[0], word[1])
        content.append(tmp_word)
    parse_result = Parse_result(content)
    return parse_result


def checkout_ss_pattern(parse_result):
    new_parse_result = fast_check_parse_result(parse_result)
    result_str = []
    for item in new_parse_result.contents:
        if isinstance(item, Word):
            result_str.append(item.value)
        else:
            result_str.append(item.pos_tag)
    ss_pattern_file.write('|'.join(result_str) + '\n')
    return


lines = file.readlines()
for i in range(len(lines)):
    if i % 3000 == 0:
        print('parsed %s sentence, total ~170000' % i)
    # if i > 1000:
    #     break

    line = lines[i].split('\t')
    parse_str = line[0]
    pos_tags = json.loads(line[1].strip())
    pos_tags = stanford_simplify(pos_tags)

    tmp_stamp = 0
    for i in range(len(pos_tags)):
        pos_tag = pos_tags[i]
        if pos_tag[0] in ['。', '！', '？', '?', '，', ',', ';', '；']:
            ss_parse_result = tuples2parse_result(pos_tags[tmp_stamp: i])
            checkout_ss_pattern(ss_parse_result)
            tmp_stamp = i + 1
    if tmp_stamp < len(pos_tags):
        ss_parse_result = tuples2parse_result(pos_tags[tmp_stamp: len(pos_tags)])
        checkout_ss_pattern(ss_parse_result)

ss_pattern_file.close()
print(time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime()))
