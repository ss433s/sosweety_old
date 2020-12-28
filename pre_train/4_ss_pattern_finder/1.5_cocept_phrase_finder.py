##############
# 第一步 找出所有在kb的NN
##############

import os
import pandas as pd

# 当前路径和项目root路径， 可以根据需求改变../..
this_file_path = os.path.split(os.path.realpath(__file__))[0]
root_path = os.path.abspath(os.path.join(this_file_path, "../.."))

stat_file_path = 'data/4_ss_pattern/ss_pattern_stat'
# stat_file_path = 'data/3_phrase_pattern/123'
stat_file_path = os.path.join(root_path, stat_file_path)

count = 0
c10 = 0
c100 = 0
key_list = []
value_list = []
with open(stat_file_path) as stat_file:
    line = stat_file.readline()
    while line:
        count += 1
        if count % 500000 == 0:
            print('count %s phrases' % count)
        line = line.strip().split('\t')
        if len(line) > 1:
            if int(line[1]) > 10:
                c10 += 1
                key_list.append(line[0])
                value_list.append(int(line[1]))
            if int(line[1]) > 100:
                c100 += 1

        line = stat_file.readline()

print(c10, c100)

df_dict = {}
df_dict['key'] = key_list
df_dict['value'] = value_list
df = pd.DataFrame(df_dict)
df2 = df.sort_values(by=['value'], ascending=False)

ordered_stat_file_path = 'data/4_ss_pattern/ordered_ss_pattern_stat.csv'
ordered_stat_file_path = os.path.join(root_path, ordered_stat_file_path)
df2.to_csv(ordered_stat_file_path)
