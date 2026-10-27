/* Own benign x86-64 System V ABI example; no binaries are distributed. */
#include <stdio.h>

__attribute__((noinline)) int combine(int a, int b, int c) {
    return a + 2 * b + c;
}

int main(void) {
    int value = combine(3, 5, 7);
    printf("result=%d\n", value);
    return value == 20 ? 0 : 1;
}
