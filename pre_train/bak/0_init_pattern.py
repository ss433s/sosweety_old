import json
# import pandas as pd
# from stanfordcorenlp import StanfordCoreNLP
# nlp = StanfordCoreNLP(r'/mnt/f/ubuntu/support/stanfordcorenlp/stanford-corenlp-full-2018-10-05/', lang='zh')
from sParser import sParser, Pre_sub_sentence, Word, Parse_result, check_special_phrase, stanford_simplify
from knowledgebase import Knowledge_base
import time

KB = Knowledge_base()
parser = sParser(KB, mode='learning')


# 专门处理百度信息抽取预处理好的语料
with open('init_data/parse_file_total') as parse_file:
    with open('init_data/unsolved_ss', 'w') as unsolved_file:

        # 计时开始
        print(time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime()))

        lines = parse_file.readlines()

        for i in range(len(lines)):
            print(i)
            if i % 1000 == 0:
                print('parsed %s sentence, total ~170000' % i)
            if i == 4:
                print('hah')
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
            # print(ss)

            for sub_sentence in ss:
                all_results = []
                contents = []
                for word_value, pos_tag in sub_sentence:
                    word = Word(word_value, pos_tag)
                    contents.append(word)
                parse_result = Parse_result(contents)
                check_special_phrase(parse_result, all_results)
                if all_results == []:
                    # print(sub_sentence)
                    unsolved_file.write(json.dumps(sub_sentence, ensure_ascii=False) + '\n')
                # else:
                #     print(all_results)

            if i == 100:
                print(time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime()))
                break
