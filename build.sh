gcc -c -O3 -Wall -std=gnu99 -fPIC cmap.c -o cmap.o
gcc cmap.o -shared -o libcmap.so
