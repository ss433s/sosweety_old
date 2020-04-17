import pandas as pd
import json
# from stanfordcorenlp import StanfordCoreNLP
# nlp = StanfordCoreNLP(r'~/setups/nlp_support/stanford-corenlp-full-2018-10-05/', lang='zh')
from pyhanlp import *
import os
from pyltp import Segmentor
from pyltp import Postagger
from pyltp import Parser
import jieba
import jieba.posseg
