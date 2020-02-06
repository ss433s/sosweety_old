import pandas as pd
from pyhanlp import HanLP


# 导入辞海数据
df = pd.read_csv('cihai.csv', header=None)

with open('tmp.json', 'w') as tmp_file:
    for i in range(len(df)):
        # print(df.iloc[i, ])
        text = df.iloc[i, 2]
        ha_parse_result = HanLP.parseDependency(text)
        for word in ha_parse_result.word:
            t_list = [word.LEMMA, word.POSTAG, word.CPOSTAG]
            tmp_file.write('\t'.join(t_list) + '\n')
