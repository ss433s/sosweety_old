import os, sys
import json

# 当前路径和项目root路径， 可以根据需求改变../..
this_file_path = os.path.split(os.path.realpath(__file__))[0]
root_path = this_file_path

sys.path.append(root_path)
from sParser.parser_class import Word, Parse_result
from sParser.sParser import fast_check_phrase, logic_check, known_entity_check
from utils.utils import stanford_simplify


example = '[["作者", "NN"], ["受到", "VV"], ["影响", "NN"]]'
example = '[["集团", "NN"], ["下属", "VV"], ["31", "CD"], ["家", "M"], ["独资", "JJ"], ["子公司", "NN"]]'
example = '[["中华", "NN"], ["中华", "NN"], ["人民", "VV"], ["共和国", "CD"], ["万万岁", "CD"]]'

pos_tags = json.loads(example)
pos_tags = stanford_simplify(pos_tags)

contents = []
for word_value, pos_tag in pos_tags:
    word = Word(word_value, pos_tag)
    contents.append(word)
parse_result = Parse_result(contents)

# fast check
all_results = fast_check_phrase(parse_result)
if all_results == []:
    pass
else:
    logic_check_result = logic_check(all_results[0])
    if len(logic_check_result) > 0 and all(logic_check_result):
        print(all_results[0])

# fast check
all_results = known_entity_check(parse_result)
if all_results == []:
    pass
else:
    print(all_results[0])
