#!/bin/bash

code=`cat interpolation.ivie`

for ((k=2; k<15; k++ ));
do

    mkdir with_align/$k
    ## Create code for data set k
    echo "$code" | sed 's/N/'$k'/g' > with_align/$k/interpolation_$k.ivie

    cp with_align/$k/interpolation_$k.ivie interpolation.ivie
    
    echo "for (tt1 = 0; tt1 < "$k"; tt1++)" >> init.txt
    echo "  for (tt2 = 0; tt2 < "$k"; tt2++)" >> init.txt
    echo "    A[tt1][tt2] = tt1 + tt2 + 5;" >> init.txt
    echo "                                 " >> init.txt
    echo "for (e = 0; e < 512; e++)" >> init.txt
    echo "  for (tt1 = 0; tt1 < "$k"; tt1++)" >> init.txt
    echo "    for (tt2 = 0; tt2 < "$k"; tt2++)" >> init.txt
    echo "      for (tt3 = 0; tt3 < "$k"; tt3++) {" >> init.txt
    echo "        u[e][tt1][tt2][tt3] = tt1 * tt2 + 5;" >> init.txt
    echo "        v[e][tt1][tt2][tt3] = 0;" >> init.txt
    echo "        tmp1[e][tt1][tt2][tt3] = 0;" >> init.txt
    echo "        tmp2[e][tt1][tt2][tt3] = 0;" >> init.txt
    echo "      }" >> init.txt
    
    python ../../ivic.py interpolation.ivie

    variants=($(ls -d [v]*))
    input='interpolation'
    v='variant'
    n=${#variants[@]}

    for (( i=2; i<$(($n+2)); i++ ));
    do
    	cat with_align/$k/interpolation_$k.ivie ${variants[i]} > with_align/$k/$input'_'$k'_'$v$i.ivie
    done
    rm $v*
    for (( i=2; i<$(($n+2)); i++ ));
    do
    	python ../../ivic.py with_align/$k/$input'_'$k'_'$v$i.ivie > prog
    	cat head.txt prog > with_align/$k/$input'_'$k'_'$v$i.c
    done
    rm $v*
    rm init.txt

    # Restore initial file
    echo "$code" > interpolation.ivie
done 
