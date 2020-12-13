import collections


d1 = {}
d2 = collections.OrderedDict()

d1['a'] = 1
d1['dd'] = 4
d1['c'] = 3
d1['b'] = 2


d2['a'] = 1
d2['c'] = 3
d2['b'] = 2


print(d1)
print(d2)

for key in d1.keys():
    print(key)

for key, value in d1.items():
    print(key)

my_dict = dict()
my_dict["name"] = "lowman"
my_dict["age"] = 26
my_dict["girl"] = "Tailand"
my_dict["money"] = 80
my_dict["hourse"] = None

for key, value in my_dict.items():
    print(key, value)
