#include <stdio.h>
#include <stdlib.h>
#include <omp.h>


int main() {

int tt1, tt2, tt3, tt4, e;
double A[5][5];
double u[512][5][5][5];
double tmp1[512][5][5][5];
double tmp2[512][5][5][5];
double v[512][5][5][5];

int i1, i2, i3, i4, j1, j2, j3, j4, k1, k2, k3, k4;

for (tt1 = 0; tt1 < 5; tt1++) 
    for (tt2 = 0; tt2 < 5; tt2++) 
    	A[tt1][tt2] = tt1 + tt2 + 5;


for (e = 0; e < 512; e++) 
    for (tt1 = 0; tt1 < 5; tt1++) 
    for (tt2 = 0; tt2 < 5; tt2++) 	
 	for (tt3 = 0; tt3 < 5; tt3++) {
	    u[e][tt1][tt2][tt3] = tt1 * tt2 + 5;
	    v[e][tt1][tt2][tt3] = 0;
 	    tmp1[e][tt1][tt2][tt3] = 0;
	    tmp2[e][tt1][tt2][tt3] = 0;	
	    }


double begin = omp_get_wtime();
for (e = 0; e < 512; e++) {
for(i1 = 0; i1 < 5; i1 += 1) {
 #pragma simd
 for(i2 = 0; i2 < 5; i2 += 1) {
  for(i3 = 0; i3 < 5; i3 += 1) {
   for(i4 = 0; i4 < 5; i4 += 1) {
    tmp1[e][i1][i2][i3] += A[i1][i4] * u[e][i4][i2][i3];
    }
   }
  }
 }
for(j1 = 0; j1 < 5; j1 += 1) {
 #pragma simd
 for(j2 = 0; j2 < 5; j2 += 1) {
  for(j3 = 0; j3 < 5; j3 += 1) {
   for(j4 = 0; j4 < 5; j4 += 1) {
    tmp2[e][j1][j2][j3] += A[j1][j4] * tmp1[e][j2][j4][j3];
    }
   }
  }
 }
for(k1 = 0; k1 < 5; k1 += 1) {
 #pragma simd
 for(k2 = 0; k2 < 5; k2 += 1) {
  for(k3 = 0; k3 < 5; k3 += 1) {
   for(k4 = 0; k4 < 5; k4 += 1) {
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

