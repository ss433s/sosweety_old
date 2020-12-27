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


###################
# CurrentEnvironment类 设置时间地点变量等 缓存知识点
###################
class CurrentEnvironment(object):
    def __init__(self, time, location, tmp_KB):
        self.time = time
        self.location = location
        self.tmp_KB = tmp_KB


