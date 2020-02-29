import json
# import pandas as pd
# from stanfordcorenlp import StanfordCoreNLP
# nlp = StanfordCoreNLP(r'/mnt/f/ubuntu/support/stanfordcorenlp/stanford-corenlp-full-2018-10-05/', lang='zh')
from sParser import sParser, Pre_sub_sentence, Word, Parse_result, check_special_phrase, stanford_simplify
from knowledgebase import Knowledge_base

KB = Knowledge_base()
parser = sParser(KB, mode='learning')


# 专门处理百度信息抽取预处理好的语料
with open('init_data/parse_file_total') as parse_file:
    lines = parse_file.readlines()

    for i in range(len(lines)):
        line = lines[i].split('\t')
        parse_str = line[0]
        pos_tags = json.loads(line[1].strip())
        pos_tags = stanford_simplify(pos_tags)

        tmp_stamp = 0
        ss = []
        for i in range(len(pos_tags)):
            pos_tag = pos_tags[i]
            if pos_tag[0] in ['。', '！', '？', '?', '，', ',', ';', '；']:
                ss.append(pos_tags[tmp_stamp: i])
                tmp_stamp = i
        if tmp_stamp < len(pos_tags):
            ss.append(pos_tags[tmp_stamp: len(pos_tags)])
        print(ss)

        for sub_sentence in ss:
            all_results = []
            contents = []
            for word_value, pos_tag in sub_sentence:
                word = Word(word_value, pos_tag)
                contents.append(word)
            parse_result = Parse_result(contents)
            check_special_phrase(parse_result, all_results)
            if all_results == []:
                print(sub_sentence)
            else:
                print(all_results)

        break
