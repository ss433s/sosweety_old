import os
import sqlite3

db_path = 'data/knowledgebase/knowledgebase.db'

# 当前路径和项目root路径
this_file_path = os.path.split(os.path.realpath(__file__))[0]
# 可以根据需求改变../..
root_path = os.path.abspath(os.path.join(this_file_path, ".."))

conn = sqlite3.connect(os.path.join(root_path, db_path))
print("Opened database successfully")
cur = conn.cursor()

sql2 = 'SELECT name FROM sqlite_master where type=\'table\' order by name'
rst = cur.execute(sql2)
table_list = []
for row in rst:
    table_list.append(row[0])

for table in table_list:
    sql3 = 'SELECT * FROM %s limit 3' % table
    table_content = cur.execute(sql3)
    for line in table_content:
        print(line)
