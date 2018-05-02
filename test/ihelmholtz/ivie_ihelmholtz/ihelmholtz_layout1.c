#include <stdio.h>
#include <stdlib.h>
#include <omp.h>
#define min(x, y) ((x) < (y)) ? ((x) : (y))
#define max(x, y) ((x) > (y)) ? ((x) : (y))

int main(int *argc, char **argv) {
  int N = atoi(argv[2]);
  int M =atoi(argv[1]);
  int tt1, tt2, tt3, tt4, tt5;
  double A[N][N];
  double u[M][N][N][N];
  double D[N][N][N];
  double tmp1[N][N][N];
  double tmp2[N][N][N];
  double tmp3[N][N][N];
  double tmp4[N][N][N];
  double tmp5[N][N][N];
  double tmp6[N][N][N];
  double v[M][N][N][N];

  int i4, i1, i2, i3, j2, j4, j1, j3, k2, k3, k4, k1, l1, l2, l3, i12, i42, i22,
    i32, j12, j22, j42, j32, k12, k22, k32, k42, e;

  double begin = omp_get_wtime();

#pragma omp parallel for private(i4, i1, i2, i3, j2, j4, j1, j3, k2, k3, k4, k1, l1, l2, l3, i12, i42, i22, i32, j12, j22, j42, j32, k12, k22, k32, k42)
  for (e = 0; e < M; e++) {
#pragma omp parallel for private(i2, i3, i1)
  for (i4 = 0; i4 < N; i4 += 1) {
    for (i1 = 0; i1 < N; i1 += 1) {
      for (i2 = 0; i2 < N; i2 += 1) {
#pragma simd
        for (i3 = 0; i3 < N; i3 += 1) {
#pragma omp atomic
	  tmp1[i1][i2][i3] += A[i4][i1] * u[e][i4][i2][i3];
        }
      }
    }
  }
#pragma omp parallel for private(j3, j4, j1)
  for (j2 = 0; j2 < N; j2 += 1) {
    for (j4 = 0; j4 < N; j4 += 1) {
      for (j1 = 0; j1 < N; j1 += 1) {
#pragma simd
        for (j3 = 0; j3 < N; j3 += 1) {
          tmp2[j1][j2][j3] += A[j4][j1] * tmp1[j2][j4][j3];
        }
      }
    }
  }
#pragma omp parallel for private(k3, k4, k1)
  for (k2 = 0; k2 < N; k2 += 1) {
    for (k3 = 0; k3 < N; k3 += 1) {
      for (k4 = 0; k4 < N; k4 += 1) {
#pragma simd
        for (k1 = 0; k1 < N; k1 += 1) {
          tmp3[k1][k2][k3] += A[k4][k1] * tmp2[k2][k3][k4];
        }
      }
    }
  }
#pragma omp parallel for private(l2, l3)
  for (l1 = 0; l1 < N; l1 += 1) {
    for (l2 = 0; l2 < N; l2 += 1) {
      for (l3 = 0; l3 < N; l3 += 1) {
        tmp4[l1][l2][l3] = D[l1][l2][l3] * tmp3[l1][l2][l3];
      }
    }
  }
#pragma omp parallel for private(i22, i32, i42)
  for (i12 = 0; i12 < N; i12 += 1) {
    for (i42 = 0; i42 < N; i42 += 1) {
      for (i22 = 0; i22 < N; i22 += 1) {
#pragma simd
        for (i32 = 0; i32 < N; i32 += 1) {
          tmp5[i12][i22][i32] += A[i12][i42] * tmp4[i42][i22][i32];
        }
      }
    }
  }
#pragma omp parallel for private(j22, j32, j42)
  for (j12 = 0; j12 < N; j12 += 1) {
    for (j22 = 0; j22 < N; j22 += 1) {
      for (j42 = 0; j42 < N; j42 += 1) {
#pragma simd
        for (j32 = 0; j32 < N; j32 += 1) {
          tmp6[j12][j22][j32] += A[j12][j42] * tmp5[j22][j42][j32];
        }
      }
    }
  }
#pragma omp parallel for private(k22, k32, k42)
  for (k12 = 0; k12 < N; k12 += 1) {
    for (k22 = 0; k22 < N; k22 += 1) {
      for (k32 = 0; k32 < N; k32 += 1) {
#pragma simd
        for (k42 = 0; k42 < N; k42 += 1) {
          v[e][k12][k22][k32] += A[k12][k42] * tmp6[k22][k32][k42];
        }
      }
    }
  }
}
double end = omp_get_wtime();
printf("Time: %f ms\n", end - begin);
return 0;
}
