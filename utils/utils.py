import os

this_file_path = os.path.split(os.path.realpath(__file__))[0]


###################
# 判定元组tuple1是否被包含于元组tuple2
###################
def tuple_in_tuple(tuple1, tuple2):
    if tuple1[0] >= tuple2[0] and tuple1[1] <= tuple2[1]:
        return True
    else:
        return False


###################
# stanford 的postag 是列表，列表元素是（词，词性）的元组
# 该函数用于简化Stanford corenlp的词性结果
###################
def stanford_simplify(pos_tags):
    stanford_simplify_dict = {}
    file_path = os.path.join(this_file_path, 'stanford_simplify')
    with open(file_path) as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip().split('\t')
            stanford_simplify_dict[line[0]] = line[1]
    result = []
    for word, pos_tag in pos_tags:
        result.append((word, stanford_simplify_dict[pos_tag]))
    return result


###################
# 找子串
###################
def find_all_sub_list(short_list, long_list):
    result = []
    for i in range(len(long_list)):
        if long_list[i] == short_list[0]:
            if i + len(short_list) <= len(long_list):
                full_match = True
                for j in range(len(short_list)):
                    if short_list[j] != long_list[i+j]:
                        full_match = False
                if full_match:
                    result.append(i)
    return result
