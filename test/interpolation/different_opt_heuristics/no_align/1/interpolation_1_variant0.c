#include <stdio.h>
#include <stdlib.h>
#include <omp.h>


int main() {

int tt1, tt2, tt3, tt4, e;
double A[1][1];
double u[512][1][1][1];
double tmp1[512][1][1][1];
double tmp2[512][1][1][1];
double v[512][1][1][1];

int i1, i2, i3, j1, j2, j3, k1, k2, k3;

for (tt1 = 0; tt1 < 1; tt1++) 
    for (tt2 = 0; tt2 < 1; tt2++) 
    	A[tt1][tt2] = tt1 + tt2 + 5;


for (e = 0; e < 512; e++) 
    for (tt1 = 0; tt1 < 1; tt1++) 
    for (tt2 = 0; tt2 < 1; tt2++) 	
 	for (tt3 = 0; tt3 < 1; tt3++) {
	    u[e][tt1][tt2][tt3] = tt1 * tt2 + 5;
	    v[e][tt1][tt2][tt3] = 0;
 	    tmp1[e][tt1][tt2][tt3] = 0;
	    tmp2[e][tt1][tt2][tt3] = 0;	
	    }


double begin = omp_get_wtime();
for (e = 0; e < 512; e++) {
for(i1 = 0; i1 < 1; i1 += 1) {
 for(i2 = 0; i2 < 1; i2 += 1) {
  #pragma simd
  for(i3 = 0; i3 < 1; i3 += 1) {
   tmp1[e][i1][i2][i3] += A[i1][0] * u[e][0][i2][i3];
   }
  }
 }
for(j1 = 0; j1 < 1; j1 += 1) {
 for(j2 = 0; j2 < 1; j2 += 1) {
  #pragma simd
  for(j3 = 0; j3 < 1; j3 += 1) {
   tmp2[e][j1][j2][j3] += A[j1][0] * tmp1[e][j2][0][j3];
   }
  }
 }
for(k1 = 0; k1 < 1; k1 += 1) {
 for(k2 = 0; k2 < 1; k2 += 1) {
  #pragma simd
  for(k3 = 0; k3 < 1; k3 += 1) {
   v[e][k1][k2][k3] += A[k1][0] * tmp2[e][k2][k3][0];
   }
  }
 }
}
double end = omp_get_wtime();
printf("Time: %f ms\n", end-begin);
return 0;
}

