#!/bin/bash

code=`cat interpolation.ivie`
po=$1


echo "$code" | sed 's/N/'$1'/g' > testing_$1.ivie

echo "for (tt1 = 0; tt1 < "$1"; tt1++)" >> init.txt
echo "  for (tt2 = 0; tt2 < "$1"; tt2++)" >> init.txt
echo "    A[tt1][tt2] = tt1 + tt2 + 5;" >> init.txt
echo "                                 " >> init.txt
echo "for (e = 0; e < 512; e++)" >> init.txt
echo "  for (tt1 = 0; tt1 < "$1"; tt1++)" >> init.txt
echo "    for (tt2 = 0; tt2 < "$1"; tt2++)" >> init.txt
echo "      for (tt3 = 0; tt3 < "$1"; tt3++) {" >> init.txt
echo "        u[e][tt1][tt2][tt3] = tt1 * tt2 + 5;" >> init.txt
echo "        v[e][tt1][tt2][tt3] = 0;" >> init.txt
echo "        tmp1[e][tt1][tt2][tt3] = 0;" >> init.txt
echo "        tmp2[e][tt1][tt2][tt3] = 0;" >> init.txt
echo "      }" >> init.txt

