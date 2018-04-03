#!/bin/bash

### Different type of generated code
###     interpolation_none.ivie: no instruction for vectorization
###     interpolation_align.ivie: #pragma align
###     interpolation_ivdep_always: (no align)#pragma ivdep and vector always added
###     interpolation_full: align + ivdep + always
### Vectorization is specified on innermost dimension for the moment. 

### Slight temporary code modification in ivie/src/backend/C_backend.py, line 206: 
###     Vectorization instruction prints ivdep and always pragmas 


path=vectorization_study
none=$path/none
align=$path/align
hints=$path/hints
all=$path/all

rm -rf $path 
mkdir $path $none $align $hints $all


# code1=`cat interpolation.ivie`
# code2=`cat interpolation_vec.ivie`

# code=`cat interpolation.ivie`

input=interpolation.ivie
align_instr="__align(A, u, tmp1, tmp2, v)"
hints_instr="__simd_hints(i4, j4, k4)"

code=`cat $input`
for ((k=2; k<15; k++ ));
do
    # # rm prog init.txt
    # # rm -fr vectorization_study/$k
    # # mkdir vectorization_study/$k
    # ## Create code for data set k
    
    nonek=$none/$k
    alignk=$align/$k
    hintsk=$hints/$k
    allk=$all/$k

    mkdir $nonek $alignk $hintsk $allk

    ## None
    echo "$code" | sed 's/N/'$k'/g' > $nonek/interpolation_$k.ivie

    ## Align only
    cp $nonek/interpolation_$k.ivie $alignk/interpolation_align_$k.ivie
    echo $align_instr >> $alignk/interpolation_align_$k.ivie

    ## Hints only
    cp $nonek/interpolation_$k.ivie $hintsk/interpolation_hints_$k.ivie
    echo $hints_instr >> $hintsk/interpolation_hints_$k.ivie

    ## All
    cp $alignk/interpolation_align_$k.ivie $allk/interpolation_all_$k.ivie
    echo $hints_instr >> $allk/interpolation_all_$k.ivie

    cp $nonek/interpolation_$k.ivie interpolation.ivie
    cp $alignk/interpolation_align_$k.ivie interpolation_align.ivie
    cp $hintsk/interpolation_hints_$k.ivie interpolation_hints.ivie
    cp $allk/interpolation_all_$k.ivie interpolation_all.ivie
    
    echo "for (tt1 = 0; tt1 < "$k"; tt1++)" >> init.txt
    echo "  for (tt2 = 0; tt2 < "$k"; tt2++)" >> init.txt
    echo "    A[tt1][tt2] = tt1 + tt2 + 5;" >> init.txt
    echo "                                 " >> init.txt
    echo "for (e = 0; e < 216; e++)" >> init.txt
    echo "  for (tt1 = 0; tt1 < "$k"; tt1++)" >> init.txt
    echo "    for (tt2 = 0; tt2 < "$k"; tt2++)" >> init.txt
    echo "      for (tt3 = 0; tt3 < "$k"; tt3++) {" >> init.txt
    echo "        u[e][tt1][tt2][tt3] = tt1 * tt2 + 5;" >> init.txt
    echo "        v[e][tt1][tt2][tt3] = 0;" >> init.txt
    echo "        tmp1[e][tt1][tt2][tt3] = 0;" >> init.txt
    echo "        tmp2[e][tt1][tt2][tt3] = 0;" >> init.txt
    echo "      }" >> init.txt
    
    python ../../ivic.py interpolation.ivie > prog
    python ../../ivic.py interpolation_align.ivie > prog_align
    python ../../ivic.py interpolation_hints.ivie > prog_hints
    python ../../ivic.py interpolation_all.ivie > prog_all

    cat head.txt prog > $nonek/interpolation_$k.c
    cat head.txt prog_align > $alignk/interpolation_align_$k.c
    cat head.txt prog_hints > $hintsk/interpolation_hints_$k.c
    cat head.txt prog_all > $allk/interpolation_all_$k.c

    rm init.txt prog prog_align prog_hints prog_all interpolation.ivie interpolation_align.ivie interpolation_hints.ivie interpolation_all.ivie

    ## Generate logs for verbosity = 1
    
    icc -O3 -qopenmp -qopt-report=1 -qopt-report-phase=vec,loop -qopt-report-file=$nonek/haswell_$k.1.log $nonek/interpolation_$k.c -o $nonek/interpolation_$k

    icc -O3 -qopenmp -qopt-report=1 -qopt-report-phase=vec,loop -qopt-report-file=$alignk/haswell_align_$k.1.log $alignk/interpolation_align_$k.c -o $alignk/interpolation_align_$k

    icc -O3 -qopenmp -qopt-report=1 -qopt-report-phase=vec,loop -qopt-report-file=$hintsk/haswell_hints_$k.1.log $hintsk/interpolation_hints_$k.c -o $hintsk/interpolation_hints_$k

    icc -O3 -qopenmp -qopt-report=1 -qopt-report-phase=vec,loop -qopt-report-file=$allk/haswell_all_$k.1.log $allk/interpolation_all_$k.c -o $allk/interpolation_all_$k



    ## Generate logs for verbosity = 2

    icc -O3 -qopenmp -qopt-report=2 -qopt-report-phase=vec,loop -qopt-report-file=$nonek/haswell_$k.2.log $nonek/interpolation_$k.c -o $nonek/interpolation_$k

    icc -O3 -qopenmp -qopt-report=2 -qopt-report-phase=vec,loop -qopt-report-file=$alignk/haswell_align_$k.2.log $alignk/interpolation_align_$k.c -o $alignk/interpolation_align_$k

    icc -O3 -qopenmp -qopt-report=2 -qopt-report-phase=vec,loop -qopt-report-file=$hintsk/haswell_hints_$k.2.log $hintsk/interpolation_hints_$k.c -o $hintsk/interpolation_hints_$k

    icc -O3 -qopenmp -qopt-report=2 -qopt-report-phase=vec,loop -qopt-report-file=$allk/haswell_all_$k.2.log $allk/interpolation_all_$k.c -o $allk/interpolation_all_$k



    ## Generate logs for verbosity = 5

    icc -O3 -qopenmp -qopt-report=5 -qopt-report-phase=vec,loop -qopt-report-file=$nonek/haswell_$k.5.log $nonek/interpolation_$k.c -o $nonek/interpolation_$k

    icc -O3 -qopenmp -qopt-report=5 -qopt-report-phase=vec,loop -qopt-report-file=$alignk/haswell_align_$k.5.log $alignk/interpolation_align_$k.c -o $alignk/interpolation_align_$k

    icc -O3 -qopenmp -qopt-report=5 -qopt-report-phase=vec,loop -qopt-report-file=$hintsk/haswell_hints_$k.5.log $hintsk/interpolation_hints_$k.c -o $hintsk/interpolation_hints_$k

    icc -O3 -qopenmp -qopt-report=5 -qopt-report-phase=vec,loop -qopt-report-file=$allk/haswell_all_$k.5.log $allk/interpolation_all_$k.c -o $allk/interpolation_all_$k


    # # variants=($(ls -d [v]*))
    # # input='interpolation'
    # # v='variant'
    # # n=${#variants[@]}

    # # for (( i=2; i<$(($n+2)); i++ ));
    # # do
    # # 	cat vectorization_study/$k/interpolation_$k.ivie ${variants[i]} > vectorization_study/$k/$input'_'$k'_'$v$i.ivie
    # # done
    # # rm $v*
    # # for (( i=2; i<$(($n+2)); i++ ));
    # # do
    # # 	python ../../ivic.py vectorization_study/$k/$input'_'$k'_'$v$i.ivie > prog
    # # 	cat head.txt prog > vectorization_study/$k/$input'_'$k'_'$v$i.c
    # # done
    # # rm $v*
    # # rm init.txt

    #Restore initial file
    cp interpolation_N.ivie $input
done 

