#include <stdio.h>
#include <stdlib.h>
#include <omp.h>


int main() {

int tt1, tt2, tt3, tt4, e;
double A[8][8];
double u[512][8][8][8];
double tmp1[512][8][8][8];
double tmp2[512][8][8][8];
double v[512][8][8][8];

int i1, i2, i3, i4, j1, j2, j3, j4, k1, k2, k3, k4;

for (tt1 = 0; tt1 < 8; tt1++) 
    for (tt2 = 0; tt2 < 8; tt2++) 
    	A[tt1][tt2] = tt1 + tt2 + 5;


for (e = 0; e < 512; e++) 
    for (tt1 = 0; tt1 < 8; tt1++) 
    for (tt2 = 0; tt2 < 8; tt2++) 	
 	for (tt3 = 0; tt3 < 8; tt3++) {
	    u[e][tt1][tt2][tt3] = tt1 * tt2 + 5;
	    v[e][tt1][tt2][tt3] = 0;
 	    tmp1[e][tt1][tt2][tt3] = 0;
	    tmp2[e][tt1][tt2][tt3] = 0;	
	    }


double begin = omp_get_wtime();
for (e = 0; e < 512; e++) {
for(i1 = 0; i1 < 8; i1 += 1) {
 #pragma simd
 for(i2 = 0; i2 < 8; i2 += 2) {
  for(i3 = 0; i3 < 8; i3 += 1) {
   for(i4 = 0; i4 < 8; i4 += 1) {
    tmp1[e][i1][i2][i3] += A[i1][i4] * u[e][i4][i2][i3];
    tmp1[e][i1][i2 + 1][i3] += A[i1][i4] * u[e][i4][i2 + 1][i3];
    }
   }
  }
 }
for(j1 = 0; j1 < 8; j1 += 1) {
 #pragma simd
 for(j2 = 0; j2 < 8; j2 += 2) {
  for(j3 = 0; j3 < 8; j3 += 1) {
   for(j4 = 0; j4 < 8; j4 += 1) {
    tmp2[e][j1][j2][j3] += A[j1][j4] * tmp1[e][j2][j4][j3];
    tmp2[e][j1][j2 + 1][j3] += A[j1][j4] * tmp1[e][j2 + 1][j4][j3];
    }
   }
  }
 }
for(k1 = 0; k1 < 8; k1 += 1) {
 #pragma simd
 for(k2 = 0; k2 < 8; k2 += 2) {
  for(k3 = 0; k3 < 8; k3 += 1) {
   for(k4 = 0; k4 < 8; k4 += 1) {
    v[e][k1][k2][k3] += A[k1][k4] * tmp2[e][k2][k3][k4];
    v[e][k1][k2 + 1][k3] += A[k1][k4] * tmp2[e][k2 + 1][k3][k4];
    }
   }
  }
 }
}
double end = omp_get_wtime();
printf("Time: %f ms\n", end-begin);
return 0;
}

