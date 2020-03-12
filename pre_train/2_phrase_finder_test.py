import json
import time


# parse result类
class Parse_result(object):
    def __init__(self, contents):
        self.contents = contents
        self.pos_tags = [i.pos_tag for i in self.contents]
        self.words = [i.value for i in self.contents]
        self.parse_str = "|".join(self.pos_tags)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        s = ""
        # s += "words: %s" % (self.words)
        # s += ", pos_tags: %s" % (self.pos_tags)
        s += "\"content: %s\"" % (self.contents)
        return s


# 单词类 value为字面， pos_tag为词性
class Word(object):
    def __init__(self, value, pos_tag, pos_tag2=None):
        self.value = value
        self.pos_tag = pos_tag
        self.core_word = self.value
        if pos_tag2:
            self.pos_tag2 = pos_tag2

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        s = ""
        s += "word: %s" % (self.value)
        s += ", pos_tag: %s" % (self.pos_tag)
        # s += ", parse_str: %s" % (self.parse_str)
        return s


def stanford_simplify(pos_tags):  # stanford 的postag 是列表，列表元素是（词，词性）的元组
    stanford_simplify_dict = {}
    with open('datasets/stanford_simplify') as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip().split('\t')
            stanford_simplify_dict[line[0]] = line[1]
    result = []
    for word, pos_tag in pos_tags:
        result.append((word, stanford_simplify_dict[pos_tag]))
    return result


###################
# 读取待处理文件
# to do
# 准备提供对外接口处理不同文件
###################
file = './init_data/parse_file_total'
unsolvable_ss_file = open(file)

# 获取所有分句


# 百度信息抽取预处理数据形式
print(time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime()))


def tuples2parse_result(tuples):
    content = []
    for word in tuples:
        tmp_word = Word(word[0], word[1])
        content.append(tmp_word)
    parse_result = Parse_result(content)
    return parse_result


lines = unsolvable_ss_file.readlines()
ss_parse_results = []
for i in range(len(lines)):
    if i % 10000 == 0:
        print('parsed %s sentence, total ~170000' % i)
    if i > 10000:
        break

    line = lines[i].split('\t')
    parse_str = line[0]
    pos_tags = json.loads(line[1].strip())
    pos_tags = stanford_simplify(pos_tags)

    tmp_stamp = 0
    for i in range(len(pos_tags)):
        pos_tag = pos_tags[i]
        if pos_tag[0] in ['。', '！', '？', '?', '，', ',', ';', '；']:
            ss_parse_result = tuples2parse_result(pos_tags[tmp_stamp: i])
            ss_parse_results.append(ss_parse_result)
            tmp_stamp = i + 1
    if tmp_stamp < len(pos_tags):
        ss_parse_result = tuples2parse_result(pos_tags[tmp_stamp: len(pos_tags)])
        ss_parse_results.append(ss_parse_result)

# 开始finder 定义参数
cutoff = 1000


###################
# 找concept pattern
###################
# def check_out_entities(parse_result, KB):
#     sentence = ''.join(parse_result.words)
#     matched_words = KB.checkout_words(sentence)
#     return matched_words


# for ss_parse_result in ss_parse_results:
#     rst = check_out_entities(ss_parse_result, KB)


###################
# 找多词pattern
###################
# high_freq_word_file = open('./ss/pre_train/high_freq_word_file', 'w')
# word_freq_dict = {}
# high_freq_word_set = set()
# # 分词遍历
# for ss_parse_result in ss_parse_results:
#     word_list = ss_parse_result.words
#     pos_list = ss_parse_result.pos_tags
#     for word in word_list:
#         if word in word_freq_dict:
#             word_freq_dict[word] += 1
#         else:
#             word_freq_dict[word] = 0
#         if word_freq_dict[word] > cutoff:
#             high_freq_word_set.add(word)
# print(len(high_freq_word_set))

# hf_co_dict = {}
# for high_freq_word in high_freq_word_set:
#     co_word_set = set()
#     co_word_freq_dict = {}
#     co_word_freq_dict[high_freq_word] = 0
#     for ss_parse_result in ss_parse_results:
#         word_list = ss_parse_result.words
#         pos_list = ss_parse_result.pos_tags
#         # 自身重复是否可以构成pattern
#         if word_list.count(high_freq_word) > 1:
#             co_word_freq_dict[high_freq_word] += 1
#             if co_word_freq_dict[high_freq_word] > cutoff:
#                 co_word_set.add(high_freq_word)
#                 # print(word_list)
#         if high_freq_word in word_list:
#             for word in word_list:
#                 if word != high_freq_word:

#                     if word in co_word_freq_dict:
#                         co_word_freq_dict[word] += 1
#                     else:
#                         co_word_freq_dict[word] = 0
#                     if co_word_freq_dict[word] > cutoff:
#                         co_word_set.add(word)
#     if len(co_word_set) > 0:
#         print(high_freq_word, co_word_set)
#         hf_co_dict[high_freq_word] = list(co_word_set)

hf_co_dict = {}
hf_co_dict['（'] = ['）']
potential_pattern_dict = {}
for high_freq_word in hf_co_dict:
    for co_word in hf_co_dict[high_freq_word]:
        for ss_parse_result in ss_parse_results:
            word_list = ss_parse_result.words
            pos_list = ss_parse_result.pos_tags

            if high_freq_word in word_list and co_word in word_list:
                high_freq_word_index = word_list.index(high_freq_word)
                co_word_index = word_list.index(co_word)
                if co_word_index > high_freq_word_index:
                    parse_str_list = [high_freq_word] + pos_list[high_freq_word_index+1:co_word_index] + [co_word]
                    example_list = [high_freq_word] + word_list[high_freq_word_index+1:co_word_index] + [co_word]
                    example = '|'.join(example_list)
                    parse_str = '|'.join(parse_str_list)
                    if parse_str in potential_pattern_dict:
                        potential_pattern_dict[parse_str]['count'] += 1
                        potential_pattern_dict[parse_str]['example'].append(example)
                    else:
                        potential_pattern = {}
                        potential_pattern['count'] = 1
                        potential_pattern['example'] = [example]
                        potential_pattern_dict[parse_str] = potential_pattern

with open('./init_data/potential_pattern', 'w') as potential_pattern_file:
    for parse_str in potential_pattern_dict:
        for example in potential_pattern_dict[parse_str]['example']:
            potential_pattern_file.write(parse_str + '\t' + str(potential_pattern_dict[parse_str]['count']) + '\t' + example + '\n')
