# import jieba
import re, json, argparse
# import regex as re2
import jieba
import jieba.posseg
from pyhanlp import HanLP
import sys
sys.path.append("..")
from sub_sentence import ahaha as ahaha
from utils import tuple_in_tuple, find_all_sub_list
from knowledgebase import Knowledge_base


# ###########################各种类######################

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
        s += "words: %s" % (self.words)
        s += ", pos_tags: %s" % (self.pos_tags)
        # s += ", parse_str: %s" % (self.parse_str)
        return s


# 单词类 value为字面， pos_tag为词性
class Word(object):
    def __init__(self, value, pos_tag, pos_tag2=None):
        self.value = value
        self.pos_tag = pos_tag
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


# Special pattern和Phrase类 特殊短语
class Special_pattern(object):
    def __init__(self, phrase_type, features, freq, core_word_index, meaning):
        self.phrase_type = phrase_type
        self.pos_tag = self.phrase_type
        self.core_word_index = core_word_index
        self.features = json.loads(features)
        self.freq = freq
        self.meaning = meaning

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        s = ""
        s += ", features: %s" % (self.features)
        s += ", phrase_type: %s" % (self.phrase_type)
        s += ", freq: %s" % (self.freq)
        s += ", meaning: %s" % (self.meaning)
        return s


class Special_phrase(object):
    def __init__(self, phrase_pattern, contents):
        self.contents = contents
        self.phrase_type = phrase_pattern.phrase_type
        self.pos_tag = self.phrase_type
        self.core_word_index = phrase_pattern.core_word_index
        self.freq = phrase_pattern.freq
        self.meaning = phrase_pattern.meaning
        self.words = [content.value for content in self.contents]
        self.value = "".join(self.words)
        if self.core_word_index == '-':
            self.core_word = self.value
        else:
            self.core_word = self.words[int(self.core_word_index)]

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        s = ""
        s += "words: %s" % (self.words)
        s += ", phrase_type: %s" % (self.phrase_type)
        s += ", freq: %s" % (self.freq)
        s += ", meaning: %s" % (self.meaning)
        return s


# sub sentence类 可以是句子中的一部分
class Sub_sentence(object):
    def __init__(self, parse_str, freq):
        self.parse_str = parse_str
        self.freq = freq


# ###########################各种函数######################

###################
# 分句
# to do 引号破折号等，引号纠错
###################
def seg2sentence(paragraph):
    sentences = re.split('(。|！|\!|\.|？|\?)', paragraph)
    new_sents = []
    for i in range(int(len(sentences) / 2)):
        if 2 * i + 1 < len(sentences):
            sent = sentences[2 * i] + sentences[2 * i + 1]
        else:
            sent = sentences[2 * i]
        new_sents.append(sent)
    return new_sents


def cut_sent(para):
    para = re.sub('([。！？\?])([^”’])', r"\1\n\2", para)  # 单字符断句符
    para = re.sub('(\.{6})([^”’])', r"\1\n\2", para)  # 英文省略号
    para = re.sub('(\…{2})([^”’])', r"\1\n\2", para)  # 中文省略号
    para = re.sub('([。！？\?][”’])([^，。！？\?])', r'\1\n\2', para)
    # 如果双引号前有终止符，那么双引号才是句子的终点，把分句符\n放到双引号后，注意前面的几句都小心保留了双引号
    para = para.rstrip()  # 段尾如果有多余的\n就去掉它
    # 很多规则中会考虑分号;，但是这里我把它忽略不计，破折号、英文双引号等同样忽略，需要的再做些简单调整即可。
    return para.split("\n")


###################
# 拆分子句
# to do 引号破折号等，引号纠错
###################
def seg2sub_sentence(sentence):
    sub_sentences = re.split('(，|,|;|；)', sentence)
    new_sub_sents = []
    for i in range(int(len(sub_sentences) / 2) + 1):
        if 2 * i + 1 < len(sub_sentences):
            sub_sent = sub_sentences[2 * i] + sub_sentences[2 * i + 1]
        else:
            sub_sent = sub_sentences[2 * i]
        new_sub_sents.append(sub_sent)
    return new_sub_sents


###################
# 词组检测
# 构建所有可能的词组组合
###################
# 先检测特殊短语
def check_special_phrase(parse_result, final_results):
    not_done = []
    if check_ss_pattern(parse_result) and parse_result not in final_results:
        final_results.append(parse_result)
    for phrase_pattern in phrase_patterns:
        new_parse_results = find_single_special_pattern(parse_result, phrase_pattern)
        not_done.append(len(new_parse_results) == 0)
        for new_parse_result in new_parse_results:
            if check_ss_pattern(new_parse_result):
                final_results.append(new_parse_result)
            check_special_phrase(new_parse_result, final_results)
    if all(not_done):
        return


# 检测一个special phrase pattern 在一份parse result中的所有位置
def find_single_special_pattern(parse_result, special_pattern):

    def match_one_feature(parse_result_content, feature):
        result = False
        if list(feature.keys())[0] == 'concept':
            rst = KB.word_belong_to_concept(parse_result_content.value, feature['concept'])
            if len(rst) > 0:
                result = True
        if list(feature.keys())[0] == 'word':
            if parse_result_content.value == feature['word']:
                result = True
        if list(feature.keys())[0] == 'special_symbol':
            pass
        if list(feature.keys())[0] == 'pos_tag':
            if parse_result_content.pos_tag == feature['pos_tag']:
                result = True
        return result

    new_parse_results = []
    first_feature = special_pattern.features[0]

    new_parse_result_contents = []
    for j in range(len(parse_result.pos_tags) - len(special_pattern.features) + 1):
        if match_one_feature(parse_result.contents[j], first_feature):
            i = 1
            while len(parse_result.contents) > j + i and len(special_pattern.features) > i:
                if match_one_feature(parse_result.contents[j + i], special_pattern.features[i]):
                    i += 1
                    continue
                else:
                    break

            if i == len(special_pattern.features):
                contents = parse_result.contents[j: j + i]
                special_phrase = Special_phrase(special_pattern, contents)
                new_parse_result_contents.append(special_phrase)
                if j + i < len(parse_result.contents):
                    new_parse_result_contents.append(parse_result.contents[j + i: len(parse_result.contents)])
                new_parse_result = Parse_result(new_parse_result_contents)
                new_parse_results.append(new_parse_result)
        else:
            new_parse_result_contents.append(parse_result.contents[j])
    return new_parse_results


# check_sub_sentence
def check_ss_pattern(parse_result):
    result = False
    for ss_pattern in ss_patterns:
        if parse_result.parse_str == ss_pattern.parse_str:
            result = True
    return result


###################
# meaningful_check
# 返回true or false
###################
def meaningful_check():
    return


###################
# Parataxis
###################
def parataxis_finder():
    return


###################
# hanlp parse
###################
def hanlp_parse(text):
    ha2stanford_dict = {}
    with open('datasets/ha2stanford') as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip().split('\t')
            ha2stanford_dict[line[0]] = line[1]
    ha_parse_result = HanLP.parseDependency(text)
    print(ha_parse_result)
    words = []
    for i in ha_parse_result.word:
        word = Word(i.LEMMA, ha2stanford_dict[i.CPOSTAG], i.CPOSTAG)
        words.append(word)
    parse_result = Parse_result(words)
    return parse_result


###################
# jieba parse
###################
def jieba_parse(text):
    parse_result = jieba.posseg.cut(text)
    words = []
    pos_tags = []
    for word, flag in parse_result:
        words.append(word)
        pos_tags.append(flag)
    clean_text = "".join(words)
    return words, pos_tags, clean_text


###################
# sParser类 通用parser
###################
class sParser(object):
    def __init__(self, KB, mode='default', ):
        self.mode = mode
        self.KB = KB

    def parse(text):
        return text


###################
# 读取短语库和句式库
###################
# with open('./datasets/np_pattern') as np_file:
with open('./datasets/new_test_file') as pattern_file:
    phrase_patterns = []
    lines = pattern_file.readlines()
    del(lines[0])
    for line in lines:
        line = line.strip().split('\t')
        phrase_pattern = Special_pattern(line[0], line[1], line[2], line[3], line[4])
        phrase_patterns.append(phrase_pattern)

with open('./datasets/ss_pattern') as ss_file:
    ss_patterns = []
    lines = ss_file.readlines()
    del(lines[0])
    for line in lines:
        line = line.strip().split()
        if len(line) > 1:
            ss_pattern = Sub_sentence(line[0], line[1])
            ss_patterns.append(ss_pattern)



KB = Knowledge_base()




if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-c",
                        "--corpus",
                        default="./init_data/train.txt",
                        help="corpus file folder for training",
                        required=False)
    args = parser.parse_args()

    ###################
    # 读取待处理语料，格式为每行一个数据，每个数据可以是多句话组成
    ###################
    try:
        corpus = open(args.corpus, 'r', encoding='utf-8')
    except Exception:
        corpus = open(args.corpus, 'r', encoding='gbk')


    line = corpus.readline()
    while line:
        line = line.strip()

        # 语料分句
        # sentences = seg2sentence(line)
        sentences = cut_sent(line)
        # CRFnewSegment_new = HanLP.newSegment("crf")
        # s = CRFnewSegment_new.seg2sentence(line)
        # print(line)
        # print(sentences)

        # 对句子进行parse
        # parse_result, clean_text, stanford_pos = hanlp_parse(line)
        # print(parse_result, clean_text, stanford_pos)
        # check_xps(parse_result)

        # 拆分子句
        for sentence in sentences:
            sub_sentences = seg2sub_sentence(sentence)

            # parse
            print(sub_sentences)
            parse_result = hanlp_parse(line)

            # find_single_special_pattern(parse_result, phrase_patterns[0])

            final_results = []
            check_special_phrase(parse_result, final_results)
            print(len(final_results))
            break
        break
        line = corpus.readline()
    corpus.close()