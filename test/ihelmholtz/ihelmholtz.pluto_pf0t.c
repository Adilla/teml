#include <omp.h>
#include <math.h>
#define ceild(n,d)  ceil(((double)(n))/((double)(d)))
#define floord(n,d) floor(((double)(n))/((double)(d)))
#define max(x,y)    ((x) > (y)? (x) : (y))
#define min(x,y)    ((x) < (y)? (x) : (y))

/* #include <stdio.h> */
/* #include <stdlib.h> */
/* #define min(x, y) ((x) < (y)) ? ((x) : (y)) */
/* #define max(x, y) ((x) > (y)) ? ((x) : (y)) */

int main(int *argc, char **argv) {
  int N = atoi(argv[2]);
  int M = atoi(argv[1]);
  int tt1, tt2, tt3, tt4, tt5;
  double A[N][N];
  double u[M][N][N][N];
  double D[N][N][N];
  double tmp1[N][N][N];
  double tmp2[N][N][N];
  double tmp3[N][N][N];
  double tmp4[N][N][N];
  double tmp5[N][N][N];
  double tmp6[N][N][N];
  double v[M][N][N][N];

  int i1, i2, i3, i4, j1, j2, j3, j4, k1, k2, k3, k4, l1, l2, l3, i12, i22, i32,
    i42, j12, j22, j32, j42, k12, k22, k32, k42, e;

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
  for (t1=0;t1<=floord(M+N-2,32);t1++) {
    lbp=max(0,ceild(32*t1-N+1,32));
    ubp=min(floord(M-1,32),t1);
#pragma omp parallel for private(lbv,ubv,t3,t4,t5,t6,t7,t8)
    for (t2=lbp;t2<=ubp;t2++) {
      for (t3=32*t1-32*t2;t3<=min(N-1,32*t1-32*t2+31);t3++) {
        for (t4=32*t2;t4<=min(M-1,32*t2+31);t4++) {
          for (t6=0;t6<=N-1;t6++) {
            for (t7=0;t7<=N-1;t7++) {
              for (t8=0;t8<=N-1;t8++) {
                tmp1[t3][t6][t7] += A[t8][t3] * u[t4][t8][t6][t7];;
              }
            }
          }
          for (t6=0;t6<=N-1;t6++) {
            for (t7=0;t7<=N-1;t7++) {
              for (t8=0;t8<=N-1;t8++) {
                tmp2[t6][t3][t7] += A[t8][t6] * tmp1[t3][t8][t7];;
              }
            }
          }
          for (t6=0;t6<=N-1;t6++) {
            for (t7=0;t7<=N-1;t7++) {
              for (t8=0;t8<=N-1;t8++) {
                tmp3[t6][t7][t3] += A[t8][t6] * tmp2[t7][t3][t8];;
              }
            }
          }
          for (t6=0;t6<=N-1;t6++) {
            lbv=0;
            ubv=N-1;
#pragma ivdep
#pragma vector always
            for (t7=lbv;t7<=ubv;t7++) {
              tmp4[t6][t7][t3] = D[t6][t7][t3] * tmp3[t6][t7][t3];;
            }
          }
          for (t6=0;t6<=N-1;t6++) {
            for (t7=0;t7<=N-1;t7++) {
              for (t8=0;t8<=N-1;t8++) {
                tmp5[t6][t7][t3] += A[t6][t8] * tmp4[t8][t7][t3];;
              }
            }
          }
          for (t6=0;t6<=N-1;t6++) {
            for (t7=0;t7<=N-1;t7++) {
              for (t8=0;t8<=N-1;t8++) {
                tmp6[t6][t7][t3] += A[t6][t8] * tmp5[t7][t8][t3];;
              }
            }
          }
          for (t6=0;t6<=N-1;t6++) {
            for (t7=0;t7<=N-1;t7++) {
              lbv=0;
              ubv=N-1;
#pragma ivdep
#pragma vector always
              for (t8=lbv;t8<=ubv;t8++) {
                v[t4][t6][t7][t8] += A[t6][t3] * tmp6[t7][t8][t3];;
              }
            }
          }
        }
      }
    }
  }
}
/* End of CLooG code */
  double end = omp_get_wtime();
  printf("Time: %f ms\n", end - begin);
  return 0;
}
