# import jieba
import re, json, argparse
from pyhanlp import HanLP
import sys
sys.path.append("..")
from sub_sentence import ahaha as ahaha
from utils import tuple_in_tuple

ahaha()

# from stanfordcorenlp import StanfordCoreNLP
# nlp = StanfordCoreNLP(r'/mnt/e/ubuntu/stanford-corenlp-full-2018-10-05/',lang='zh')

parser = argparse.ArgumentParser()
parser.add_argument("-c",
                    "--corpus",
                    default="./data/train.txt",
                    help="corpus file folder for training",
                    required=False)
args = parser.parse_args()


###################
# 分句
# to do 引号破折号等，引号纠错
###################
def seg2sentence(paragraph):
    sentences = re.split('(。|！|\!|\.|？|\?)', paragraph)
    new_sents = []
    for i in range(int(len(sentences)/2)):
        if 2*i + 1 < len(sentences):
            sent = sentences[2*i] + sentences[2*i+1]
        else:
            sent = sentences[2*i]
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
    for i in range(int(len(sub_sentences)/2)+1):
        if 2*i + 1 < len(sub_sentences):
            sub_sent = sub_sentences[2*i] + sub_sentences[2*i+1]
        else:
            sub_sent = sub_sentences[2*i]
        new_sub_sents.append(sub_sent)
    return new_sub_sents


###################
# 重分词
###################
def re_cut_word():
    return


###################
# 词组识别
###################
def xps_finder():
    return


###################
# spo_check
###################
def spo_check():
    return


###################
# Parataxis
###################
def parataxis_finder():
    return


###################
# 处理分句
###################
def check_sub_sentence(sub_sentence):
    return


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
    # sentences = seg2sentence(line)
    sentences = cut_sent(line)
    # CRFnewSegment_new = HanLP.newSegment("crf")
    # s = CRFnewSegment_new.seg2sentence(line)
    print(line)
    print(sentences)
    for sentence in sentences:
        sub_sentences = seg2sub_sentence(sentence)
        print(sub_sentences)
    line = corpus.readline()
corpus.close()


###################
# 读取处理好的Stanford语法分析和依存分析结果
###################
def get_stanford_words_token(pos_tags):
    k = 0
    words_token = []
    pos_str_list = []
    for i in pos_tags:
        words_token.append((k, k + len(i[0]) - 1))
        k += len(i[0])

        # 标点单算？
        if i[1] == 'PU':
            pos_str_list.append(i[0])
        else:
            pos_str_list.append(i[1])
    pos_str = '|'.join(pos_str_list)
    return words_token, pos_str


###################
# 切分sub sentence，需增加中文分句算法和并列关系合并方法
# 返回值为sbar_list 内容为[sbar_pos_list,sbar_word_list]
###################
def divide_sentence(sentence, pos_str, words_token):
    pos_str_list = pos_str.split('|')
    stop_codens = ['，', '。', '：', ':', ',']

    sbar_pos_list = []
    sbar_word_list = []
    sbar_list = []
    for idx in range(len(pos_str_list)):

        if idx == len(pos_str_list) - 1:
            token = words_token[idx]
            sbar_pos_list.append(pos_str_list[idx])
            sbar_word_list.append(sentence[token[0]:token[1] + 1])
            sbar_list.append([sbar_pos_list, sbar_word_list])
            sbar_pos_list = []
            sbar_word_list = []
        else:
            if pos_str_list[idx] in stop_codens:
                sbar_list.append([sbar_pos_list, sbar_word_list])
                sbar_pos_list = []
                sbar_word_list = []
            else:
                token = words_token[idx]
                sbar_pos_list.append(pos_str_list[idx])
                sbar_word_list.append(sentence[token[0]:token[1] + 1])
    return sbar_list


###################
# 简化sub sentence
###################
def simplify1(sbar_pos_list, sbar_word_list):
    ap_pattern1 = ('((AD\|)*(JJ\|?)+)+', 'AP|', 'ap1')
    qp_pattern1 = ('(AP\|)*([CO]D\|)(AP\|)*M\|?', 'QP|', 'qp1')
    np_pattern1 = (
        '((QP\|)*(AP\|)+(QP\|)*(DE.\|))?(QP\|)*(AP\|)*(QP\|)*(NN|NR)\|?',
        'NP|', 'np1')
    vp_pattern1 = ('(AD\|)*(JJ\|)*(VV\|?)+(AS\|?)*', 'VP|', 'vp1')
    ntp_pattern1 = ('(NT\|?)+', 'NTP|', 'ntp1')

    patterns = [
        ap_pattern1, qp_pattern1, np_pattern1, vp_pattern1, ntp_pattern1
    ]

    #     ap_pattern1=('((AD\|)*(JJ\|?)+)+','AP|','ap1')
    #     qp_pattern1=('(AP\|)*([CO]D\|)(AP\|)*M\|?','QP|','qp1')
    #     np_pattern1=('(((QP\|)*(AP\|)+(QP\|)*(DE.\|))?(QP\|)*(AP\|)*(QP\|)*(NN|NR|NP|PN)\|?)+','NP|','np1')
    #     vp_pattern1=('(AD\|)*(JJ\|)*(V[VC]\|?)+(AS\|?)*','VP|','vp1')
    #     ntp_pattern1=('(NT\|?)+','NTP|','ntp1')

    #     #方案1
    #     np_pattern2=('((NP\|)*(VP\|)+(NP\|)*|(NP\|)+)(DE.\|)NP','NP|','np2')
    #     pp_pattern1=('(((^|\|)P)\|)+(NP\|?)+(LC\|?)*','PP|','pp1')
    #     patterns=[ap_pattern1,qp_pattern1,np_pattern1,vp_pattern1,ntp_pattern1,np_pattern2,pp_pattern1]

    #     #方案2
    # #     np_pattern2=('(NP\|)+(DE.\|)NP','NP|','np2')
    # #     np_pattern3=('(NP\|)*(VP\|)+(DE.\|)NP','NP|','np3')
    # #     pp_pattern1=('(((^|\|)P)\|)+(NP\|?)+(LC\|?)*','PP|','pp1')
    # #     patterns=[ap_pattern1,qp_pattern1,np_pattern1,vp_pattern1,np_pattern2,np_pattern3,pp_pattern1]

    t_str_list = sbar_pos_list
    t_words_list = sbar_word_list
    for pattern, re_str, _ in patterns:
        t_str = '|'.join(t_str_list)
        result = re.finditer(pattern, t_str)

        spans = []
        for match in result:
            spans.append(match.span())
#         print(t_words_list)
#         print(t_str)
#         print(spans)
        k = 0
        kept_word_list = []
        ketp_pos_list = []
        tmp_words = [''] * len(spans)
        for i in range(len(t_str_list)):
            i_span = (k, k + len(t_str_list[i]))
            k += len(t_str_list[i]) + 1

            not_in_spans = True

            for j in range(len(spans)):
                if tuple_in_tuple(i_span, spans[j]):
                    not_in_spans = False
                    tmp_word = tmp_words[j]

                    if tmp_word == '':
                        ketp_pos_list.append(re_str[:-1])
                        kept_word_list.append(t_words_list[i])
                        tmp_word += t_words_list[i]
                        tmp_words[j] = tmp_word
                    else:
                        tmp_word += t_words_list[i]
                        tmp_words[j] = tmp_word
                        kept_word_list[-1] = tmp_word

            if not_in_spans:
                kept_word_list.append(t_words_list[i])
                ketp_pos_list.append(t_str_list[i])
        t_words_list = kept_word_list
        t_str_list = ketp_pos_list

    rst_str = '|'.join(t_str_list)
    rst_words = t_words_list
    return (rst_str, rst_words)


###################
# 读取sub sentence pattern和 phrase_rules. 考虑以后改为数据库
###################
ss_pattern_file = open('ss_pattern')
ss_pattern_list = []
for line in ss_pattern_file.readlines():
    line = line.strip().split('\t')
    if len(line[0]) > 0:
        ss_pattern_list.append(line[0])
print(ss_pattern_list)

###################
# 读取待分析数据
###################
stanford_tokens = []
file = open('parse_file_total')
lines = file.readlines()
print(len(lines))

unsolvable_ss_file = open('unsolvable_ss', 'w')

for i in range(len(lines)):
    # for i in range(300,320):
    line = lines[i].strip().split('\t')
    pos_tags = json.loads(line[1])
    sentence = train_data[i]['text']
    sentence = re.sub('\s', '', sentence, 0)
    token, pos_str = get_stanford_words_token(pos_tags)

    # todo 竖线的处理
    if '|' in sentence:
        continue

    if len(sentence) != token[-1][1] + 1:
        print(sentence)
        print(len(sentence))
        print(token[-1][1])

        ################
        # 包含空格的句子的处理
        ################

    else:
        sbar_list = divide_sentence(sentence, pos_str, token)
        for sbar in sbar_list:
            sbar_pos_list = sbar[0]
            sbar_word_list = sbar[1]
            simplified_str, simplified_words = simplify1(
                sbar_pos_list, sbar_word_list)

            ################
            # 是否在句式库
            ################
            if simplified_str in ss_pattern_list:
                ################
                # 后续处理
                ################
                continue
            else:
                unsolvable_ss_file.write(json.dumps(sbar[0], ensure_ascii=False) + '\t' +
                                         json.dumps(sbar[1], ensure_ascii=False) + '\t' +
                                         json.dumps(simplified_str, ensure_ascii=False) + '\t' +
                                         json.dumps(simplified_words, ensure_ascii=False) + '\n')
unsolvable_ss_file.close()
