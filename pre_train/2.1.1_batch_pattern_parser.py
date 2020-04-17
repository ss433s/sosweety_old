import os
from pathlib import Path
import math


ref_file = 'init_data/process/unsolve_ss5th'
# ref_file = 'init_data/process/10line'
tmp_path = 'init_data/process/batch_solve'
python_script_name = '2.1.1_pattern_parser.py'
python_location = '/home/guoyu9/miniconda3/envs/ss36/bin/python'
number = 30  # 批处理文件数
mode = 2  # 1 处理百度语料的预处理后数据 2 处理普通sub sentence tuple

# 创建临时目录
my_file = Path(tmp_path)
if not my_file.is_dir():
    os.makedirs(tmp_path)


# 文件分割
with open(ref_file) as f:
    lines = f.readlines()
    average = math.ceil(len(lines)/number)
    tmp_file_name_prefix = os.path.join(tmp_path, os.path.basename(ref_file))
    for i in range(number):
        tmp_file_name = tmp_file_name_prefix + str(i+1)
        with open(tmp_file_name, 'w') as f2:
            if i == number - 1:
                r = range(average*i, len(lines))
            else:
                r = range(average*i, average*(i+1))
            for j in r:
                f2.write(lines[j])

for i in range(number):
    cmd = python_location + ' ' + python_script_name + ' ' + tmp_file_name_prefix + str(i+1) + ' ' + str(mode) + ' >' + tmp_file_name_prefix + str(i+1) + '.log'
    fd = os.popen(cmd)
    # output = fd.read()
