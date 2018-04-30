#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/time.h>
#include <omp.h>

double rtclock() {
 struct timezone Tzp;
 struct timeval Tp;
 int stat;
 stat = gettimeofday(&Tp, &Tzp);if (stat != 0) printf("Error return from gettimeofday: %d", stat);
return(Tp.tv_sec + Tp.tv_usec*1.0e-7);
}
void gconv(double I[const restrict 32][32][30][16][12][14],
double W1[const restrict 32][32][16][16][3][3],
double B[const restrict 32][32][16]) {
for (i1 = 0; i1 < 32; i1+= 1) {
for (i2 = 0; i2 < 30; i2+= 1) {
for (i3 = 0; i3 < 16; i3+= 1) {
for (i4 = 0; i4 < 12; i4+= 1) {
for (i5 = 0; i5 < 14; i5+= 1) {
I[i1][i2][i3][i4][i5] = 7;
}
}
}
}
}
for (i1 = 0; i1 < 32; i1+= 1) {
for (i2 = 0; i2 < 16; i2+= 1) {
for (i3 = 0; i3 < 16; i3+= 1) {
for (i4 = 0; i4 < 3; i4+= 1) {
for (i5 = 0; i5 < 3; i5+= 1) {
W1[i1][i2][i3][i4][i5] = 8;
}
}
}
}
}
for (i1 = 0; i1 < 32; i1+= 1) {
for (i2 = 0; i2 < 16; i2+= 1) {
B[i1][i2] = 4;
}
}
double begin, end;
begin = rtclock();
for (i1 = 0; i1 <= 31; i1 += 1)  {
for (i2 = 0; i2 <= 29; i2 += 1)  {
for (i3 = 0; i3 <= 15; i3 += 1)  {
for (i4 = 0; i4 <= 15; i4 += 1)  {
for (i5 = 0; i5 <= 6; i5 += 1)  {
for (i6 = 0; i6 <= 11; i6 += 1)  {
for (i7 = 0; i7 <= 2; i7 += 1)  {
for (i8 = 0; i8 <= 2; i8 += 1)  {
O[i1][i2][i3][i5][i6] = I[i1][i2][i4][i5 + 5][i6 + 2] * W1[i2][i3][i4][i7][i8];
}
}
}
}
}
}
}
}
for (i1 = 0; i1 <= 31; i1 += 1)  {
for (i2 = 0; i2 <= 29; i2 += 1)  {
for (i3 = 0; i3 <= 15; i3 += 1)  {
for (i4 = 0; i4 <= 6; i4 += 1)  {
for (i5 = 0; i5 <= 11; i5 += 1)  {
O1[i1][i2][i3][i4][i5] = O[i1][i2][i3][i4][i5] + B[i2][i3];
}
}
}
}
}
for (i1 = 0; i1 <= 31; i1 += 1)  {
for (i2 = 0; i2 <= 29; i2 += 1)  {
for (i3 = 0; i3 <= 15; i3 += 1)  {
for (i4 = 0; i4 <= 6; i4 += 1)  {
O1[i1][i2][i3][i4][0] = O[i1][i2][i3][i4][0] + B[i2][i3];
O1[i1][i2][i3][i4][1] = O[i1][i2][i3][i4][1] + B[i2][i3];
O1[i1][i2][i3][i4][2] = O[i1][i2][i3][i4][2] + B[i2][i3];
O1[i1][i2][i3][i4][3] = O[i1][i2][i3][i4][3] + B[i2][i3];
O1[i1][i2][i3][i4][4] = O[i1][i2][i3][i4][4] + B[i2][i3];
O1[i1][i2][i3][i4][5] = O[i1][i2][i3][i4][5] + B[i2][i3];
O1[i1][i2][i3][i4][6] = O[i1][i2][i3][i4][6] + B[i2][i3];
O1[i1][i2][i3][i4][7] = O[i1][i2][i3][i4][7] + B[i2][i3];
O1[i1][i2][i3][i4][8] = O[i1][i2][i3][i4][8] + B[i2][i3];
O1[i1][i2][i3][i4][9] = O[i1][i2][i3][i4][9] + B[i2][i3];
O1[i1][i2][i3][i4][10] = O[i1][i2][i3][i4][10] + B[i2][i3];
}
}
}
}
end = rtclock();
}

int main(int * argc, char ** argv) {double (*I)[32][30][16][12][14] = malloc(sizeof * I);
double (*W1)[32][16][16][3][3] = malloc(sizeof * W1);
double (*B)[32][16] = malloc(sizeof * B);
gconv(I, W1, B);
free(I);
free(W1);
free(B);
return 0;
}