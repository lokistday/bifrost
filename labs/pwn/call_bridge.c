#include <stdio.h>

static int seed = 7;
static const char banner[] = "BIFROST";

int adjust(int base) {
    int bumped = base + 3;
    int result = bumped * 2;
    return result;
}

int main(void) {
    int value = seed;
    int answer = adjust(value);
    printf("%s value=%d answer=%d\n", banner, value, answer);
    return 0;
}
