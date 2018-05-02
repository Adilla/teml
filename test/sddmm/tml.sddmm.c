#include <libnuma.h>
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
void sddmm(double B[const restrict 4096][4096],
           double C[const restrict 4096][4096],
           double D[const restrict 4096][4096],
           double A[const restrict 4096][4096]) {

  int i1, i2;

  for (i1 = 0; i1 < 4096; i1 += 1) {
    for (i2 = 0; i2 < 4096; i2 += 1) {
      B[i1][i2] = 1;
    }
  }
  for (i1 = 0; i1 < 4096; i1 += 1) {
    for (i2 = 0; i2 < 4096; i2 += 1) {
      C[i1][i2] = 1;
    }
  }
  for (i1 = 0; i1 < 4096; i1 += 1) {
    for (i2 = 0; i2 < 4096; i2 += 1) {
      D[i1][i2] = 1;
    }
  }
  for (i1 = 0; i1 < 4096; i1 += 1) {
    for (i2 = 0; i2 < 4096; i2 += 1) {
      A[i1][i2] = 0;
    }
  }

  double begin, end;
  begin = rtclock();
  for (i1 = 0; i1 <= 4095; i1 += 1) {
    for (i2 = 0; i2 <= 4095; i2 += 1) {
      for (i3 = 0; i3 <= 4095; i3 += 1) {
        A[i1][i2] = B[i1][i2] * C[i1][i3] * D[i3][i2];
      }
    }
  }
  end = rtclock();
}

int main(int *argc, char **argv) {
  double(*B)[4096][4096] = _mm_malloc(sizeof *B, 64);
  double(*C)[4096][4096] = numa_alloc_interleaved(sizeof *C);
  double(*D)[4096][4096] = numa_alloc_onnode(sizeof *D, 0);
  double(*A)[4096][4096] = malloc(sizeof *A);

  sddmm(B, C, D, A);

  _mm_free(B);
  numa_free(C, sizeof *C);
  numa_free(D, sizeof *D);
  free(A);

  return 0;
}