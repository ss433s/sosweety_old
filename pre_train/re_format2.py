import json
# import sys
# sys.path.append("..")
from sParser import find_single_special_pattern, Special_pattern, Word, Parse_result, stanford_simplify


with open('datasets/new_test_file') as pattern_file:
    phrase_patterns = []
    lines = pattern_file.readlines()
    del(lines[0])
    for line in lines:
        line = line.strip().split('\t')
        phrase_pattern = Special_pattern(line[0], line[1], line[2], line[3], line[4])
        pos_tags = []
        for feature in phrase_pattern.features:
            pos_tags.append(feature['pos_tag'])
        phrase_pattern.symbol = '|'.join(pos_tags)
        # print(phrase_pattern)
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
                if len(new_parse_result) > 0:
                    tmp_str = 'sentence: ' + str(parse_result.words) + ' parse_str: ' + parse_result.parse_str
                    if phrase_pattern.examples:
                        if len(phrase_pattern.examples) < 5:
                            phrase_pattern.examples.append(tmp_str)
                    else:
                        phrase_pattern.examples = [tmp_str]

        get_enough_examples = [(phrase_pattern.examples is not None and len(phrase_pattern.examples) == 5) for phrase_pattern in phrase_patterns]
        if all(get_enough_examples):
            break


with open('datasets/new_test_file2', 'w') as f:
    heads = []
    for k, _ in vars(phrase_patterns[0]).items():
        heads.append(k)
    heads_str = '#' + '\t'.join(heads)
    f.write(heads_str + '\n')
    for phrase_pattern in phrase_patterns:
        value_list = []
        for k, v in vars(phrase_pattern).items():
            if v is not None:
                if isinstance(v, str):
                    value_list.append(v)
                else:
                    value_list.append(json.dumps(v, ensure_ascii=False))
            else:
                value_list.append('-')
        f.write('\t'.join(value_list) + '\n')
