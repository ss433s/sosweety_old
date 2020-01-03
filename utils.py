

###################
# 判定元组tuple1是否被包含于元组tuple2
###################
def tuple_in_tuple(tuple1, tuple2):
    if tuple1[0] >= tuple2[0] and tuple1[1] <= tuple2[1]:
        return True
    else:
        return False


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


# short_list = [1, 2, 3, 1]
# long_list = [1, 2, 3, 1,2,3,1,3, 1, 2, 3]
# rst = find_all_sub_list(short_list, long_list)
# print(rst)
