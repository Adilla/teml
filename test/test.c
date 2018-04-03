int main() {

#pragma omp parallel for private(i2, i3)
  for (i1 = 0; i1 < N; i1 += 1) {
    for (i2 = 0; i2 < N; i2 += 1) {
      for (i3 = 0; i3 < N; i3 += 1) {
	rt[i1 *(N + i2 * (N + i3))] = w[i1] * w[i2] * w[i3] * ut[i1 * (N + i2 * (N + i3))];
      }
    }
  }
  for (j1 = 0; j1 < N; j1 += 1) {
    for (j2 = 0; j2 < N; j2 += 1) {
      for (j3 = 0; j3 < N; j3 += 1) {
	for (j4 = 0; j4 < N; j4 += 1) {
	  rt[j1 *(N + j2 * (N + j3))] += L[j1 * N + j4] * w[j2] * w[j3] * ut[j4 * (N + j2 * (N + j3))];
	}
      }
    }
  }


  for (i1 = 0; i1 < N; i1 += 1) {
    for (i2 = 0; i2 < N; i2 += 1) {
      for (i3 = 0; i3 < N; i3 += 1) {
	rt[i1][i2][i3] = w[i1] * w[i2] * w[i3] * ut[i1][i2][i3];
      }
    }
  }
  for (j1 = 0; j1 < N; j1 += 1) {
    for (j2 = 0; j2 < N; j2 += 1) {
      for (j3 = 0; j3 < N; j3 += 1) {
	for (j4 = 0; j4 < N; j4 += 1) {
	  rt[j1][j2][j3] += L[j1][j4] * w[j2] * w[j3] * ut[j4][j2][j3];
	}
      }
    }
  }


  return 0;
}
