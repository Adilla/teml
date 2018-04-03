#include <omp.h>
#include <math.h>
#define ceild(n,d)  ceil(((double)(n))/((double)(d)))
#define floord(n,d) floor(((double)(n))/((double)(d)))
#define max(x,y)    ((x) > (y)? (x) : (y))
#define min(x,y)    ((x) < (y)? (x) : (y))

#include <stdio.h>
#include <stdlib.h>
#define min(x, y) ((x) < (y) ? (x) : (y))
#define max(x, y) ((x) > (y) ? (x) : (y))

int main(int *argc, char **argv) {

  int N = atoi(argv[2]);
  int M = atoi(argv[1]);

  double rt[M][N][N][N];
  double ut[M][N][N][N];
  double L[N][N];
  double w[N];


  int i1, i2, i3, j1, j2, j3, j4, k1, k2, k3, k4, l1, l2, l3, l4;

  int i, j, k, l;

  for (i = 0; i < N; i++) {
    w[i] = i + 15;
    for (j = 0; j < N; j++) {
      L[i][j] = i + j + 1;
    }
  }
  for (i = 0; i < M; i++) {
    for (j = 0; j < N; j++) {
      for (k = 0; k < N; k++) {
        for (l = 0; l < N; l++)
          ut[i][j][k][l] = i * j + 10;
	rt[i][j][k][l] = 0;
      }
    }
  }
  int e;
  double begin = omp_get_wtime();
/* Copyright (C) 1991-2014 Free Software Foundation, Inc.
   This file is part of the GNU C Library.

   The GNU C Library is free software; you can redistribute it and/or
   modify it under the terms of the GNU Lesser General Public
   License as published by the Free Software Foundation; either
   version 2.1 of the License, or (at your option) any later version.

   The GNU C Library is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
   Lesser General Public License for more details.

   You should have received a copy of the GNU Lesser General Public
   License along with the GNU C Library; if not, see
   <http://www.gnu.org/licenses/>.  */
/* This header is separate from features.h so that the compiler can
   include it implicitly at the start of every compilation.  It must
   not itself include <features.h> or any other header that includes
   <features.h> because the implicit include comes before any feature
   test macros that may be defined in a source file before it first
   explicitly includes a system header.  GCC knows the name of this
   header in order to preinclude it.  */
/* glibc's intent is to support the IEC 559 math functionality, real
   and complex.  If the GCC (4.9 and later) predefined macros
   specifying compiler intent are available, use them to determine
   whether the overall intent is to support these features; otherwise,
   presume an older compiler has intent to support these features and
   define these macros by default.  */
/* wchar_t uses ISO/IEC 10646 (2nd ed., published 2011-03-15) /
   Unicode 6.0.  */
/* We do not support C11 <threads.h>.  */
  int t1, t2, t3, t4, t5, t6, t7, t8;
 int lb, ub, lbp, ubp, lb2, ub2;
 register int lbv, ubv;
/* Start of CLooG code */
if ((M >= 1) && (N >= 1)) {
  lbp=0;
  ubp=M-1;
#pragma omp parallel for private(lbv,ubv,t3,t4,t5,t6,t7,t8)
  for (t2=lbp;t2<=ubp;t2++) {
    for (t3=0;t3<=N-1;t3++) {
      for (t4=0;t4<=N-1;t4++) {
        lbv=0;
        ubv=N-1;
#pragma ivdep
#pragma vector always
        for (t5=lbv;t5<=ubv;t5++) {
          rt[t2][t3][t4][t5] += w[t3] * w[t4] * w[t5] * ut[t2][t3][t4][t5];;
        }
      }
    }
  }
  lbp=0;
  ubp=M-1;
#pragma omp parallel for private(lbv,ubv,t3,t4,t5,t6,t7,t8)
  for (t2=lbp;t2<=ubp;t2++) {
    for (t3=0;t3<=N-1;t3++) {
      for (t4=0;t4<=N-1;t4++) {
        for (t5=0;t5<=N-1;t5++) {
          for (t8=0;t8<=N-1;t8++) {
            rt[t2][t3][t4][t5] += L[t3][t8] * w[t4] * w[t5] * ut[t2][t8][t4][t5];;
          }
          for (t8=0;t8<=N-1;t8++) {
            rt[t2][t3][t4][t5] += w[t3] * L[t4][t8] * w[t5] * ut[t2][t3][t8][t5];;
          }
          for (t8=0;t8<=N-1;t8++) {
            rt[t2][t3][t4][t5] += w[t3] * w[t4] * L[t5][t8] * ut[t2][t3][t4][t8];;
          }
        }
      }
    }
  }
}
/* End of CLooG code */
  double end = omp_get_wtime();
  printf("Time: %f ms\n", end - begin);

  /* for (j = 0; j < 3; j++) */
  /*   for (k = 0; k < 3; k++) */
  /*     for (l = 0; l < 3; l++) */
  /*       printf("%.0f  ", rt[j][k][l]); */

  /* printf("\n"); */

  return 0;
}

