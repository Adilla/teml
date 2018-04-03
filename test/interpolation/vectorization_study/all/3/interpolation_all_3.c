#include <stdio.h>
#include <stdlib.h>
#include <omp.h>


int main() {

int tt1, tt2, tt3, tt4, e;
double A[3][3] __attribute__((aligned(64)));
double u[216][3][3][3] __attribute__((aligned(64)));
double tmp1[216][3][3][3] __attribute__((aligned(64)));
double tmp2[216][3][3][3] __attribute__((aligned(64)));
double v[216][3][3][3] __attribute__((aligned(64)));

int i1, i2, i3, i4, j1, j2, j3, j4, k1, k2, k3, k4;


double begin = omp_get_wtime();
for (e = 0; e < 216; e++) {

for(i1 = 0; i1 < 3; i1 += 1) {
 
for(i2 = 0; i2 < 3; i2 += 1) {
  
for(i3 = 0; i3 < 3; i3 += 1) {
   #pragma ivdep
#pragma vector always   
for(i4 = 0; i4 < 3; i4 += 1) {
    tmp1[e][i1][i2][i3] += A[i1][i4] * u[e][i4][i2][i3];
    }
   }
  }
 }

for(j1 = 0; j1 < 3; j1 += 1) {
 
for(j2 = 0; j2 < 3; j2 += 1) {
  
for(j3 = 0; j3 < 3; j3 += 1) {
   #pragma ivdep
#pragma vector always   
for(j4 = 0; j4 < 3; j4 += 1) {
    tmp2[e][j1][j2][j3] += A[j1][j4] * tmp1[e][j2][j4][j3];
    }
   }
  }
 }

for(k1 = 0; k1 < 3; k1 += 1) {
 
for(k2 = 0; k2 < 3; k2 += 1) {
  
for(k3 = 0; k3 < 3; k3 += 1) {
   #pragma ivdep
#pragma vector always   
for(k4 = 0; k4 < 3; k4 += 1) {
    v[e][k1][k2][k3] += A[k1][k4] * tmp2[e][k2][k3][k4];
    }
   }
  }
 }
}
double end = omp_get_wtime();
printf("Time: %f ms\n", end-begin);
return 0;
}

