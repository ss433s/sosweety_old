

###################
# 判定元组tuple1是否被包含于元组tuple2
###################
def tuple_in_tuple(tuple1, tuple2):
    if tuple1[0] >= tuple2[0] and tuple1[1] <= tuple2[1]:
        return True
    else:
        return False
