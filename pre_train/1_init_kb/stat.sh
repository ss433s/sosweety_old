echo "123" #>$1_stamp
# awk 'BEGIN{FS="\t"}{if ($0 in a) {a[$0]++} else {a[$0]=1} }'END'{for(i=1;i<=asorti(a,Ta);i++) print Ta[i] FS a[Ta[i]]}' $1 >$1_tmp
# awk 'BEGIN{FS="\t"}{if ($0 in a) {a[$0]++} else {a[$0]=1} }'END'{asort(a,b);for(i=1;i<=length(b);i++) print a[i] FS b[i]}' $1 >$1_tmp
# awk 'BEGIN{FS="\t"}{if ($0 in a) {a[$0]++} else {a[$0]=1} }'END'{n=asort(a,b);for(i in a) print i FS a[i]}' $1 >$1_tmp

awk 'BEGIN{FS="\t"}{if ($0 in a) {a[$0]++} else {a[$0]=1} }'END'{for(i in a) print i FS a[i]}' $1 >$1_tmp
sort -t $'\t' -k2 -nr $1_tmp >$1_stat
rm $1_tmp
echo "321"