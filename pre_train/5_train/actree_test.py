import os, time
import ahocorasick
import sqlite3


# 当前路径和项目root路径
this_file_path = os.path.split(os.path.realpath(__file__))[0]
# 可以根据需求改变../..
root_path = os.path.abspath(os.path.join(this_file_path, "../.."))

# 数据库路径 诡异的bug 不能在vscode的目录里
root_path_up = os.path.abspath(os.path.join(root_path, ".."))
db_dir = 'data/knowledgebase/'
db_file = 'knowledgebase.db'
db_dir = os.path.join(root_path_up, db_dir)
if not os.path.exists(db_dir):
    os.makedirs(db_dir)
new_db_path = os.path.join(db_dir, db_file)

kb_db_conn = sqlite3.connect(new_db_path)
print("Open database successfully")

cur = kb_db_conn.cursor()
sql_test = "select Word from Word_tbl"
rst = cur.execute(sql_test)

B = ahocorasick.Automaton()
print(time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime()))
count = 0
for word in rst:
    count += 1
    if count % 1000000 == 0:
        print('add %s word' % count)
    word = word[0]
    B.add_word(word, word)
print(time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime()))
B.make_automaton()
print(time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime()))
