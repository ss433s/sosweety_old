import json
from ..sParser import find_single_special_pattern, Special_pattern, stanford_simplify


with open('./datasets/new_test_file') as pattern_file:
    phrase_patterns = []
    lines = pattern_file.readlines()
    del(lines[0])
    for line in lines:
        line = line.strip().split('\t')
        phrase_pattern = Special_pattern(line[0], line[1], line[2], line[3], line[4])
        pos_tags = []
        for feature in phrase_pattern.features:
            pos_tags.append(feature['pos_tag'])
        phrase_pattern['symbol'] = '|'.join(pos_tags)
        print(phrase_pattern)
        phrase_patterns.append(phrase_pattern)


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

            # 以上与init相同

            for phrase_pattern in phrase_patterns:
                new_parse_result = find_single_special_pattern(parse_result, phrase_pattern)
                if 'example' in phrase_pattern:
                    if len(phrase_pattern['example']) < 5:
                        phrase_pattern['example'].append(new_parse_result[0])
                else:
                    phrase_pattern['example'] = [new_parse_result[0]]
            if all_results == []:
                print(sub_sentence)
            else:
                print(all_results)



with open('new_test_file', 'w') as new_test_file:
    lines = new_test_file.readlines()
    del(lines[0])
    for line in lines:
        line = line.strip().split()
        pos_tags = line[1].split('|')
        features = []
        for pos_tag in pos_tags:
            feature = {}
            feature['pos_tag'] = pos_tag
            features.append(feature)
        phrase_pattern = [line[0], json.dumps(features, ensure_ascii=False), line[2], line[3], line[4]]
        new_test_file.write('\t'.join(phrase_pattern) + '\n')
