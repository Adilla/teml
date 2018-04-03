#include <stdio.h>
#include <stdlib.h>
#include <omp.h>


int main() {

int tt1, tt2, tt3, tt4, e;
double A[2][2];
double u[512][2][2][2];
double tmp1[512][2][2][2];
double tmp2[512][2][2][2];
double v[512][2][2][2];

int i1, i2, i4, j1, j2, j4, k1, k2, k4;

for (tt1 = 0; tt1 < 2; tt1++) 
    for (tt2 = 0; tt2 < 2; tt2++) 
    	A[tt1][tt2] = tt1 + tt2 + 5;


for (e = 0; e < 512; e++) 
    for (tt1 = 0; tt1 < 2; tt1++) 
    for (tt2 = 0; tt2 < 2; tt2++) 	
 	for (tt3 = 0; tt3 < 2; tt3++) {
	    u[e][tt1][tt2][tt3] = tt1 * tt2 + 5;
	    v[e][tt1][tt2][tt3] = 0;
 	    tmp1[e][tt1][tt2][tt3] = 0;
	    tmp2[e][tt1][tt2][tt3] = 0;	
	    }


double begin = omp_get_wtime();
for (e = 0; e < 512; e++) {
for(i1 = 0; i1 < 2; i1 += 1) {
 #pragma simd
 for(i2 = 0; i2 < 2; i2 += 1) {
  for(i4 = 0; i4 < 2; i4 += 1) {
   tmp1[e][i1][i2][0] += A[i1][i4] * u[e][i4][i2][0];
   tmp1[e][i1][i2][1] += A[i1][i4] * u[e][i4][i2][1];
   }
  }
 }
for(j1 = 0; j1 < 2; j1 += 1) {
 #pragma simd
 for(j2 = 0; j2 < 2; j2 += 1) {
  for(j4 = 0; j4 < 2; j4 += 1) {
   tmp2[e][j1][j2][0] += A[j1][j4] * tmp1[e][j2][j4][0];
   tmp2[e][j1][j2][1] += A[j1][j4] * tmp1[e][j2][j4][1];
   }
  }
 }
for(k1 = 0; k1 < 2; k1 += 1) {
 #pragma simd
 for(k2 = 0; k2 < 2; k2 += 1) {
  for(k4 = 0; k4 < 2; k4 += 1) {
   v[e][k1][k2][0] += A[k1][k4] * tmp2[e][k2][0][k4];
   v[e][k1][k2][1] += A[k1][k4] * tmp2[e][k2][1][k4];
   }
  }
 }
}
double end = omp_get_wtime();
printf("Time: %f ms\n", end-begin);
return 0;
}

