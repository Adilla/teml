#include <stdio.h>
#include <stdlib.h>
#include <omp.h>
#define min(x, y) ((x) < (y) ? (x) : (y))
#define max(x, y) ((x) > (y) ? (x) : (y))
#define N 80

int main() {

  double rt[N][N][N];
  double ut[N][N][N];
  double L[N][N];
  double w[N];


  int i1, i2, i3, j1, j2, j3, j4, k1, k2, k3, k4, l1, l2, l3, l4;

  int i, j, k, l;

  for (i = 0; i < N; i++) {
    w[i] = i + 15;
    for (j = 0; j < N; j++) {
      L[i][j] = i + j + 1;
      for (k = 0; k < N; k++) {
        rt[i][j][k] = 0;
        ut[i][j][k] = i * j + 10;
      }
    }
  }

  double begin = omp_get_wtime();
  //#pragma omp parallel for private(i2, i3)
  for (i1 = 0; i1 < N; i1 += 1) {
    for (i2 = 0; i2 < N; i2 += 1) {
      for (i3 = 0; i3 < N; i3 += 1) {
        rt[i1][i2][i3] = w[i1] * w[i2] * w[i3] * ut[i1][i2][i3];
      }
    }
  }
#pragma omp parallel for private(j2, j3, j4)
  for (j1 = 0; j1 < N; j1 += 1) {
    for (j2 = 0; j2 < N; j2 += 1) {
      for (j3 = 0; j3 < N; j3 += 1) {
        for (j4 = 0; j4 < N; j4 += 1) {
          rt[j1][j2][j3] += L[j1][j4] * w[j2] * w[j3] * ut[j4][j2][j3];
        }
      }
    }
  }
#pragma omp parallel for private(k2, k3, k4)
  for (k1 = 0; k1 < N; k1 += 1) {
    for (k2 = 0; k2 < N; k2 += 1) {
      for (k3 = 0; k3 < N; k3 += 1) {
        for (k4 = 0; k4 < N; k4 += 1) {
          rt[k1][k2][k3] += w[k1] * L[k2][k4] * w[k3] * ut[k1][k4][k3];
        }
      }
    }
  }
#pragma omp parallel for private(l2, l3, l4)
  for (l1 = 0; l1 < N; l1 += 1) {
    for (l2 = 0; l2 < N; l2 += 1) {
      for (l3 = 0; l3 < N; l3 += 1) {
        for (l4 = 0; l4 < N; l4 += 1) {
          rt[l1][l2][l3] += w[l1] * w[l2] * L[l3][l4] * ut[l1][l2][l4];
        }
      }
    }
  }
  double end = omp_get_wtime();
  printf("Time: %f ms\n", end - begin);

  for (j = 0; j < 3; j++)
    for (k = 0; k < 3; k++)
      for (l = 0; l < 3; l++)
        printf("%.0f  ", rt[j][k][l]);

  printf("\n");

  return 0;
}
