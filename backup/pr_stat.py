import sys
import json

file = open(sys.argv[1])
file_pr = open(sys.argv[1]+'_pr', 'w')
symbol = 'PR'
line = file.readline()
while line:
    line_raw = line
    line = line.split('\t')
    pos_list = json.loads(line[1])
    if sys.argv[2] == '1':
        if ((pos_list[0] == 'NR' or pos_list[4] == 'nh') and pos_list[2] == 'nr') \
           or pos_list[2] == 'nr1' or pos_list[2] == 'nr2' or pos_list[2] == 'nrf' or pos_list[2] == 'nrj':
            keys = line[0].split('|')
            key = symbol + '|' + keys[1]
            file_pr.write(key+'\t'+line[1]+'\t'+line[2])
        else:
            file_pr.write(line_raw)
    elif sys.argv[2] == '2':
        if ((pos_list[1] == 'NR' or pos_list[5] == 'nh') and pos_list[3] == 'nr') \
           or pos_list[3] == 'nr1' or pos_list[3] == 'nr2' or pos_list[3] == 'nrf' or pos_list[3] == 'nrj':
            keys = line[0].split('|')
            key = keys[0] + '|' + symbol
            file_pr.write(key+'\t'+line[1]+'\t'+line[2])
        else:
            file_pr.write(line_raw)

    line = file.readline()

file_pr.close()
