import json
import pandas as pd
from stanfordcorenlp import StanfordCoreNLP
nlp = StanfordCoreNLP(r'/mnt/e/ubuntu/stanford-corenlp/stanford-corenlp-full-2018-10-05/', lang='zh')


# 从parse_str中提取指定类型的短语，转化为[词，词性]的数组中的第N个元素的合集 
def check_np(parse_str, xp_type):
    tag_count = 0
    sbar_str_group = []
    # for i in range(len(parse_str)):
    i = 0
    while i < len(parse_str):
        i += 1
        if parse_str[i - 1:i + 1] == xp_type:
            k = 0
            for j in range(i, len(parse_str)):
                if parse_str[j] == '(':
                    k += 1
                if parse_str[j] == ')':
                    k -= 1
                if k < 0:
                    # print(parse_str[i-2:j+1])
                    sbar_str_group.append(range(i - 2, j + 1))
                    i = j + 1
                    break
    # print(sbar_str_group)
    sbar_word_group = [[] for i in range(len(sbar_str_group))]
    for i in range(len(parse_str)):
        char = parse_str[i]
        if char == '(':
            for j in range(i + 1, len(parse_str)):
                if parse_str[j] == '(':
                    break
                if parse_str[j] == ')':
                    # print(parse_str[i:j+1])
                    tag_count += 1
                    for sbar_count in range(len(sbar_str_group)):
                        if j in sbar_str_group[sbar_count]:
                            if tag_count not in sbar_word_group[sbar_count]:
                                sbar_word_group[sbar_count].append(tag_count)
                    break
    return sbar_word_group


# 把元素顺序合集转化为pos_str 和[词，词性]的list
def group2str(sbar_word_group, pos_tags):
    str_group = []
    for group in sbar_word_group:
        parse_str_list = []
        pos_tag_list = []
        for i in group:
            if pos_tags[i - 1][1] == 'PU':
                parse_str_list.append(pos_tags[i - 1][0])
            else:
                parse_str_list.append(pos_tags[i - 1][1])
            pos_tag_list.append(pos_tags[i - 1])
        parse_str = '|'.join(parse_str_list)
        str_group.append([parse_str, pos_tag_list])
    return str_group


# with open('data/parse_file_total') as parse_file:
#     lines = parse_file.readlines()

#     np_file = open('data/np_file', 'w')
#     pp_file = open('data/pp_file', 'w')

#     for i in range(len(lines)):
#         line = lines[i].split('\t')
#         parse_str = line[0]
#         pos_tags = json.loads(line[1].strip())

#         np_word_group = check_np(parse_str, 'NP')
#         np_str_group = group2str(np_word_group, pos_tags)

#         for group in np_str_group:
#             np_file.write(group[0] + '\t' +
#                           json.dumps(group[1], ensure_ascii=False) + '\n')

#         pp_word_group = check_np(parse_str, 'PP')
#         pp_str_group = group2str(pp_word_group, pos_tags)

#         for group in pp_str_group:
#             pp_file.write(group[0] + '\t' +
#                           json.dumps(group[1], ensure_ascii=False) + '\n')

#     np_file.close()
#     pp_file.close()

with open('data/np_file') as np_file:
    line = np_file.readline()
    all_phrase = []
    while line:
        phrase = {}
        line = line.strip().split('\t')
        words = json.loads(line[1])
        if len(words) > 1:
            phrase['type'] = 'NN'
            phrase['pos_str'] = line[0]
            all_phrase.append(phrase)

        line = np_file.readline()

    df = pd.DataFrame(data=all_phrase)
    df_count = df['pos_str'].value_counts()
    count_table_dict = {'pos_str': df_count.index, 'count': df_count.values}
    count_table_df = pd.DataFrame(count_table_dict)

    with open('data/nn_pattern', 'w') as nn_pattern_file:
        for i in range(len(count_table_df)):
            nn_pattern_file.write('NN\t' + count_table_df.iloc[i]['pos_str'] + '\t' + str(count_table_df.iloc[i]['count']) + '\t-\t-\n')

with open('data/pp_file') as pp_file:
    line = pp_file.readline()
    all_phrase = []
    while line:
        phrase = {}
        line = line.strip().split('\t')
        words = json.loads(line[1])
        if len(words) > 1:
            phrase['type'] = 'NN'
            phrase['pos_str'] = line[0]
            all_phrase.append(phrase)

        line = pp_file.readline()

    df = pd.DataFrame(data=all_phrase)
    df_count = df['pos_str'].value_counts()
    count_table_dict = {'pos_str': df_count.index, 'count': df_count.values}
    count_table_df = pd.DataFrame(count_table_dict)

    with open('data/pp_pattern', 'w') as pp_pattern_file:
        for i in range(len(count_table_df)):
            pp_pattern_file.write('PP\t' + count_table_df.iloc[i]['pos_str'] + '\t' + str(count_table_df.iloc[i]['count']) + '\t-\t-\n')