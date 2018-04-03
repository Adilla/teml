#include <stdio.h>
#include <stdlib.h>
#include <omp.h>


int main() {

int tt1, tt2, tt3, tt4, e;
double A[9][9] __attribute__((aligned(64)));
double u[512][9][9][9] __attribute__((aligned(64)));
double tmp1[512][9][9][9] __attribute__((aligned(64)));
double tmp2[512][9][9][9] __attribute__((aligned(64)));
double v[512][9][9][9] __attribute__((aligned(64)));

int i1, i2, i3, i4, j1, j2, j3, j4, k1, k2, k3, k4;

for (tt1 = 0; tt1 < 9; tt1++)
  for (tt2 = 0; tt2 < 9; tt2++)
    A[tt1][tt2] = tt1 + tt2 + 5;
                                 
for (e = 0; e < 512; e++)
  for (tt1 = 0; tt1 < 9; tt1++)
    for (tt2 = 0; tt2 < 9; tt2++)
      for (tt3 = 0; tt3 < 9; tt3++) {
        u[e][tt1][tt2][tt3] = tt1 * tt2 + 5;
        v[e][tt1][tt2][tt3] = 0;
        tmp1[e][tt1][tt2][tt3] = 0;
        tmp2[e][tt1][tt2][tt3] = 0;
      }

double begin = omp_get_wtime();
for (e = 0; e < 512; e++) {
for(i1 = 0; i1 < 8; i1 += 4) {
 for(i2 = 0; i2 < 9; i2 += 1) {
  for(i3 = 0; i3 < 9; i3 += 1) {
   for(i4 = 0; i4 < 9; i4 += 1) {
    tmp1[e][i1][i2][i3] += A[i1][i4] * u[e][i4][i2][i3];
    tmp1[e][8][i2][i3] += A[i2][i4] * u[e][i4][i2][i3];
    tmp1[e][i1 + 1][i2][i3] += A[i1 + 1][i4] * u[e][i4][i2][i3];
    tmp1[e][8][i2][i3] += A[i2][i4] * u[e][i4][i2][i3];
    tmp1[e][i1 + 2][i2][i3] += A[i1 + 2][i4] * u[e][i4][i2][i3];
    tmp1[e][8][i2][i3] += A[i2][i4] * u[e][i4][i2][i3];
    tmp1[e][i1 + 3][i2][i3] += A[i1 + 3][i4] * u[e][i4][i2][i3];
    tmp1[e][8][i2][i3] += A[i2][i4] * u[e][i4][i2][i3];
    }
   }
  }
 }
for(j1 = 0; j1 < 8; j1 += 4) {
 for(j2 = 0; j2 < 9; j2 += 1) {
  for(j3 = 0; j3 < 9; j3 += 1) {
   for(j4 = 0; j4 < 9; j4 += 1) {
    tmp2[e][j1][j2][j3] += A[j1][j4] * tmp1[e][j2][j4][j3];
    tmp2[e][8][j2][j3] += A[j2][j4] * tmp1[e][j2][j4][j3];
    tmp2[e][j1 + 1][j2][j3] += A[j1 + 1][j4] * tmp1[e][j2][j4][j3];
    tmp2[e][8][j2][j3] += A[j2][j4] * tmp1[e][j2][j4][j3];
    tmp2[e][j1 + 2][j2][j3] += A[j1 + 2][j4] * tmp1[e][j2][j4][j3];
    tmp2[e][8][j2][j3] += A[j2][j4] * tmp1[e][j2][j4][j3];
    tmp2[e][j1 + 3][j2][j3] += A[j1 + 3][j4] * tmp1[e][j2][j4][j3];
    tmp2[e][8][j2][j3] += A[j2][j4] * tmp1[e][j2][j4][j3];
    }
   }
  }
 }
for(k1 = 0; k1 < 8; k1 += 4) {
 for(k2 = 0; k2 < 9; k2 += 1) {
  for(k3 = 0; k3 < 9; k3 += 1) {
   for(k4 = 0; k4 < 9; k4 += 1) {
    v[e][k1][k2][k3] += A[k1][k4] * tmp2[e][k2][k3][k4];
    v[e][8][k2][k3] += A[k2][k4] * tmp2[e][k2][k3][k4];
    v[e][k1 + 1][k2][k3] += A[k1 + 1][k4] * tmp2[e][k2][k3][k4];
    v[e][8][k2][k3] += A[k2][k4] * tmp2[e][k2][k3][k4];
    v[e][k1 + 2][k2][k3] += A[k1 + 2][k4] * tmp2[e][k2][k3][k4];
    v[e][8][k2][k3] += A[k2][k4] * tmp2[e][k2][k3][k4];
    v[e][k1 + 3][k2][k3] += A[k1 + 3][k4] * tmp2[e][k2][k3][k4];
    v[e][8][k2][k3] += A[k2][k4] * tmp2[e][k2][k3][k4];
    }
   }
  }
 }
}
double end = omp_get_wtime();
printf("Time: %f ms\n", end-begin);
return 0;
}

