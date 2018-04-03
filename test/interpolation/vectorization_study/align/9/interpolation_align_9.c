#include <stdio.h>
#include <stdlib.h>
#include <omp.h>


int main() {

int tt1, tt2, tt3, tt4, e;
double A[9][9] __attribute__((aligned(64)));
double u[216][9][9][9] __attribute__((aligned(64)));
double tmp1[216][9][9][9] __attribute__((aligned(64)));
double tmp2[216][9][9][9] __attribute__((aligned(64)));
double v[216][9][9][9] __attribute__((aligned(64)));

int i1, i2, i3, i4, j1, j2, j3, j4, k1, k2, k3, k4;


double begin = omp_get_wtime();
for (e = 0; e < 216; e++) {

for(i1 = 0; i1 < 9; i1 += 1) {
 
for(i2 = 0; i2 < 9; i2 += 1) {
  
for(i3 = 0; i3 < 9; i3 += 1) {
   
for(i4 = 0; i4 < 9; i4 += 1) {
    tmp1[e][i1][i2][i3] += A[i1][i4] * u[e][i4][i2][i3];
    }
   }
  }
 }

for(j1 = 0; j1 < 9; j1 += 1) {
 
for(j2 = 0; j2 < 9; j2 += 1) {
  
for(j3 = 0; j3 < 9; j3 += 1) {
   
for(j4 = 0; j4 < 9; j4 += 1) {
    tmp2[e][j1][j2][j3] += A[j1][j4] * tmp1[e][j2][j4][j3];
    }
   }
  }
 }

for(k1 = 0; k1 < 9; k1 += 1) {
 
for(k2 = 0; k2 < 9; k2 += 1) {
  
for(k3 = 0; k3 < 9; k3 += 1) {
   
for(k4 = 0; k4 < 9; k4 += 1) {
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

