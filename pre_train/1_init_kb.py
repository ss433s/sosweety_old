import json
import pandas as pd
from sParser import hanlp_parse
# from stanfordcorenlp import StanfordCoreNLP
# nlp = StanfordCoreNLP(r'/Users/guoyu/Documents/supports/stanford-corenlp/stanford-corenlp-full-2018-10-05/', lang='zh')


# 导入辞海数据
df = pd.read_csv('init_data/cihai.csv', header=None)
# print(df.iloc[0, 2])
# for i in range(len(df)):
for i in range(1, 2):
    text = df.iloc[i, 2]
    text = text.split('<br>')
    if len(text) > 1:
        text = text[1]
        print(text)
        s = hanlp_parse(text)
        print(s)
    if i > 10:
        break
