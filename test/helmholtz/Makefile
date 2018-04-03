CC=gcc -march=native -O3 -g
CFLAGS=
LIBS=-fopenmp

SRCS = $(wildcard *.c)

EXECS = $(SRCS:%.c=%.o)

all: 	$(EXECS)

%: %.c
	$(CC) $(CFLAGS) -o $@ $< $(LIBS)

.PHONY: clean

clean:
	rm *.o
