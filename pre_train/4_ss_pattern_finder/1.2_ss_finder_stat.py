import os, sys
sys.path.append("..")
sys.path.append("../..")
from utils.utils import count_value


# 当前路径和项目root路径， 可以根据需求改变../..
this_file_path = os.path.split(os.path.realpath(__file__))[0]
root_path = os.path.abspath(os.path.join(this_file_path, "../.."))

ss_patterns = {}
ss_pattern_file_path = 'data/4_ss_pattern/ss_patterns_raw'
ss_pattern_file_path = os.path.join(root_path, ss_pattern_file_path)

ordered_stat_file_path = 'data/4_ss_pattern/ordered_ss_pattern_stat_cutoff10.csv'
ordered_stat_file_path = os.path.join(root_path, ordered_stat_file_path)

count_value(ss_pattern_file_path, ordered_stat_file_path)
