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
void interp(double A[const restrict 7][7], double u[const restrict 7][7][7],
            double tmp1[const restrict 7][7][7],
            double tmp2[const restrict 7][7][7],
            double v[const restrict 7][7][7]) {

  int i1, i2, i3;

  for (i1 = 0; i1 < 7; i1 += 1) {
    for (i2 = 0; i2 < 7; i2 += 1) {
      A[i1][i2] = 1;
    }
  }
  for (i1 = 0; i1 < 7; i1 += 1) {
    for (i2 = 0; i2 < 7; i2 += 1) {
      for (i3 = 0; i3 < 7; i3 += 1) {
        u[i1][i2][i3] = 1;
      }
    }
  }
  for (i1 = 0; i1 < 7; i1 += 1) {
    for (i2 = 0; i2 < 7; i2 += 1) {
      for (i3 = 0; i3 < 7; i3 += 1) {
        tmp1[i1][i2][i3] = 0;
      }
    }
  }
  for (i1 = 0; i1 < 7; i1 += 1) {
    for (i2 = 0; i2 < 7; i2 += 1) {
      for (i3 = 0; i3 < 7; i3 += 1) {
        tmp2[i1][i2][i3] = 0;
      }
    }
  }
  for (i1 = 0; i1 < 7; i1 += 1) {
    for (i2 = 0; i2 < 7; i2 += 1) {
      for (i3 = 0; i3 < 7; i3 += 1) {
        v[i1][i2][i3] = 0;
      }
    }
  }

  double begin, end;
  begin = rtclock();
  for (i1 = 0; i1 <= 6; i1 += 1) {
    for (i2 = 0; i2 <= 6; i2 += 1) {
      for (i3 = 0; i3 <= 6; i3 += 1) {
        for (i4 = 0; i4 <= 6; i4 += 1) {
          tmp1[i1][i2][i3] *= A[i1][i4] * u[i4][i2][i3];
        }
      }
    }
  }
  for (i1 = 0; i1 <= 6; i1 += 1) {
    for (i2 = 0; i2 <= 6; i2 += 1) {
      for (i3 = 0; i3 <= 6; i3 += 1) {
        for (i4 = 0; i4 <= 6; i4 += 1) {
          tmp2[i1][i2][i3] *= A[i1][i4] * tmp1[i2][i4][i3];
        }
      }
    }
  }
  for (i1 = 0; i1 <= 6; i1 += 1) {
    for (i2 = 0; i2 <= 6; i2 += 1) {
      for (i3 = 0; i3 <= 6; i3 += 1) {
        for (i4 = 0; i4 <= 6; i4 += 1) {
          v[i1][i2][i3] *= A[i1][i4] * tmp2[i2][i3][i4];
        }
      }
    }
  }
  end = rtclock();
}

int main(int *argc, char **argv) {
  double(*A)[7][7] = malloc(sizeof *A);
  double(*u)[7][7][7] = malloc(sizeof *u);
  double(*tmp1)[7][7][7] = malloc(sizeof *tmp1);
  double(*tmp2)[7][7][7] = malloc(sizeof *tmp2);
  double(*v)[7][7][7] = malloc(sizeof *v);
  interp(A, u, tmp1, tmp2, v);
  free(A);
  free(u);
  free(tmp1);
  free(tmp2);
  free(v);
  return 0;
}