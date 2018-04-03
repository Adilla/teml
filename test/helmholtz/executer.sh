#!/bin/bash

# Generate all versions
python code_generator.py

# Execute
for i in *.ivie;
do
    echo $i
    rm ${i%ivie}c
   
    echo "#include <stdio.h>" >> ${i%ivie}c
    echo "#include <stdlib.h>" >> ${i%ivie}c
    echo "#include <omp.h>" >> ${i%ivie}c
    echo "#define min(x, y) ((x) < (y) ? (x) : (y))" >> ${i%ivie}c
    echo "#define max(x, y) ((x) > (y) ? (x) : (y))" >> ${i%ivie}c
    echo "#define N 50" >> ${i%ivie}c
    echo " " >> ${i%ivie}c
  
    python ../../ivic.py $i >> ${i%ivie}c
    clang-format-3.5 ${i%ivie}c >> tmp
    mv tmp ${i%ivie}c
    
done

make clean
make all
