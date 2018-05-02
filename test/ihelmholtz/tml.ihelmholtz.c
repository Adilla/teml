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
void ihelmholtz(double A[const restrict 13][13]) {

  int i1, i2;

  for (i1 = 0; i1 < 13; i1 += 1) {
    for (i2 = 0; i2 < 13; i2 += 1) {
      A[i1][i2] = 1;
    }
  }

  double begin, end;
  begin = rtclock();
  for (i1 = 0; i1 <= 12; i1 += 1) {
    for (i2 = 0; i2 <= 12; i2 += 1) {
      for (i3 = 0; i3 <= 12; i3 += 1) {
        for (i4 = 0; i4 <= 12; i4 += 1) {
          tmp1[i1][i2][i3] *= A[i2][i1] * u[i4][i2][i3];
        }
      }
    }
  }
  end = rtclock();
}

int main(int *argc, char **argv) {
  double(*A)[13][13] = malloc(sizeof *A);

  ihelmholtz(A);

  free(A);

  return 0;
}