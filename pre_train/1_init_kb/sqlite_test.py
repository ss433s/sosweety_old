import sqlite3

db_path = '../../data/database/test.db'
test_db_conn = sqlite3.connect(db_path)
print("Open database successfully")

cur = test_db_conn.cursor()

create_concept_tbl_sql = '''CREATE TABLE Concept_tbl
       (ID INT PRIMARY KEY     NOT NULL,
       Word           TEXT    NOT NULL,
       Methods        TEXT    NOT NULL,
       Prpperties     TEXT    NOT NULL);'''

create_method_tbl_sql = '''CREATE TABLE Method_tbl
       (ID INT PRIMARY KEY     NOT NULL,
       Word           TEXT    NOT NULL,
       Code        TEXT    NOT NULL);'''

create_fact_tbl_sql = '''CREATE TABLE Fact_tbl
       (ID INT PRIMARY KEY     NOT NULL,
       Concept1       INT    NOT NULL,
       Restriction1   TEXT    NOT NULL,
       Concept2       INT    NOT NULL,
       Restriction2   TEXT    NOT NULL,
       Relation       INT    NOT NULL,
       Relation_restriction   TEXT    NOT NULL,
       Time       TEXT,
       Location   TEXT,
       Confidence  REAL       NOT NULL);'''


create_word_tbl_sql = '''CREATE TABLE Word_tbl
       (ID INT PRIMARY KEY     NOT NULL,
       Word           TEXT    NOT NULL,
       Concept_id        TEXT    NOT NULL,
       Type     TEXT    NOT NULL,
       Frequece  INT    NOT NULL,
       Confidence REAL NOT NULL);'''

create_concept_relation_tbl_sql = '''CREATE TABLE Concept_relation_tbl
       (ID INT PRIMARY KEY     NOT NULL,
       Concept1       INT    NOT NULL,
       Concept2       INT    NOT NULL,
       Relation_type  INT    NOT NULL);'''

# 显示所有表
sql2 = 'SELECT name FROM sqlite_master where type=\'table\' order by name'
rst = cur.execute(sql2)
for row in rst:
    print(row)

cursor = cur.execute("SELECT id, name, address, salary  from COMPANY")
for row in cursor:
   print("ID = ", row[0])
   print("NAME = ", row[1])
   print("ADDRESS = ", row[2])
   print("SALARY = ", row[3], "\n")


test_db_conn.commit()
test_db_conn.close()

print(rst)
