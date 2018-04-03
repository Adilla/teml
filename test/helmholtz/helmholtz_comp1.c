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

  int i1, i2, i3, j4;

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
#pragma omp parallel for private(i2, i3, j4)
  for (i1 = 0; i1 < N; i1 += 1) {
    for (i2 = 0; i2 < N; i2 += 1) {
      for (i3 = 0; i3 < N; i3 += 1) {
        rt[i1][i2][i3] += w[i1] * w[i2] * w[i3] * ut[i1][i2][i3];
        for (j4 = 0; j4 < N; j4 += 1) {
          rt[i1][i2][i3] += L[i1][j4] * w[i2] * w[i3] * ut[j4][i2][i3];
          rt[i1][i2][i3] += w[i1] * L[i2][j4] * w[i3] * ut[i1][j4][i3];
          rt[i1][i2][i3] += w[i1] * w[i2] * L[i3][j4] * ut[i1][i2][j4];
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
