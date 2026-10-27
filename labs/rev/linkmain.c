#include <stdio.h>

extern int adjust(int value);

int main(void) {
    printf("adjusted=%d\n", adjust(5));
    return 0;
}
