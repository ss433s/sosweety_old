import json
# import pandas as pd
from sParser import Word, Parse_result, stanford_simplify, KB


###################
# 读取待处理文件
# to do
# 准备提供对外接口处理不同文件
###################
file = './init_data/parse_file_total'
unsolvable_ss_file = open(file)

# 开始finder 定义参数
cutoff = 1000


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


# pandas排序去重，超级慢，不如awk
# with open('./init_data/123') as f:
# with open('./init_data/all_concept_phrases') as f:
#     total_concept_phrase = []
#     lines = f.readlines()
#     for line in lines:
#         line = line.strip()
#         concept_phrase = json.loads(line)
#         total_concept_phrase.append(concept_phrase)

#     df_dict = {}
#     df_dict['concept_phrase'] = total_concept_phrase
#     df = pd.DataFrame(df_dict)
#     df2 = df.concept_phrase.value_counts()
#     df2.to_csv('./init_data/123stat.csv')
