#include <stdio.h>
#include <stdlib.h>
#include <omp.h>


int main() {

int tt1, tt2, tt3, tt4, e;
double A[13][13] __attribute__((aligned(64)));
double u[512][13][13][13] __attribute__((aligned(64)));
double tmp1[512][13][13][13] __attribute__((aligned(64)));
double tmp2[512][13][13][13] __attribute__((aligned(64)));
double v[512][13][13][13] __attribute__((aligned(64)));

int i1, i2, i3, i4, j1, j2, j3, j4, k1, k2, k3, k4;

for (tt1 = 0; tt1 < 13; tt1++)
  for (tt2 = 0; tt2 < 13; tt2++)
    A[tt1][tt2] = tt1 + tt2 + 5;
                                 
for (e = 0; e < 512; e++)
  for (tt1 = 0; tt1 < 13; tt1++)
    for (tt2 = 0; tt2 < 13; tt2++)
      for (tt3 = 0; tt3 < 13; tt3++) {
        u[e][tt1][tt2][tt3] = tt1 * tt2 + 5;
        v[e][tt1][tt2][tt3] = 0;
        tmp1[e][tt1][tt2][tt3] = 0;
        tmp2[e][tt1][tt2][tt3] = 0;
      }

double begin = omp_get_wtime();
for (e = 0; e < 512; e++) {
for(i1 = 0; i1 < 13; i1 += 1) {
 for(i2 = 0; i2 < 13; i2 += 1) {
  for(i3 = 0; i3 < 13; i3 += 1) {
   for(i4 = 0; i4 < 12; i4 += 4) {
    tmp1[e][i1][i2][i3] += A[i1][i4] * u[e][i4][i2][i3];
    tmp1[e][i1][i2][i3] += A[i1][i4 + 1] * u[e][i4 + 1][i2][i3];
    tmp1[e][i1][i2][i3] += A[i1][i4 + 2] * u[e][i4 + 2][i2][i3];
    tmp1[e][i1][i2][i3] += A[i1][i4 + 3] * u[e][i4 + 3][i2][i3];
    }
   tmp1[e][i1][i2][i3] += A[i1][12] * u[e][12][i2][i3];
   }
  }
 }
for(j1 = 0; j1 < 13; j1 += 1) {
 for(j2 = 0; j2 < 13; j2 += 1) {
  for(j3 = 0; j3 < 13; j3 += 1) {
   for(j4 = 0; j4 < 12; j4 += 4) {
    tmp2[e][j1][j2][j3] += A[j1][j4] * tmp1[e][j2][j4][j3];
    tmp2[e][j1][j2][j3] += A[j1][j4 + 1] * tmp1[e][j2][j4 + 1][j3];
    tmp2[e][j1][j2][j3] += A[j1][j4 + 2] * tmp1[e][j2][j4 + 2][j3];
    tmp2[e][j1][j2][j3] += A[j1][j4 + 3] * tmp1[e][j2][j4 + 3][j3];
    }
   tmp2[e][j1][j2][j3] += A[j1][12] * tmp1[e][j2][12][j3];
   }
  }
 }
for(k1 = 0; k1 < 13; k1 += 1) {
 for(k2 = 0; k2 < 13; k2 += 1) {
  for(k3 = 0; k3 < 13; k3 += 1) {
   for(k4 = 0; k4 < 12; k4 += 4) {
    v[e][k1][k2][k3] += A[k1][k4] * tmp2[e][k2][k3][k4];
    v[e][k1][k2][k3] += A[k1][k4 + 1] * tmp2[e][k2][k3][k4 + 1];
    v[e][k1][k2][k3] += A[k1][k4 + 2] * tmp2[e][k2][k3][k4 + 2];
    v[e][k1][k2][k3] += A[k1][k4 + 3] * tmp2[e][k2][k3][k4 + 3];
    }
   v[e][k1][k2][k3] += A[k1][12] * tmp2[e][k2][k3][12];
   }
  }
 }
}
double end = omp_get_wtime();
printf("Time: %f ms\n", end-begin);
return 0;
}

