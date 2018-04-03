#!/bin/bash

source=$1

for i in {10..10}
do
    cp $1.ivie $1_$i.ivie
    sed -i 's/N/'$i'/g' $1_$i.ivie 

    python ../../ivic.py $1_$i.ivie
done 
