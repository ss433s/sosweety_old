import os, sys, csv
sys.path.append("..")
sys.path.append("../..")


# 当前路径和项目root路径， 可以根据需求改变../..
this_file_path = os.path.split(os.path.realpath(__file__))[0]
root_path = os.path.abspath(os.path.join(this_file_path, ".."))

phrase_file_name = 'phrase_pattern'
phrase_file_path = os.path.join(this_file_path, phrase_file_name)
ss_file_name = 'ss_pattern'
ss_file_path = os.path.join(this_file_path, ss_file_name)

phrase_csv_file_name = 'phrase_pattern.csv'
phrase_csv_file_path = os.path.join(this_file_path, phrase_csv_file_name)
ss_csv_file_name = 'ss_pattern.csv'
ss_csv_file_path = os.path.join(this_file_path, ss_csv_file_name)


with open(phrase_file_path) as pattern_file:
    phrase_csv_file = open(phrase_csv_file_path, 'w+', encoding='utf-8-sig')
    phrase_writer = csv.writer(phrase_csv_file, dialect='excel')
    header = ['pos_tag', 'core_word_index', 'features', 'freq', 'meaning', 'symbol', 'examples']
    phrase_writer.writerow(header)
    lines = pattern_file.readlines()
    for line in lines:
        if line[0] != '#':
            line = line.strip().split('\t')
            phrase_writer.writerow(line)


with open(ss_file_path) as ss_file:
    ss_writer = csv.writer(open(ss_csv_file_path, 'w+', encoding='utf-8-sig'), dialect='excel')
    lines = ss_file.readlines()
    header = ['parse_str', 'freq', 'type', 'meaning']
    ss_writer.writerow(header)
    for line in lines:
        if line[0] != '#':
            line = line.strip().split('\t')
            ss_writer.writerow(line)
