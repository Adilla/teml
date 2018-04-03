#include <stdio.h>
#include <stdlib.h>
#include <omp.h>


int main() {

int tt1, tt2, tt3, tt4, e;
double u[512][4][8][8];
double M123[4][8][8];
double Lh[4][8];
double d1;
double d2;
double d3;
double Mu[4][8][8];
double cr1[4][8][8];
double r1;
double cr2[4][4][8];
double r2;
double cr3[4][4][8];
double r3;

int i1, i2, i3, j1, j2, j3, j4, j11, j22, j33, k1, k2, k3, k4, k11, k22, k33, l1, l2, l3, l4, l11, l22, l33;

int i, j, k, l;

for (i = 0; i < N; i++) {
    w[i] = i + 15;
    for (j = 0; j < N; j++) {
    	L[i][j] = i + j +1;
	for (k = 0; k < N; k++) { 
	    	rt[i][j][k] = 0;
		ut[i][j][k] = i*j+10;
	}		
	
}
}



double begin = omp_get_wtime();
for (e = 0; e < 512; e++) {
for(i1 = 0; i1 < 8; i1 += 1) {
 for(i2 = 0; i2 < 8; i2 += 1) {
  #pragma simd
  for(i3 = 0; i3 < 8; i3 += 2) {
   Mu[i1][i2][i3] = M123[i1][i2][i3] * u[e][i1][i2][i3];
   Mu[i1][i2][i3 + 1] = M123[i1][i2][i3 + 1] * u[e][i1][i2][i3 + 1];
   }
  }
 }
for(j1 = 0; j1 < 8; j1 += 1) {
 for(j2 = 0; j2 < 8; j2 += 1) {
  for(j3 = 0; j3 < 8; j3 += 1) {
   #pragma simd
   for(j4 = 0; j4 < 8; j4 += 2) {
    cr1[j1][j2][j3] += Lh[j1][j4] * Mu[j4][j2][j3];
    cr1[j1][j2][j3] += Lh[j1][j4 + 1] * Mu[j4 + 1][j2][j3];
    }
   }
  }
 }
for(j11 = 0; j11 < 8; j11 += 1) {
 for(j22 = 0; j22 < 8; j22 += 1) {
  for(j33 = 0; j33 < 8; j33 += 1) {
   r1[j11][j22][j33] = d1 * cr1[j11][j22][j33];
   }
  }
 }
for(k1 = 0; k1 < 8; k1 += 1) {
 for(k2 = 0; k2 < 8; k2 += 1) {
  for(k3 = 0; k3 < 8; k3 += 1) {
   #pragma simd
   for(k4 = 0; k4 < 8; k4 += 2) {
    cr2[k1][k2][k3] += Lh[k1][k4] * Mu[k2][k4][k3];
    cr2[k1][k2][k3] += Lh[k1][k4 + 1] * Mu[k2][k4 + 1][k3];
    }
   }
  }
 }
for(k11 = 0; k11 < 8; k11 += 1) {
 for(k22 = 0; k22 < 8; k22 += 1) {
  for(k33 = 0; k33 < 8; k33 += 1) {
   r2[k11][k22][k33] = d2 * cr2[k11][k22][k33];
   }
  }
 }
for(l1 = 0; l1 < 8; l1 += 1) {
 for(l2 = 0; l2 < 8; l2 += 1) {
  for(l3 = 0; l3 < 8; l3 += 1) {
   #pragma simd
   for(l4 = 0; l4 < 8; l4 += 2) {
    cr3[l1][l2][l3] += Lh[l1][l4] * Mu[l2][l3][l4];
    cr3[l1][l2][l3] += Lh[l1][l4 + 1] * Mu[l2][l3][l4 + 1];
    }
   }
  }
 }
for(l11 = 0; l11 < 8; l11 += 1) {
 for(l22 = 0; l22 < 8; l22 += 1) {
  for(l33 = 0; l33 < 8; l33 += 1) {
   r3[l11][l22][l33] = d3 * cr3[l11][l22][l33];
   }
  }
 }
}
double end = omp_get_wtime();
printf("Time: %f ms\n", end-begin);
return 0;
}

