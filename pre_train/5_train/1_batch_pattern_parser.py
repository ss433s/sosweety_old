import os
import math
import sys

# 当前路径和项目root路径， 可以根据需求改变../..
this_file_path = os.path.split(os.path.realpath(__file__))[0]
root_path = os.path.abspath(os.path.join(this_file_path, "../.."))

corpus_file_path = 'data/corpus/baidu_ie_competition/parse_file_total'
# corpus_file_path = 'data/corpus/baidu_ie_competition/pft10'
corpus_file_path = os.path.join(root_path, corpus_file_path)

train_path = 'data/5_train'
train_path = os.path.join(root_path, train_path)
tmp_path = os.path.join(train_path, 'process')
if not os.path.exists(tmp_path):
    os.makedirs(tmp_path)

python_script_name = '1.1_pattern_parser.py'
python_script_name = os.path.join(this_file_path, python_script_name)
python_location = sys.executable  # '/mnt/d/ubuntu/anaconda3/envs/py36'
number = 3  # 批处理文件数
mode = 1  # 1 处理百度语料的预处理后数据 2 处理普通sub sentence tuple


# 文件分割
with open(corpus_file_path) as f:
    lines = f.readlines()
    average = math.ceil(len(lines)/number)
    tmp_file_name_prefix = os.path.join(tmp_path, os.path.basename(corpus_file_path))
    for i in range(number):
        tmp_file_name = tmp_file_name_prefix + str(i+1)
        with open(tmp_file_name, 'w') as f2:
            if i == number - 1:
                r = range(average*i, len(lines))
            else:
                r = range(average*i, average*(i+1))
            for j in r:
                f2.write(lines[j])

fds = []
for i in range(number):
    cmd = python_location + ' ' + python_script_name + ' ' + tmp_file_name_prefix + str(i+1) + ' ' + str(mode) + ' >' + tmp_file_name_prefix + str(i+1) + '.log'
    cmd = python_location + ' ' + python_script_name + ' ' + tmp_file_name_prefix + str(i+1) + ' >' + tmp_file_name_prefix + str(i+1) + '.log'
    fd = os.popen(cmd)
    fds.append(fd)
for fd in fds:
    fd.read()

print('123')
cmd = 'cat ' + tmp_file_name_prefix + '*unsolved_ss >' + train_path + '/unsolved_ss'
fd = os.popen(cmd)
cmd = 'cat ' + tmp_file_name_prefix + '*_solved_ss >' + train_path + '/solved_ss'
fd = os.popen(cmd)
