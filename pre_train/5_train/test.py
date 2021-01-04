import os, sys
import json, time
sys.path.append("..")
sys.path.append("../..")
from sParser.parser_class import Word, Parse_result
from sParser.sParser import fast_check_phrase, logic_check
from utils.utils import stanford_simplify


# 当前路径和项目root路径， 可以根据需求改变../..
this_file_path = os.path.split(os.path.realpath(__file__))[0]
root_path = os.path.abspath(os.path.join(this_file_path, "../.."))

# 打开语料文件
# 此处为预处理好的百度信息抽取比赛语料


example = '[["作者", "NN"], ["受到", "VV"], ["0.01%", "NN"]]'

pos_tags = json.loads(example)
pos_tags = stanford_simplify(pos_tags)

contents = []
for word_value, pos_tag in pos_tags:
    word = Word(word_value, pos_tag)
    contents.append(word)
parse_result = Parse_result(contents)

all_results = fast_check_phrase(parse_result)
if all_results == []:
    pass
else:
    logic_check_result = logic_check(all_results[0])
    if len(logic_check_result) > 0 and all(logic_check_result):
        print(all_results[0])
