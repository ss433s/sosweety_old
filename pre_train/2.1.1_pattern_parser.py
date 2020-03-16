import json, time, sys
# import pandas as pd
# from stanfordcorenlp import StanfordCoreNLP
# nlp = StanfordCoreNLP(r'/mnt/f/ubuntu/support/stanfordcorenlp/stanford-corenlp-full-2018-10-05/', lang='zh')
from sParser import Word, Parse_result, check_special_phrase, stanford_simplify


# 专门处理百度信息抽取预处理好的语料
with open(sys.argv[1]) as parse_file:
    with open(sys.argv[1] + '_unsolve_ss', 'w') as unsolved_file:
        lines = parse_file.readlines()

        total_ss = 0
        parsed_ss = 0
        for i in range(len(lines)):
        # for i in range(1):
            if i % 200 == 0:
                print(time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime()))
                print('parsed %s sentence, total ~170000' % i)
                print('total ss is %s, parsed is %s' % (total_ss, parsed_ss))
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
                    tmp_stamp = i + 1
            if tmp_stamp < len(pos_tags):
                ss.append(pos_tags[tmp_stamp: len(pos_tags)])
            # print(ss)

            for sub_sentence in ss:
                total_ss += 1

                contents = []
                for word_value, pos_tag in sub_sentence:
                    word = Word(word_value, pos_tag)
                    contents.append(word)
                parse_result = Parse_result(contents)

                all_results = []
                total_count = []
                start_time = time.time()
                check_special_phrase(parse_result, all_results, total_count=total_count, start_time=start_time)
                # print(len(total_count))
                # print(sum(total_count))
                # print(time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime()))
                if all_results == []:
                    unsolved_file.write(json.dumps(sub_sentence, ensure_ascii=False) + '\n')
                else:
                    parsed_ss += 1
