#include <stdio.h>
#include <stdlib.h>
#include <omp.h>


int main() {

int tt1, tt2, tt3, tt4, e;
double A[12][12];
double u[216][12][12][12];
double tmp1[216][12][12][12];
double tmp2[216][12][12][12];
double v[216][12][12][12];

int i1, i2, i3, i4, j1, j2, j3, j4, k1, k2, k3, k4;


double begin = omp_get_wtime();
for (e = 0; e < 216; e++) {

for(i1 = 0; i1 < 12; i1 += 1) {
 
for(i2 = 0; i2 < 12; i2 += 1) {
  
for(i3 = 0; i3 < 12; i3 += 1) {
   
for(i4 = 0; i4 < 12; i4 += 1) {
    tmp1[e][i1][i2][i3] += A[i1][i4] * u[e][i4][i2][i3];
    }
   }
  }
 }

for(j1 = 0; j1 < 12; j1 += 1) {
 
for(j2 = 0; j2 < 12; j2 += 1) {
  
for(j3 = 0; j3 < 12; j3 += 1) {
   
for(j4 = 0; j4 < 12; j4 += 1) {
    tmp2[e][j1][j2][j3] += A[j1][j4] * tmp1[e][j2][j4][j3];
    }
   }
  }
 }

for(k1 = 0; k1 < 12; k1 += 1) {
 
for(k2 = 0; k2 < 12; k2 += 1) {
  
for(k3 = 0; k3 < 12; k3 += 1) {
   
for(k4 = 0; k4 < 12; k4 += 1) {
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

