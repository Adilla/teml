#include <stdio.h>
#include <stdlib.h>
#include <omp.h>
#define min(x, y) ((x) < (y) ? (x) : (y))
#define max(x, y) ((x) > (y) ? (x) : (y))
#define N 50

int main() {

  double rt[N][N][N];
  double ut[N][N][N];
  double L[N][N];
  double w[N];

  int ti1, ti2, ti3, i1, i2, i3, j3;

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
#pragma omp parallel for private(ti2, ti3, i1, i2, i3, j3)
  for (ti1 = 0; ti1 < N; ti1 += 8) {
    for (ti2 = 0; ti2 < N; ti2 += 8) {
      for (ti3 = 0; ti3 < N; ti3 += 8) {
        for (i1 = ti1; i1 < min(N, ti1 + 8); i1 += 1) {
          for (i2 = ti2; i2 < min(N, ti2 + 8); i2 += 1) {
            for (i3 = ti3; i3 < min(N, ti3 + 8); i3 += 1) {
              rt[i1][i2][i3] += w[i1] * w[i2] * w[i3] * ut[i1][i2][i3];
              for (j3 = 0; j3 < N; j3 += 1) {
                rt[i1][i3][j3] += L[i1][i2] * w[i3] * w[j3] * ut[i2][i3][j3];
                rt[i1][i2][j3] += w[i1] * L[i2][i3] * w[j3] * ut[i1][i3][j3];
                rt[i1][i2][i3] += w[i1] * w[i2] * L[i3][j3] * ut[i1][i2][j3];
              }
            }
          }
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
