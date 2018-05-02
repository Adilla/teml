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
void sddmm(
    double B[const restrict 4096][4096], double Z[const restrict 4096][4096],
    double Z1[const restrict 4096][4096], double Z2[const restrict 4096][4096],
    double Z3[const restrict 4096][4096], double Z4[const restrict 4096][4096],
    double H[const restrict 4096][4096], double C[const restrict 4096][4096],
    double D[const restrict 4096][4096], double A[const restrict 4096][4096]) {

  int i1, i2;

  for (i1 = 0; i1 < 4096; i1 += 1) {
    for (i2 = 0; i2 < 4096; i2 += 1) {
      B[i1][i2] = 1;
    }
  }
  for (i1 = 0; i1 < 4096; i1 += 1) {
    for (i2 = 0; i2 < 4096; i2 += 1) {
      Z[i1][i2] = 0;
    }
  }
  for (i1 = 0; i1 < 4096; i1 += 1) {
    for (i2 = 0; i2 < 4096; i2 += 1) {
      Z1[i1][i2] = 1;
    }
  }
  for (i1 = 0; i1 < 4096; i1 += 1) {
    for (i2 = 0; i2 < 4096; i2 += 1) {
      if (i1 == i2)
        Z2[i1][i2] = 1;
    }
  }
  for (i1 = 0; i1 < 4096; i1 += 1) {
    for (i2 = 0; i2 < 4096; i2 += 1) {
      if (i2 == (i1 + 1))
        Z3[i1][i2] = 1;
    }
  }
  for (i1 = 0; i1 < 4096; i1 += 1) {
    for (i2 = 0; i2 < 4096; i2 += 1) {
      if (i2 == (i1 - 1))
        Z4[i1][i2] = 1;
    }
  }
  for (i1 = 0; i1 < 4096; i1 += 1) {
    for (i2 = 0; i2 < 4096; i2 += 1) {
      H[i1][i2] = 1 / (i1 + i2 - 1);
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
  double(*Z)[4096][4096] = malloc(sizeof *Z);
  double(*Z1)[4096][4096] = malloc(sizeof *Z1);
  double(*Z2)[4096][4096] = malloc(sizeof *Z2);
  double(*Z3)[4096][4096] = malloc(sizeof *Z3);
  double(*Z4)[4096][4096] = malloc(sizeof *Z4);
  double(*H)[4096][4096] = malloc(sizeof *H);
  double(*C)[4096][4096] = numa_alloc_interleaved(sizeof *C);
  double(*D)[4096][4096] = numa_alloc_onnode(sizeof *D, 0);
  double(*A)[4096][4096] = malloc(sizeof *A);

  sddmm(B, Z, Z1, Z2, Z3, Z4, H, C, D, A);

  _mm_free(B);
  free(Z);
  free(Z1);
  free(Z2);
  free(Z3);
  free(Z4);
  free(H);
  numa_free(C, sizeof *C);
  numa_free(D, sizeof *D);
  free(A);

  return 0;
}