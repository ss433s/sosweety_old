import jieba
import sys
import argparse
from stanfordcorenlp import StanfordCoreNLP
nlp = StanfordCoreNLP(r'/mnt/e/ubuntu/stanford-corenlp-full-2018-10-05/',lang='zh')


parser=argparse.ArgumentParser()
parser.add_argument("-c","--corpus",help="corpus file folder for training",required=True)
args=parser.parse_args()


print (nlp.pos_tag(args.corpus))
