##############
# 第一步 找出所有在kb的NN
##############

import os


# 当前路径和项目root路径， 可以根据需求改变../..
this_file_path = os.path.split(os.path.realpath(__file__))[0]
root_path = os.path.abspath(os.path.join(this_file_path, "../.."))


ss_patterns = {}
ss_pattern_file_path = 'data/4_ss_pattern/ss_patterns_raw'
ss_pattern_file_path = os.path.join(root_path, ss_pattern_file_path)

stat_file_path = 'data/4_ss_pattern/ss_pattern_stat'
stat_file_path = os.path.join(root_path, stat_file_path)

count = 0
with open(ss_pattern_file_path) as ss_pattern_file:
    line = ss_pattern_file.readline()
    while line:
        count += 1
        if count % 500000 == 0:
            print('count %s phrases' % count)
        line = line.strip()
        if line in ss_patterns:
            ss_patterns[line] += 1
        else:
            ss_patterns[line] = 1

        line = ss_pattern_file.readline()

print(len(ss_patterns))

with open(stat_file_path, 'w') as stat_file:
    for key, value in ss_patterns.items():
        stat_file.write(key + '\t' + str(value) + '\n')
