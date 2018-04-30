#include <omp.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/time.h>
#include <unistd.h>

double rtclock() {
  struct timezone Tzp;
  struct timeval Tp;
  int stat;
  stat = gettimeofday(&Tp, &Tzp);
  if (stat != 0)
    printf("Error return from gettimeofday: %d", stat);
  return (Tp.tv_sec + Tp.tv_usec * 1.0e-7);
}
void pluto_mttkrp(double B[const restrict 500][500][500],
                  double C[const restrict 500][500],
                  double D[const restrict 500][500],
                  double A[const restrict 500][500][500]) {

  int i1, i2, i3;

  for (i1 = 0; i1 < 500; i1 += 1) {
    for (i2 = 0; i2 < 500; i2 += 1) {
      for (i3 = 0; i3 < 500; i3 += 1) {
        B[i1][i2][i3] = 1;
      }
    }
  }
  for (i1 = 0; i1 < 500; i1 += 1) {
    for (i2 = 0; i2 < 500; i2 += 1) {
      C[i1][i2] = 1;
    }
  }
  for (i1 = 0; i1 < 500; i1 += 1) {
    for (i2 = 0; i2 < 500; i2 += 1) {
      D[i1][i2] = 1;
    }
  }
  for (i1 = 0; i1 < 500; i1 += 1) {
    for (i2 = 0; i2 < 500; i2 += 1) {
      for (i3 = 0; i3 < 500; i3 += 1) {
        A[i1][i2][i3] = 0;
      }
    }
  }

  double begin, end;
  begin = rtclock();
  for (i1 = 0; i1 <= 499; i1 += 1) {
    for (i2 = 0; i2 <= 499; i2 += 1) {
      for (i3 = 0; i3 <= 499; i3 += 1) {
        for (i4 = 0; i4 <= 499; i4 += 1) {
          A[i1][i2][i3] *= B[i1][i2][i4] * D[i4][i3] * C[i4][i3];
        }
      }
    }
  }
#pragma omp parallel for schedule(static, None)
  for (i1 = 0; i1 <= 499; i1 += 1) {
    for (i2 = 0; i2 <= 499; i2 += 1) {
      for (i3 = 0; i3 <= 499; i3 += 1) {
        for (i4 = 0; i4 <= 499; i4 += 1) {
          A[i1][i3][i2] *= B[i1][i3][i4] * D[i4][i2] * C[i4][i2];
        }
      }
    }
  }
  end = rtclock();
}

int main(int *argc, char **argv) {
  double(*B)[500][500][500] = malloc(sizeof *B);
  double(*C)[500][500] = malloc(sizeof *C);
  double(*D)[500][500] = malloc(sizeof *D);
  double(*A)[500][500][500] = malloc(sizeof *A);
  pluto_mttkrp(B, C, D, A);
  free(B);
  free(C);
  free(D);
  free(A);
  return 0;
}