import json
# import pandas as pd
# import numpy as np
# from sParser import hanlp_parse
# from stanfordcorenlp import StanfordCoreNLP
# nlp = StanfordCoreNLP(r'/Users/guoyu/Documents/supports/stanford-corenlp/stanford-corenlp-full-2018-10-05/', lang='zh')

from knowledgebase import word2id_dict

with open('./init_data/train_data.json') as test_file:
    with open('../data/fake_database/Concept_relation_table', 'w') as f:
        f.write('# concept1\tconcept2\trelation_type(0: belong_to)\n')
        lines = test_file.readlines()
        for i in range(len(lines)):
            data = json.loads(lines[i])
            for spo in data['spo_list']:
                object_type_id = word2id_dict[spo['object_type']][0][0]
                subject_type_id = word2id_dict[spo['subject_type']][0][0]
                object_id = word2id_dict[spo['object']][0][0]
                subject_id = word2id_dict[spo['subject']][0][0]

                f.write(str(object_id) + '\t' + str(object_type_id) + '\t0\n')
                f.write(str(subject_id) + '\t' + str(subject_type_id) + '\t0\n')
