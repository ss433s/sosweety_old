# cut -f1 -d "|" datasets/nsubj_pr_stat|sort -u >init_data/subj 
# cut -f1 -d "|" datasets/dobj_pr_stat |sort -u >init_data/obj
cut -f1 datasets/amod_pr_stat |cut -f2 -d "|" |sort -u >init_data/amod_noun 

# 过actree之前的操作
# cat init_data/obj init_data/subj init_data/entities init_data/amod_noun init_data/known_entities |sort -u >init_data/all_entities 

cat init_data/used_entities_total_uniq init_data/amod_noun init_data/known_entities |sort -u >init_data/all_entities 
rm init_data/subj 
rm init_data/obj 
rm init_data/amod_noun 
