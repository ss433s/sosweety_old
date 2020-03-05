import sys, time
#import pandas as pd
import json
from stanfordcorenlp import StanfordCoreNLP
nlp = StanfordCoreNLP(
    r'/DATA/disk1/guoyu9/setups/stanford-corenlp-full-2018-10-05/', lang='zh')
from pyhanlp import *
import os
from pyltp import Segmentor
from pyltp import Postagger
from pyltp import Parser

LTP_DATA_DIR = '/DATA/disk1/guoyu9/setups/ltp_data_v3.4.0/'
cws_model_path = os.path.join(LTP_DATA_DIR, 'cws.model')
pos_model_path = os.path.join(LTP_DATA_DIR,
                              'pos.model')  # 词性标注模型路径，模型名称为`pos.model`
par_model_path = os.path.join(LTP_DATA_DIR,
                              'parser.model')  # 依存句法分析模型路径，模型名称为`parser.model`

#tools 初始化和加载模型
segmentor = Segmentor()
segmentor.load(cws_model_path)
postagger = Postagger()
postagger.load(pos_model_path)
parser = Parser()
parser.load(par_model_path)

filename = os.path.basename(sys.argv[1])
print(filename)
amod_file = open(filename + '_amod', 'w')
nsubj_file = open(filename + '_nsubj', 'w')
dobj_file = open(filename + '_dobj', 'w')
error_file = open(filename + '_error_file', 'w')

with open(sys.argv[1], 'r', encoding='utf8') as corpus:
    line = corpus.readline()
    count = 0

    while line:
        try:
            sentence = line.strip()
            han_amod_dict = {}
            han_nsubj_dict = {}
            han_dobj_dict = {}
            parse = HanLP.parseDependency(sentence)
            for i in parse.word:
                if i.DEPREL == '定中关系':
                    han_amod_dict[i.LEMMA + '|' +
                                  i.HEAD.LEMMA] = (i.POSTAG, i.HEAD.POSTAG)
                if i.DEPREL == '主谓关系':
                    han_nsubj_dict[i.LEMMA + '|' +
                                   i.HEAD.LEMMA] = (i.POSTAG, i.HEAD.POSTAG)
                if i.DEPREL == '动宾关系':
                    han_dobj_dict[i.LEMMA + '|' +
                                  i.HEAD.LEMMA] = (i.POSTAG, i.HEAD.POSTAG)

            ltp_amod_dict = {}
            ltp_nsubj_dict = {}
            ltp_dobj_dict = {}
            words = segmentor.segment(sentence)
            postags = postagger.postag(words)
            arcs = parser.parse(words, postags)
            for i in range(len(arcs)):
                arc = arcs[i]
                if arc.relation == 'ATT':
                    ltp_amod_dict[words[i] + '|' +
                                  words[arc.head - 1]] = (postags[i],
                                                          postags[arc.head -
                                                                  1])
                if arc.relation == 'SBV':
                    ltp_nsubj_dict[words[i] + '|' +
                                   words[arc.head - 1]] = (postags[i],
                                                           postags[arc.head -
                                                                   1])
                if arc.relation == 'VOB':
                    ltp_dobj_dict[words[i] + '|' +
                                  words[arc.head - 1]] = (postags[i],
                                                          postags[arc.head -
                                                                  1])

            pos_tag = nlp.pos_tag(sentence)
            for i in nlp.dependency_parse(sentence):
                key = pos_tag[i[2] - 1][0] + '|' + pos_tag[i[1] - 1][0]
                if i[0] == 'amod':
                    if key in han_amod_dict and key in ltp_amod_dict:
                        tmp_tuple = (pos_tag[i[2] - 1][1], pos_tag[
                            i[1] -
                            1][1]) + han_amod_dict[key] + ltp_amod_dict[key]
                        amod_file.write(key + '\t' + json.dumps(tmp_tuple) +
                                        '\t' + str(count) + '\n')
                if i[0] == 'nsubj':
                    if key in han_nsubj_dict and key in ltp_nsubj_dict:
                        tmp_tuple = (pos_tag[i[2] - 1][1], pos_tag[
                            i[1] -
                            1][1]) + han_nsubj_dict[key] + ltp_nsubj_dict[key]
                        nsubj_file.write(key + '\t' + json.dumps(tmp_tuple) +
                                         '\t' + str(count) + '\n')
                if i[0] == 'dobj':
                    if key in han_dobj_dict and key in ltp_dobj_dict:
                        tmp_tuple = (pos_tag[i[2] - 1][1], pos_tag[
                            i[1] -
                            1][1]) + han_dobj_dict[key] + ltp_dobj_dict[key]
                        dobj_file.write(key + '\t' + json.dumps(tmp_tuple) +
                                        '\t' + str(count) + '\n')
        except Exception as e:
            # print(e)
            error_file.write(line)

        line = corpus.readline()
        count += 1
        if count % 5000 == 0:
            localtime = time.asctime(time.localtime(time.time()))
            print(count, localtime)
        # if count>1000:
        # break

    amod_file.close()
    nsubj_file.close()
    dobj_file.close()
    error_file.close()

segmentor.release()
postagger.release()
parser.release()
