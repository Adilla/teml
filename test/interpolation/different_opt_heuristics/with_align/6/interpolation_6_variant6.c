#include <stdio.h>
#include <stdlib.h>
#include <omp.h>


int main() {

int tt1, tt2, tt3, tt4, e;
double A[6][6] __attribute__((aligned(64)));
double u[512][6][6][6] __attribute__((aligned(64)));
double tmp1[512][6][6][6] __attribute__((aligned(64)));
double tmp2[512][6][6][6] __attribute__((aligned(64)));
double v[512][6][6][6] __attribute__((aligned(64)));

int i1, i2, i3, j1, j2, j3, k1, k2, k3;

for (tt1 = 0; tt1 < 6; tt1++)
  for (tt2 = 0; tt2 < 6; tt2++)
    A[tt1][tt2] = tt1 + tt2 + 5;
                                 
for (e = 0; e < 512; e++)
  for (tt1 = 0; tt1 < 6; tt1++)
    for (tt2 = 0; tt2 < 6; tt2++)
      for (tt3 = 0; tt3 < 6; tt3++) {
        u[e][tt1][tt2][tt3] = tt1 * tt2 + 5;
        v[e][tt1][tt2][tt3] = 0;
        tmp1[e][tt1][tt2][tt3] = 0;
        tmp2[e][tt1][tt2][tt3] = 0;
      }

double begin = omp_get_wtime();
for (e = 0; e < 512; e++) {
for(i1 = 0; i1 < 6; i1 += 1) {
 for(i2 = 0; i2 < 6; i2 += 1) {
  #pragma vector aligned
#pragma simd
  for(i3 = 0; i3 < 6; i3 += 1) {
   tmp1[e][i1][i2][i3] += A[i1][0] * u[e][0][i2][i3];
   tmp1[e][i1][i2][i3] += A[i1][1] * u[e][1][i2][i3];
   tmp1[e][i1][i2][i3] += A[i1][2] * u[e][2][i2][i3];
   tmp1[e][i1][i2][i3] += A[i1][3] * u[e][3][i2][i3];
   tmp1[e][i1][i2][i3] += A[i1][4] * u[e][4][i2][i3];
   tmp1[e][i1][i2][i3] += A[i1][5] * u[e][5][i2][i3];
   }
  }
 }
for(j1 = 0; j1 < 6; j1 += 1) {
 for(j2 = 0; j2 < 6; j2 += 1) {
  #pragma vector aligned
#pragma simd
  for(j3 = 0; j3 < 6; j3 += 1) {
   tmp2[e][j1][j2][j3] += A[j1][0] * tmp1[e][j2][0][j3];
   tmp2[e][j1][j2][j3] += A[j1][1] * tmp1[e][j2][1][j3];
   tmp2[e][j1][j2][j3] += A[j1][2] * tmp1[e][j2][2][j3];
   tmp2[e][j1][j2][j3] += A[j1][3] * tmp1[e][j2][3][j3];
   tmp2[e][j1][j2][j3] += A[j1][4] * tmp1[e][j2][4][j3];
   tmp2[e][j1][j2][j3] += A[j1][5] * tmp1[e][j2][5][j3];
   }
  }
 }
for(k1 = 0; k1 < 6; k1 += 1) {
 for(k2 = 0; k2 < 6; k2 += 1) {
  #pragma vector aligned
#pragma simd
  for(k3 = 0; k3 < 6; k3 += 1) {
   v[e][k1][k2][k3] += A[k1][0] * tmp2[e][k2][k3][0];
   v[e][k1][k2][k3] += A[k1][1] * tmp2[e][k2][k3][1];
   v[e][k1][k2][k3] += A[k1][2] * tmp2[e][k2][k3][2];
   v[e][k1][k2][k3] += A[k1][3] * tmp2[e][k2][k3][3];
   v[e][k1][k2][k3] += A[k1][4] * tmp2[e][k2][k3][4];
   v[e][k1][k2][k3] += A[k1][5] * tmp2[e][k2][k3][5];
   }
  }
 }
}
double end = omp_get_wtime();
printf("Time: %f ms\n", end-begin);
return 0;
}

