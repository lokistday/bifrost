/* C11: explicit numeric syntax, conversion errors, range, then cast. */
#include <errno.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>

static int parse_count(const char *text, size_t *out) {
    char *end;
    if (!text || !*text) return 0;
    for (const char *p = text; *p; ++p)
        if (*p < '0' || *p > '9') return 0;
    errno = 0;
    uintmax_t value = strtoumax(text, &end, 10);
    if (errno == ERANGE || *end != '\0' || value > 1024) return 0;
    *out = (size_t)value;
    return 1;
}

int main(int argc, char **argv) {
    size_t count = 0;
    if (argc != 2 || !parse_count(argv[1], &count)) {
        puts("INVALID_COUNT");
        return 2;
    }
    printf("count=%zu\n", count);
    return 0;
}
