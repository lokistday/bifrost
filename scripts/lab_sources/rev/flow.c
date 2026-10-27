/* Input is data, never shell code. Zero terminates this toy traversal. */
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <limits.h>

int sum_positive(const int *values, size_t count) {
    int total = 0;
    for (size_t i = 0; i < count; ++i) {
        if (values[i] == 0) break;
        if (values[i] < 0) continue;
        total += values[i];
    }
    return total;
}

int main(int argc, char **argv) {
    if (argc < 2 || argc > 9) { fputs("usage: flow INT... (1..8 values, -100..100)\n", stderr); return 2; }
    int values[8];
    for (int i = 1; i < argc; ++i) {
        char *end;
        errno = 0;
        long n = strtol(argv[i], &end, 10);
        if (errno || end == argv[i] || *end || n < -100 || n > 100) {
            fputs("INVALID integer\n", stderr); return 2;
        }
        values[i - 1] = (int)n;
    }
    printf("sum=%d\n", sum_positive(values, (size_t)(argc - 1)));
    return 0;
}
