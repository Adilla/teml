#include <stdio.h>
#include <stdlib.h>
#include <omp.h>


int main() {

int tt1, tt2, tt3, tt4, e;
double A[11][11] __attribute__((aligned(64)));
double u[512][11][11][11] __attribute__((aligned(64)));
double tmp1[512][11][11][11] __attribute__((aligned(64)));
double tmp2[512][11][11][11] __attribute__((aligned(64)));
double v[512][11][11][11] __attribute__((aligned(64)));

int i1, i2, i4, j1, j2, j4, k1, k2, k4;

for (tt1 = 0; tt1 < 11; tt1++)
  for (tt2 = 0; tt2 < 11; tt2++)
    A[tt1][tt2] = tt1 + tt2 + 5;
                                 
for (e = 0; e < 512; e++)
  for (tt1 = 0; tt1 < 11; tt1++)
    for (tt2 = 0; tt2 < 11; tt2++)
      for (tt3 = 0; tt3 < 11; tt3++) {
        u[e][tt1][tt2][tt3] = tt1 * tt2 + 5;
        v[e][tt1][tt2][tt3] = 0;
        tmp1[e][tt1][tt2][tt3] = 0;
        tmp2[e][tt1][tt2][tt3] = 0;
      }

double begin = omp_get_wtime();
for (e = 0; e < 512; e++) {
for(i1 = 0; i1 < 11; i1 += 1) {
 #pragma vector aligned
#pragma simd
 for(i2 = 0; i2 < 11; i2 += 1) {
  for(i4 = 0; i4 < 11; i4 += 1) {
   tmp1[e][i1][i2][0] += A[i1][i4] * u[e][i4][i2][0];
   tmp1[e][i1][i2][1] += A[i1][i4] * u[e][i4][i2][1];
   tmp1[e][i1][i2][2] += A[i1][i4] * u[e][i4][i2][2];
   tmp1[e][i1][i2][3] += A[i1][i4] * u[e][i4][i2][3];
   tmp1[e][i1][i2][4] += A[i1][i4] * u[e][i4][i2][4];
   tmp1[e][i1][i2][5] += A[i1][i4] * u[e][i4][i2][5];
   tmp1[e][i1][i2][6] += A[i1][i4] * u[e][i4][i2][6];
   tmp1[e][i1][i2][7] += A[i1][i4] * u[e][i4][i2][7];
   tmp1[e][i1][i2][8] += A[i1][i4] * u[e][i4][i2][8];
   tmp1[e][i1][i2][9] += A[i1][i4] * u[e][i4][i2][9];
   tmp1[e][i1][i2][10] += A[i1][i4] * u[e][i4][i2][10];
   }
  }
 }
for(j1 = 0; j1 < 11; j1 += 1) {
 #pragma vector aligned
#pragma simd
 for(j2 = 0; j2 < 11; j2 += 1) {
  for(j4 = 0; j4 < 11; j4 += 1) {
   tmp2[e][j1][j2][0] += A[j1][j4] * tmp1[e][j2][j4][0];
   tmp2[e][j1][j2][1] += A[j1][j4] * tmp1[e][j2][j4][1];
   tmp2[e][j1][j2][2] += A[j1][j4] * tmp1[e][j2][j4][2];
   tmp2[e][j1][j2][3] += A[j1][j4] * tmp1[e][j2][j4][3];
   tmp2[e][j1][j2][4] += A[j1][j4] * tmp1[e][j2][j4][4];
   tmp2[e][j1][j2][5] += A[j1][j4] * tmp1[e][j2][j4][5];
   tmp2[e][j1][j2][6] += A[j1][j4] * tmp1[e][j2][j4][6];
   tmp2[e][j1][j2][7] += A[j1][j4] * tmp1[e][j2][j4][7];
   tmp2[e][j1][j2][8] += A[j1][j4] * tmp1[e][j2][j4][8];
   tmp2[e][j1][j2][9] += A[j1][j4] * tmp1[e][j2][j4][9];
   tmp2[e][j1][j2][10] += A[j1][j4] * tmp1[e][j2][j4][10];
   }
  }
 }
for(k1 = 0; k1 < 11; k1 += 1) {
 #pragma vector aligned
#pragma simd
 for(k2 = 0; k2 < 11; k2 += 1) {
  for(k4 = 0; k4 < 11; k4 += 1) {
   v[e][k1][k2][0] += A[k1][k4] * tmp2[e][k2][0][k4];
   v[e][k1][k2][1] += A[k1][k4] * tmp2[e][k2][1][k4];
   v[e][k1][k2][2] += A[k1][k4] * tmp2[e][k2][2][k4];
   v[e][k1][k2][3] += A[k1][k4] * tmp2[e][k2][3][k4];
   v[e][k1][k2][4] += A[k1][k4] * tmp2[e][k2][4][k4];
   v[e][k1][k2][5] += A[k1][k4] * tmp2[e][k2][5][k4];
   v[e][k1][k2][6] += A[k1][k4] * tmp2[e][k2][6][k4];
   v[e][k1][k2][7] += A[k1][k4] * tmp2[e][k2][7][k4];
   v[e][k1][k2][8] += A[k1][k4] * tmp2[e][k2][8][k4];
   v[e][k1][k2][9] += A[k1][k4] * tmp2[e][k2][9][k4];
   v[e][k1][k2][10] += A[k1][k4] * tmp2[e][k2][10][k4];
   }
  }
 }
}
double end = omp_get_wtime();
printf("Time: %f ms\n", end-begin);
return 0;
}

