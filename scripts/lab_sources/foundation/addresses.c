#include <stdio.h>
int main(void) {
    int value = 7;
    int *pointer = &value;
    printf("value=%d dereferenced=%d\n", value, *pointer);
    printf("address=%p\n", (void *)pointer);
    *pointer = 9;
    printf("after=%d\n", value);
    return 0;
}
