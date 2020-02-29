import json

with open('test_pattern') as test_file:
    with open('new_test_file', 'w') as new_test_file:
        lines = test_file.readlines()
        del(lines[0])
        for line in lines:
            line = line.strip().split()
            pos_tags = line[1].split('|')
            features = []
            for pos_tag in pos_tags:
                feature = {}
                feature['pos_tag'] = pos_tag
                features.append(feature)
            phrase_pattern = [line[0], json.dumps(features, ensure_ascii=False), line[2], line[3], line[4]]
            new_test_file.write('\t'.join(phrase_pattern) + '\n')
