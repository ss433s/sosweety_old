import json

###################
# 读取未分类ss文件
###################
unsolvable_ss_file = open('./ss/pre_train/unsolvable_ss')
sub_sentences = []
for line in unsolvable_ss_file.readlines():
    line = line.strip().split('\t')
    sub_sentences.append(line)

###################
# 找多词pattern
###################
cutoff = 1000

high_freq_word_file = open('./ss/pre_train/high_freq_word_file', 'w')
word_freq_dict = {}
high_freq_word_set = set()
# 分词遍历
for sub_sentence in sub_sentences:
    word_list = json.loads(sub_sentence[1])
    pos_list = json.loads(sub_sentence[0])
    for word in word_list:
        if word in word_freq_dict:
            word_freq_dict[word] += 1
        else:
            word_freq_dict[word] = 0
        if word_freq_dict[word] > cutoff:
            high_freq_word_set.add(word)
print(len(high_freq_word_set))

hf_co_dict = {}
for high_freq_word in high_freq_word_set:
    co_word_set = set()
    co_word_freq_dict = {}
    co_word_freq_dict[high_freq_word] = 0
    for sub_sentence in sub_sentences:
        word_list = json.loads(sub_sentence[1])
        pos_list = json.loads(sub_sentence[0])
        # 自身重复是否可以构成pattern
        if word_list.count(high_freq_word) > 1:
            co_word_freq_dict[high_freq_word] += 1
            if co_word_freq_dict[high_freq_word] > cutoff:
                co_word_set.add(high_freq_word)
                # print(word_list)
        if high_freq_word in word_list:
            for word in word_list:
                if word != high_freq_word:

                    if word in co_word_freq_dict:
                        co_word_freq_dict[word] += 1
                    else:
                        co_word_freq_dict[word] = 0
                    if co_word_freq_dict[word] > cutoff:
                        co_word_set.add(word)
    if len(co_word_set) > 0:
        print(high_freq_word, co_word_set)
        hf_co_dict[high_freq_word] = list(co_word_set)
