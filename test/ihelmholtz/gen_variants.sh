#!/bin/bash



variants=($(ls -d [v]*))
input=$1
v='variant'
n=${#variants[@]}

for (( i=0; i<$n; i++ ));
do
    cat $input.ivie ${variants[i]} > $input'_'$v$i.ivie
done

rm $v*


for (( i=0; i<$n; i++ ));
do
    python ../../ivic.py $input'_'$v$i.ivie > prog
    cat head.txt prog > $input'_'$v$i.c
done

rm $v*
