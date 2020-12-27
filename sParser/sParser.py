import re, argparse
# import regex as re2
# import jieba
# import jieba.posseg
import time
import ahocorasick
from pyhanlp import HanLP
import sys
sys.path.append("..")
# from utils import tuple_in_tuple, find_all_sub_list
from kb import Knowledge_base
from parser_class import Parse_result, Word, Special_pattern, Special_phrase, Sub_sentence, Sub_sentence_pattern, Pre_sub_sentence


# ###########################各种函数######################

###################
# 分句
# todo 引号破折号等，引号纠错
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


def cut_sent(paragraph):
    paragraph = re.sub('([。！？\?])([^”’])', r"\1\n\2", paragraph)  # 单字符断句符
    paragraph = re.sub('(\.{6})([^”’])', r"\1\n\2", paragraph)  # 英文省略号
    paragraph = re.sub('(\…{2})([^”’])', r"\1\n\2", paragraph)  # 中文省略号
    paragraph = re.sub('([。！？\?][”’])([^，。！？\?])', r'\1\n\2', paragraph)
    # 如果双引号前有终止符，那么双引号才是句子的终点，把分句符\n放到双引号后，注意前面的几句都小心保留了双引号
    paragraph = paragraph.rstrip()  # 段尾如果有多余的\n就去掉它
    # 很多规则中会考虑分号;，但是这里我把它忽略不计，破折号、英文双引号等同样忽略，需要的再做些简单调整即可。
    return paragraph.split("\n")


###################
# 拆分子句
# todo 引号破折号等，引号纠错 小数点处理
###################
def seg2sub_sentence(sentence):
    sub_sentences = re.split('(，|,|;|；)', sentence)
    new_sub_sents = []
    for i in range(len(sub_sentences)):
        if i % 2 == 0:
            sub_sent = Pre_sub_sentence(sub_sentences[i])
        else:
            sub_sent = Word(sub_sentences[i], 'PU')
        new_sub_sents.append(sub_sent)
    return new_sub_sents


###################
# 词组检测
# 构建所有可能的词组组合
###################
# 先检测特殊短语
def check_special_phrase(parse_result, final_results, mode='default', N=0, start_time=None):
    # print('next')
    not_done = []
    final_results_str = [str(final_result) for final_result in final_results]

    # 自身就在ss_pattern中
    matched_ss_pattern = check_ss_pattern(parse_result)
    if len(matched_ss_pattern) > 0:
        for ss_pattern in matched_ss_pattern:
            ss = Sub_sentence(ss_pattern, parse_result.contents)
            # todo 有可能有ss_str相同 但结构不同的情况出现
            if str(ss) not in final_results_str:
                final_results.append(ss)
                final_results_str.append(str(ss))

    # 替换phrase后在ss_pattern中
    for i in range(len(phrase_patterns)):
        phrase_pattern = phrase_patterns[i]
        # if i % 10 == 0:
        #     print(i, N)
        new_parse_results = find_single_special_pattern(parse_result, phrase_pattern)
        not_done.append(len(new_parse_results) == 0)
        for new_parse_result in new_parse_results:
            matched_ss_pattern = check_ss_pattern(new_parse_result)
            if len(matched_ss_pattern) > 0:
                for ss_pattern in matched_ss_pattern:
                    ss = Sub_sentence(ss_pattern, new_parse_result.contents)
                    if str(ss) not in final_results_str:
                        final_results.append(ss)
                        final_results_str.append(str(ss))

                # 初始化时开启这句，找到就退出循环
                if mode == 'init':
                    break

            if mode == 'init' and len(final_results) > 0:
                break
            # if N < 5:
            if start_time is not None and time.time() - start_time < 60:
                check_special_phrase(new_parse_result, final_results, mode, N + 1, start_time)

            # 不给start time就无限找下去
            if start_time is None:
                check_special_phrase(new_parse_result, final_results, mode, N + 1, start_time)
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
        if list(feature.keys())[0] == 'pos_tag':
            if parse_result_content.pos_tag == feature['pos_tag']:
                result = True

        # 正则符合，需谨慎
        if list(feature.keys())[0] == 'special_symbol':
            if feature['special_symbol'] == '*':
                result = True

        return result

    new_parse_results = []
    first_feature = special_pattern.features[0]

    # for j in range(len(parse_result.pos_tags) - len(special_pattern.features) + 1):
    #     if match_one_feature(parse_result.contents[j], first_feature):
    #         i = 1
    #         while len(parse_result.contents) > j + i and len(special_pattern.features) > i:
    #             if match_one_feature(parse_result.contents[j + i], special_pattern.features[i]):
    #                 i += 1
    #                 continue
    #             else:
    #                 break

    #         if i == len(special_pattern.features):
    #             new_parse_result_contents = parse_result.contents[0:j]
    #             contents = parse_result.contents[j: j + i]
    #             special_phrase = Special_phrase(special_pattern, contents)
    #             new_parse_result_contents.append(special_phrase)
    #             if j + i < len(parse_result.contents):
    #                 new_parse_result_contents += parse_result.contents[j + i: len(parse_result.contents)]
    #             new_parse_result = Parse_result(new_parse_result_contents)
    #             new_parse_results.append(new_parse_result)
    # return new_parse_results

    # 目前限制很多，只识别*且*至少一个,且*前后必须有非*
    for j in range(len(parse_result.pos_tags) - len(special_pattern.features) + 1):
        if match_one_feature(parse_result.contents[j], first_feature):
            # 确定是否包含特殊feature
            pattern_contain_special = False
            for feature in special_pattern.features:
                if 'special_symbol' in feature:
                    pattern_contain_special = True
                    break

            # 有*
            if pattern_contain_special:
                full_match = False
                i = 1
                while len(parse_result.contents) > j + i and len(special_pattern.features) > i:
                    current_feature = special_pattern.features[i]
                    if match_one_feature(parse_result.contents[j + i], current_feature):
                        if 'special_symbol' in current_feature and current_feature['special_symbol'] == '*':
                            next_feature = special_pattern.features[i+1]
                            if match_one_feature(parse_result.contents[j + i + 1], next_feature):
                                i += 2
                                full_match = True
                                break
                            else:
                                for k in range(1, len(parse_result.contents) - j - i):
                                    if match_one_feature(parse_result.contents[j + i + k], next_feature):
                                        i += k + 1
                                        full_match = True
                                        break
                                if full_match:
                                    break
                        i += 1
                    else:
                        break
            # 没有*
            else:
                i = 1
                while len(parse_result.contents) > j + i and len(special_pattern.features) > i:
                    if match_one_feature(parse_result.contents[j + i], special_pattern.features[i]):
                        i += 1
                        # continue
                    else:
                        break
                full_match = i == len(special_pattern.features)

            if full_match:
                new_parse_result_contents = parse_result.contents[0:j]
                contents = parse_result.contents[j: j + i]
                special_phrase = Special_phrase(special_pattern, contents)
                new_parse_result_contents.append(special_phrase)
                if j + i < len(parse_result.contents):
                    new_parse_result_contents += parse_result.contents[j + i: len(parse_result.contents)]
                new_parse_result = Parse_result(new_parse_result_contents)
                new_parse_results.append(new_parse_result)
    return new_parse_results


# check_sub_sentence  返回所有匹配到的ss_pattern
def check_ss_pattern(parse_result):
    result = []
    for ss_pattern in ss_patterns:
        if parse_result.parse_str == ss_pattern.parse_str:
            result.append(ss_pattern)
    return result


###################
# hanlp parse
###################
def hanlp_parse(text):
    ha2stanford_dict = {}
    with open('../utils/ha2stanford') as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip().split('\t')
            ha2stanford_dict[line[0]] = line[1]
    ha_parse_result = HanLP.parseDependency(text)
    # print(ha_parse_result)
    words = []
    for i in ha_parse_result.word:
        word = Word(i.LEMMA, ha2stanford_dict[i.CPOSTAG], i.CPOSTAG)
        words.append(word)
    parse_result = Parse_result(words)
    return parse_result


###################
# stanford parse
###################
def stanford_parse(text):
    return


###################
# 读取短语库和句式库
###################
with open('../data/pattern/new_test_file2') as pattern_file:
    phrase_patterns = []
    lines = pattern_file.readlines()
    del(lines[0])
    for line in lines:
        line = line.strip().split('\t')
        phrase_pattern = Special_pattern(line[0], line[1], line[2], line[3], line[4], line[5], line[6], line[7])
        phrase_patterns.append(phrase_pattern)

with open('../data/pattern/ss_pattern') as ss_file:
    ss_patterns = []
    lines = ss_file.readlines()
    del(lines[0])
    for line in lines:
        line = line.strip().split()
        if len(line) > 1:
            ss_pattern = Sub_sentence_pattern(line[0], line[1], line[2], line[3])
            ss_patterns.append(ss_pattern)


KB = Knowledge_base()


###################
# sParser类 通用parser
###################
class sParser(object):
    def __init__(self, KB, mode='default', current_environment=None):
        self.mode = mode
        self.KB = KB
        self.current_environment = current_environment

    def parse(self, text):

        result = {}
        result['parse_results'] = []
        result['k_points'] = []

        # 1，判定文本类型。对话/新闻稿/公告 等。可自动发现，自动学习
        # to do

        # 2，分句。
        # to do 优化分句
        sentences = cut_sent(text)

        # 3，逐句parse
        for sentence in sentences:
            # 分句的句号处理 可以直接进行分类
            # to do
            sentence = re.sub('([。！？\?])', '', sentence)
            sub_sentences = seg2sub_sentence(sentence)

            for sub_sentence in sub_sentences:
                # print(sub_sentence.value)
                if isinstance(sub_sentence, Pre_sub_sentence):
                    print(sub_sentence.value)
                    # if self.mode == 'special1':  # 专门处理百度信息抽取预处理好的语料

                    parse_result = hanlp_parse(sub_sentence.value)
                    sub_sentence.raw_parse_result = parse_result

                    all_results = []
                    check_special_phrase(parse_result, all_results)

                    # 返回所有results
                    if self.mode == 'default':
                        ss_result = all_results
                    # 返回最高分result
                    if self.mode == 'learning':
                        final_result_score = 0
                        ss_result = []
                        for parse_result in all_results:
                            score = cal_score(parse_result)
                            if score > final_result_score:
                                ss_result = parse_result
                        if ss_result == []:
                            result['parse_results'].append(sub_sentence)  # 无解析结果返回原始的 Pre_sub_sentence
                        else:
                            result['parse_results'].append(ss_result)  # 有解析结果返回Sub_sentence
                else:
                    result['parse_results'].append(sub_sentence)

        return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-c",
                        "--corpus",
                        default="../data/corpus/train.txt",
                        help="corpus file folder for training",
                        required=False)
    args = parser.parse_args()

    # parse_result = hanlp_parse('纵横中文网。')
    # check_known_concepts(parse_result)

    text = '北京（中国的首都）是北京。'
    text = '宝马和奔驰联合开发无人驾驶技术'

    parser = sParser(KB, mode='learning')
    rst = parser.parse(text)
    print(rst)

'''
    # ################## old version #############
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

        parser.parse(line)
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
            sentence = re.sub('([。！？\?])', '', sentence)
            sub_sentences = seg2sub_sentence(sentence)

            # parse
            # print(sub_sentences)
            # parse_result = hanlp_parse(line)

            # # find_single_special_pattern(parse_result, phrase_patterns[0])

            # final_results = []
            # check_special_phrase(parse_result, final_results)
            # print(len(final_results))
            # break
        # break
        line = corpus.readline()
    corpus.close()
'''
