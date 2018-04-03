#CC=icc -O3 -msse4.2 -openmp  #-qopt-report=1 -qopt-report-phase=vec,openmp,loop,par
CC=gcc -O3 -fopenmp -march=native -g -lm
CFLAGS=
LIBS=

SRCS = $(wildcard *.c)

EXECS = $(SRCS:%.c=%)

all: 	$(EXECS)

%: %.c
	$(CC) $(CFLAGS) -o $@ $< $(LIBS)

.PHONY: clean

clean:
	rm $(EXECS)
