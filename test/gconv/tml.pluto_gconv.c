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
void pluto_gconv(double I[const restrict 32][30][16][12][14],
                 double W1[const restrict 32][16][16][3][3],
                 double B[const restrict 32][16],
                 double O[const restrict 32][30][16][11][13],
                 double O1[const restrict 32][30][16][11][13]) {

  int i1, i2, i3, i4, i5;

  for (i1 = 0; i1 < 32; i1 += 1) {
    for (i2 = 0; i2 < 30; i2 += 1) {
      for (i3 = 0; i3 < 16; i3 += 1) {
        for (i4 = 0; i4 < 12; i4 += 1) {
          for (i5 = 0; i5 < 14; i5 += 1) {
            I[i1][i2][i3][i4][i5] = 1;
          }
        }
      }
    }
  }
  for (i1 = 0; i1 < 32; i1 += 1) {
    for (i2 = 0; i2 < 16; i2 += 1) {
      for (i3 = 0; i3 < 16; i3 += 1) {
        for (i4 = 0; i4 < 3; i4 += 1) {
          for (i5 = 0; i5 < 3; i5 += 1) {
            W1[i1][i2][i3][i4][i5] = 1;
          }
        }
      }
    }
  }
  for (i1 = 0; i1 < 32; i1 += 1) {
    for (i2 = 0; i2 < 16; i2 += 1) {
      B[i1][i2] = 1;
    }
  }
  for (i1 = 0; i1 < 32; i1 += 1) {
    for (i2 = 0; i2 < 30; i2 += 1) {
      for (i3 = 0; i3 < 16; i3 += 1) {
        for (i4 = 0; i4 < 11; i4 += 1) {
          for (i5 = 0; i5 < 13; i5 += 1) {
            O[i1][i2][i3][i4][i5] = 0;
          }
        }
      }
    }
  }
  for (i1 = 0; i1 < 32; i1 += 1) {
    for (i2 = 0; i2 < 30; i2 += 1) {
      for (i3 = 0; i3 < 16; i3 += 1) {
        for (i4 = 0; i4 < 11; i4 += 1) {
          for (i5 = 0; i5 < 13; i5 += 1) {
            O1[i1][i2][i3][i4][i5] = 0;
          }
        }
      }
    }
  }

  double begin, end;
  begin = rtclock();
#pragma omp parallel for schedule(static, None)
  for (i1 = 0; i1 <= 31; i1 += 1) {
    for (i2 = 0; i2 <= 29; i2 += 1) {
      for (i3 = 0; i3 <= 15; i3 += 1) {
        for (i4 = 0; i4 <= 10; i4 += 1) {
          for (i5 = 0; i5 <= 12; i5 += 1) {
            for (i6 = 0; i6 <= 15; i6 += 1) {
              for (i7 = 0; i7 <= 2; i7 += 1) {
                for (i8 = 0; i8 <= 2; i8 += 1) {
                  O[i1][i2][i3][i4][i5] =
                      I[i1][i2][i6][i5 + 1][i6 + 1] * W1[i2][i3][i6][i7][i8];
                }
              }
            }
          }
        }
      }
    }
  }
  for (i1 = 0; i1 <= 31; i1 += 1) {
    for (i2 = 0; i2 <= 29; i2 += 1) {
      for (i3 = 0; i3 <= 15; i3 += 1) {
        for (i4 = 0; i4 <= 10; i4 += 1) {
          for (i5 = 0; i5 <= 12; i5 += 1) {
            O1[i1][i2][i3][i4][i5] = O[i1][i2][i3][i4][i5] + B[i2][i3];
          }
        }
      }
    }
  }
  end = rtclock();
}

int main(int *argc, char **argv) {
  double(*I)[32][30][16][12][14] = malloc(sizeof *I);
  double(*W1)[32][16][16][3][3] = malloc(sizeof *W1);
  double(*B)[32][16] = malloc(sizeof *B);
  double(*O)[32][30][16][11][13] = malloc(sizeof *O);
  double(*O1)[32][30][16][11][13] = malloc(sizeof *O1);
  pluto_gconv(I, W1, B, O, O1);
  free(I);
  free(W1);
  free(B);
  free(O);
  free(O1);
  return 0;
}