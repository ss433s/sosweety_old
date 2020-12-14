import os
import json
import sqlite3


# 当前路径和项目root路径， 可以根据需求改变../..
this_file_path = os.path.split(os.path.realpath(__file__))[0]
root_path = os.path.abspath(os.path.join(this_file_path, "../.."))

# 数据库路径 诡异的bug 不能在vscode的目录里
root_path_up = os.path.abspath(os.path.join(root_path, ".."))
db_path = 'data/knowledgebase/knowledgebase.db'
new_db_path = os.path.join(root_path_up, db_path)

kb_db_conn = sqlite3.connect(new_db_path)
print("Opened database successfully")
cur = kb_db_conn.cursor()


def find_rules(concept1_list, concept2):

    # 前1-2个字和前N个字（N=len（concept2））
    # 后1-2个字和后N个字（N=len（concept2））
    # ??中间出现concept2

    length = len(concept2)
    f_words = []
    b_words = []
    for concept1 in concept1_list:
        char_1 = concept1[0]
        char_r1 = concept1[-1]
        f_words.append(char_1)
        b_words.append(char_r1)
        if len(concept1) >= 2:
            char_12 = concept1[0:2]
            char_r12 = concept1[-2:]
            f_words.append(char_12)
            b_words.append(char_r12)
        if length > 2 and len(concept1) >= length:
            char_n = concept1[0:length]
            char_rn = concept1[0-length:]
            f_words.append(char_n)
            b_words.append(char_rn)





    return


###################
# 获取所有二级以上concept
###################
high_level_concept_id2word_dict = {}
select_sql = "SELECT Concept2, Concept_tbl.Word FROM Concept_relation_tbl LEFT OUTER JOIN \
                Concept_tbl ON Concept_relation_tbl.Concept2 = Concept_tbl.Concept_id LIMIT 100000"
result = cur.execute(select_sql)
count = 0
for row in result:
    count += 1
    if count % 100000 == 0:
        print('check %s relations' % count)
    concept_id = row[0]
    high_level_concept_id2word_dict[row[0]] = row[1]

for concept_id, word in high_level_concept_id2word_dict.items():
    sub_concept_words = set()
    select_sql = "SELECT Concept1, Concept_tbl.Word FROM Concept_relation_tbl LEFT OUTER JOIN \
                    Concept_tbl ON Concept_relation_tbl.Concept1 = Concept_tbl.Concept_id where Concept2 = ? LIMIT 100000"
    result = cur.execute(select_sql, [str(concept_id)])
    for row in result:
        sub_concept_words.add(row[1])
    find_rules(list(sub_concept_words), word)
    break





file = './init_data/parse_file_total'
unsolvable_ss_file = open(file)

# 开始finder 定义参数
cutoff = 1000


# phrase str提取
phrase_strs = []
for phrase_pattern in phrase_patterns:
    phrase_strs.append(phrase_pattern.symbol)


# parse result构建
def tuples2parse_result(tuples):
    content = []
    for word in tuples:
        tmp_word = Word(word[0], word[1])
        content.append(tmp_word)
    parse_result = Parse_result(content)
    return parse_result


# 查出某个词所有的潜在隶属于的concept
# todo 目前仅限直属，可以考虑拓展
def get_word_relations(word):
    word_relations = []
    word_ids = KB.get_word_ids(word)
    for word_id in word_ids:
        if word_id[1] == 'concept':
            single_concept_relations = KB.get_concept_relations(word_id[0])
            for single_concept_relation in single_concept_relations:
                if single_concept_relation not in word_relations:
                    word_relations.append(single_concept_relation)
    return word_relations


# 强行遍历各种可能性2-3个词
def checkout_concept_phrase(parse_result):

    def create_feature(word_relation):
        feature = {}
        feature['concept'] = word_relation[0]
        feature['word'] = KB.get_concept_word(word_relation[0])
        return feature

    concept_phrases = []
    for i in range(len(parse_result.contents)-1):
        item = parse_result.contents[i]
        next_item = parse_result.contents[i+1]
        item_concept_phrases = []
        phrase_str = '|'.join([item.pos_tag, next_item.pos_tag])
        if phrase_str in phrase_strs:
            word_relations = get_word_relations(item.value)
            if len(word_relations) > 0:
                next_word_relations = get_word_relations(next_item.value)
                for word_relation in word_relations:
                    feature1 = create_feature(word_relation)
                    for next_word_relation in next_word_relations:
                        feature2 = create_feature(next_word_relation)
                        # concept_phrase = [feature1, feature2, item.value, next_item.value]
                        concept_phrase = [feature1, feature2]
                        item_concept_phrases.append(concept_phrase)
                    feature2 = {}
                    feature2['word'] = next_item.value
                    # item_concept_phrases.append([feature1, feature2, item.value, next_item.value])
                    item_concept_phrases.append([feature1, feature2])
        if i < len(parse_result.contents) - 2:
            item_concept_phrases3 = []
            next_next_item = parse_result.contents[i+2]
            phrase_str = '|'.join([item.pos_tag, next_item.pos_tag, next_next_item.pos_tag])
            if phrase_str in phrase_strs:
                next_next_word_relations = get_word_relations(next_next_item.value)
                for concept_phrase in item_concept_phrases:
                    for word_relation in next_next_word_relations:
                        feature3 = create_feature(word_relation)
                        # concept_phrase3 = concept_phrase + [feature3, next_next_item.value]
                        concept_phrase3 = concept_phrase + [feature3]
                        item_concept_phrases3.append(concept_phrase3)
                    feature3 = {}
                    feature3['word'] = next_next_item.value
                    # item_concept_phrases3.append(concept_phrase + [feature3, next_next_item.value])
                    item_concept_phrases3.append(concept_phrase + [feature3])
                item_concept_phrases += item_concept_phrases3
        concept_phrases += item_concept_phrases

    return concept_phrases


lines = unsolvable_ss_file.readlines()
total_concept_phrase = []
for i in range(len(lines)):
    if i % 3000 == 0:
        print('parsed %s sentence, total ~170000' % i)

    line = lines[i].split('\t')
    parse_str = line[0]
    pos_tags = json.loads(line[1].strip())
    pos_tags = stanford_simplify(pos_tags)

    tmp_stamp = 0
    for i in range(len(pos_tags)):
        pos_tag = pos_tags[i]
        if pos_tag[0] in ['。', '！', '？', '?', '，', ',', ';', '；']:
            ss_parse_result = tuples2parse_result(pos_tags[tmp_stamp: i])
            tmp_stamp = i + 1
            total_concept_phrase += checkout_concept_phrase(ss_parse_result)
    if tmp_stamp < len(pos_tags):
        ss_parse_result = tuples2parse_result(pos_tags[tmp_stamp: len(pos_tags)])
        total_concept_phrase += checkout_concept_phrase(ss_parse_result)

with open('./init_data/all_concept_phrases', 'w') as f:
    for i in total_concept_phrase:
        f.write(json.dumps(i, ensure_ascii=False) + '\n')


# pandas排序去重，不能是json，直接读字符串就行, 写csv速度更快
# with open('./init_data/123') as f:
with open('./init_data/all_concept_phrases') as f:
    total_concept_phrase = []
    lines = f.readlines()
    for line in lines:
        line = line.strip()
        # concept_phrase = json.loads(line)
        total_concept_phrase.append(line)

    df_dict = {}
    df_dict['concept_phrase'] = total_concept_phrase
    df = pd.DataFrame(df_dict)
    df2 = df.concept_phrase.value_counts()
    df3_dict = {'label': df2.index, 'count': df2.values}
    df3 = pd.DataFrame(df3_dict)
    with open('./init_data/all_concept_phrases_stat', 'w') as result_file:
        for i in range(len(df3)):
            result_file.write(df3['label'][i] + '\t' + str(df3['count'][i]) + '\n')
    # df2.to_csv('./init_data/123stat.csv')
