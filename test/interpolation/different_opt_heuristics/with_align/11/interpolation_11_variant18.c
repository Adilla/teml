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

int i1, i2, i3, i4, j1, j2, j3, j4, k1, k2, k3, k4;

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
 for(i2 = 0; i2 < 11; i2 += 1) {
  for(i3 = 0; i3 < 11; i3 += 1) {
   #pragma vector aligned
#pragma simd
   for(i4 = 0; i4 < 8; i4 += 4) {
    tmp1[e][i1][i2][i3] += A[i1][i4] * u[e][i4][i2][i3];
    tmp1[e][i1][i2][i3] += A[i1][i4 + 1] * u[e][i4 + 1][i2][i3];
    tmp1[e][i1][i2][i3] += A[i1][i4 + 2] * u[e][i4 + 2][i2][i3];
    tmp1[e][i1][i2][i3] += A[i1][i4 + 3] * u[e][i4 + 3][i2][i3];
    }
   tmp1[e][i1][i2][i3] += A[i1][8] * u[e][8][i2][i3];
   tmp1[e][i1][i2][i3] += A[i1][9] * u[e][9][i2][i3];
   tmp1[e][i1][i2][i3] += A[i1][10] * u[e][10][i2][i3];
   }
  }
 }
for(j1 = 0; j1 < 11; j1 += 1) {
 for(j2 = 0; j2 < 11; j2 += 1) {
  for(j3 = 0; j3 < 11; j3 += 1) {
   #pragma vector aligned
#pragma simd
   for(j4 = 0; j4 < 8; j4 += 4) {
    tmp2[e][j1][j2][j3] += A[j1][j4] * tmp1[e][j2][j4][j3];
    tmp2[e][j1][j2][j3] += A[j1][j4 + 1] * tmp1[e][j2][j4 + 1][j3];
    tmp2[e][j1][j2][j3] += A[j1][j4 + 2] * tmp1[e][j2][j4 + 2][j3];
    tmp2[e][j1][j2][j3] += A[j1][j4 + 3] * tmp1[e][j2][j4 + 3][j3];
    }
   tmp2[e][j1][j2][j3] += A[j1][8] * tmp1[e][j2][8][j3];
   tmp2[e][j1][j2][j3] += A[j1][9] * tmp1[e][j2][9][j3];
   tmp2[e][j1][j2][j3] += A[j1][10] * tmp1[e][j2][10][j3];
   }
  }
 }
for(k1 = 0; k1 < 11; k1 += 1) {
 for(k2 = 0; k2 < 11; k2 += 1) {
  for(k3 = 0; k3 < 11; k3 += 1) {
   #pragma vector aligned
#pragma simd
   for(k4 = 0; k4 < 8; k4 += 4) {
    v[e][k1][k2][k3] += A[k1][k4] * tmp2[e][k2][k3][k4];
    v[e][k1][k2][k3] += A[k1][k4 + 1] * tmp2[e][k2][k3][k4 + 1];
    v[e][k1][k2][k3] += A[k1][k4 + 2] * tmp2[e][k2][k3][k4 + 2];
    v[e][k1][k2][k3] += A[k1][k4 + 3] * tmp2[e][k2][k3][k4 + 3];
    }
   v[e][k1][k2][k3] += A[k1][8] * tmp2[e][k2][k3][8];
   v[e][k1][k2][k3] += A[k1][9] * tmp2[e][k2][k3][9];
   v[e][k1][k2][k3] += A[k1][10] * tmp2[e][k2][k3][10];
   }
  }
 }
}
double end = omp_get_wtime();
printf("Time: %f ms\n", end-begin);
return 0;
}

