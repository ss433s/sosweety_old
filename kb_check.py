import os
import sqlite3
import time

# 当前路径和项目root路径， 可以根据需求改变../..
this_file_path = os.path.split(os.path.realpath(__file__))[0]
root_path = this_file_path

# 数据库路径 诡异的bug 不能在vscode的目录里
root_path_up = os.path.abspath(os.path.join(root_path, ".."))
db_path = 'data/knowledgebase/knowledgebase.db'
new_db_path = os.path.join(root_path_up, db_path)

conn = sqlite3.connect(new_db_path)
print("Opened database successfully")
cur = conn.cursor()

sql2 = 'SELECT name FROM sqlite_master where type=\'table\' order by name'
rst = cur.execute(sql2)
table_list = []
for row in rst:
    table_list.append(row[0])

# for table in table_list:
#     print('--------' + table + '------------')
#     sql3 = 'SELECT * FROM %s limit 10' % table
#     table_content = cur.execute(sql3)
#     for line in table_content:
#         print(line)

# print('--------some test------------')
# word = '国家'
# sql_test = 'select Item_id from Word_tbl where Word=?'
# rst = cur.execute(sql_test, [word])
# for row in rst:
#     print(row)

# print('--------concept downstream------------')
# word = '社会'
# select_sql = "SELECT Concept1, Concept_tbl.Word, Concept2 FROM Concept_relation_tbl LEFT OUTER JOIN \
#                     Concept_tbl ON Concept_relation_tbl.Concept2 = Concept_tbl.Concept_id where Concept1 in (select Item_id from Word_tbl where Word= ? and Type=0)"
# rst = cur.execute(select_sql, [word]).fetchall()
# for row in rst:
#     print(row)
# print(len(rst))

print('--------concept check------------')
word = '国家地理'
sql_test = "select * from Word_tbl where word='国家地理'"
# sql_test = "select * from Word_tbl where substr(Word,1,4)='国家地理'"


# # sql_test = "select * from Word_tbl where Word LIKE '国家%'"
# def check_word(word):
#     sql_test = "select Word from Word_tbl where Word LIKE '国家%'"
#     rst = cur.execute(sql_test).fetchall()
#     new_dict = {}
#     # print(len(rst.fetchall()))
#     for row in rst:
#         word = row[0]
#         # print(word)

# check_word(word)
print(time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime()))
for i in range(100000):
    rst = cur.execute(sql_test)
    # check_word(word)
    # break
print(time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime()))
print(len(rst.fetchall()))
for row in rst:
    print(row)
