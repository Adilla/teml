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
void ihelmholtz_def(double A[const restrict 13][13],
                    double D[const restrict 13][13][13],
                    double u[const restrict 13][13][13],
                    double tmp1[const restrict 13][13][13],
                    double tmp2[const restrict 13][13][13],
                    double tmp3[const restrict 13][13][13],
                    double tmp4[const restrict 13][13][13],
                    double tmp5[const restrict 13][13][13],
                    double tmp6[const restrict 13][13][13],
                    double v[const restrict 13][13][13]) {

  int i1, i2, i3;

  for (i1 = 0; i1 < 13; i1 += 1) {
    for (i2 = 0; i2 < 13; i2 += 1) {
      A[i1][i2] = 1;
    }
  }
  for (i1 = 0; i1 < 13; i1 += 1) {
    for (i2 = 0; i2 < 13; i2 += 1) {
      for (i3 = 0; i3 < 13; i3 += 1) {
        D[i1][i2][i3] = 1;
      }
    }
  }
  for (i1 = 0; i1 < 13; i1 += 1) {
    for (i2 = 0; i2 < 13; i2 += 1) {
      for (i3 = 0; i3 < 13; i3 += 1) {
        u[i1][i2][i3] = 1;
      }
    }
  }
  for (i1 = 0; i1 < 13; i1 += 1) {
    for (i2 = 0; i2 < 13; i2 += 1) {
      for (i3 = 0; i3 < 13; i3 += 1) {
        tmp1[i1][i2][i3] = 0;
      }
    }
  }
  for (i1 = 0; i1 < 13; i1 += 1) {
    for (i2 = 0; i2 < 13; i2 += 1) {
      for (i3 = 0; i3 < 13; i3 += 1) {
        tmp2[i1][i2][i3] = 0;
      }
    }
  }
  for (i1 = 0; i1 < 13; i1 += 1) {
    for (i2 = 0; i2 < 13; i2 += 1) {
      for (i3 = 0; i3 < 13; i3 += 1) {
        tmp3[i1][i2][i3] = 0;
      }
    }
  }
  for (i1 = 0; i1 < 13; i1 += 1) {
    for (i2 = 0; i2 < 13; i2 += 1) {
      for (i3 = 0; i3 < 13; i3 += 1) {
        tmp4[i1][i2][i3] = 0;
      }
    }
  }
  for (i1 = 0; i1 < 13; i1 += 1) {
    for (i2 = 0; i2 < 13; i2 += 1) {
      for (i3 = 0; i3 < 13; i3 += 1) {
        tmp5[i1][i2][i3] = 0;
      }
    }
  }
  for (i1 = 0; i1 < 13; i1 += 1) {
    for (i2 = 0; i2 < 13; i2 += 1) {
      for (i3 = 0; i3 < 13; i3 += 1) {
        tmp6[i1][i2][i3] = 0;
      }
    }
  }
  for (i1 = 0; i1 < 13; i1 += 1) {
    for (i2 = 0; i2 < 13; i2 += 1) {
      for (i3 = 0; i3 < 13; i3 += 1) {
        v[i1][i2][i3] = 0;
      }
    }
  }

  double begin, end;
  begin = rtclock();
  for (i1 = 0; i1 <= 12; i1 += 1) {
    for (i2 = 0; i2 <= 12; i2 += 1) {
      for (i3 = 0; i3 <= 12; i3 += 1) {
        for (i4 = 0; i4 <= 12; i4 += 1) {
          tmp1[i1][i2][i3] += A[i4][i1] * u[i4][i2][i3];
        }
      }
    }
  }
  for (i1 = 0; i1 <= 12; i1 += 1) {
    for (i2 = 0; i2 <= 12; i2 += 1) {
      for (i3 = 0; i3 <= 12; i3 += 1) {
        for (i4 = 0; i4 <= 12; i4 += 1) {
          tmp2[i1][i2][i3] += A[i4][i1] * tmp1[i2][i4][i3];
        }
      }
    }
  }
  for (i1 = 0; i1 <= 12; i1 += 1) {
    for (i2 = 0; i2 <= 12; i2 += 1) {
      for (i3 = 0; i3 <= 12; i3 += 1) {
        for (i4 = 0; i4 <= 12; i4 += 1) {
          tmp3[i1][i2][i3] += A[i4][i1] * tmp2[i2][i3][i4];
        }
      }
    }
  }
  for (i1 = 0; i1 <= 12; i1 += 1) {
    for (i2 = 0; i2 <= 12; i2 += 1) {
      for (i3 = 0; i3 <= 12; i3 += 1) {
        tmp4[i1][i2][i3] = D[i1][i2][i3] * tmp3[i1][i2][i3];
      }
    }
  }
  for (i1 = 0; i1 <= 12; i1 += 1) {
    for (i2 = 0; i2 <= 12; i2 += 1) {
      for (i3 = 0; i3 <= 12; i3 += 1) {
        for (i4 = 0; i4 <= 12; i4 += 1) {
          tmp5[i1][i2][i3] += A[i1][i4] * tmp4[i4][i2][i3];
        }
      }
    }
  }
  for (i1 = 0; i1 <= 12; i1 += 1) {
    for (i2 = 0; i2 <= 12; i2 += 1) {
      for (i3 = 0; i3 <= 12; i3 += 1) {
        for (i4 = 0; i4 <= 12; i4 += 1) {
          tmp6[i1][i2][i3] += A[i1][i4] * tmp5[i2][i4][i3];
        }
      }
    }
  }
  for (i1 = 0; i1 <= 12; i1 += 1) {
    for (i2 = 0; i2 <= 12; i2 += 1) {
      for (i3 = 0; i3 <= 12; i3 += 1) {
        for (i4 = 0; i4 <= 12; i4 += 1) {
          v[i1][i2][i3] += A[i1][i4] * tmp6[i2][i3][i4];
        }
      }
    }
  }
  end = rtclock();
  printf("Time: %0.6lfs\n", end - begin);
}

int main(int *argc, char **argv) {
  double(*A)[13][13] = malloc(sizeof *A);
  double(*D)[13][13][13] = malloc(sizeof *D);
  double(*u)[13][13][13] = malloc(sizeof *u);
  double(*tmp1)[13][13][13] = malloc(sizeof *tmp1);
  double(*tmp2)[13][13][13] = malloc(sizeof *tmp2);
  double(*tmp3)[13][13][13] = malloc(sizeof *tmp3);
  double(*tmp4)[13][13][13] = malloc(sizeof *tmp4);
  double(*tmp5)[13][13][13] = malloc(sizeof *tmp5);
  double(*tmp6)[13][13][13] = malloc(sizeof *tmp6);
  double(*v)[13][13][13] = malloc(sizeof *v);

  ihelmholtz_def(A, D, u, tmp1, tmp2, tmp3, tmp4, tmp5, tmp6, v);

  free(A);
  free(D);
  free(u);
  free(tmp1);
  free(tmp2);
  free(tmp3);
  free(tmp4);
  free(tmp5);
  free(tmp6);
  free(v);

  return 0;
}