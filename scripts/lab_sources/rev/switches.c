#include <stdio.h>

__attribute__((noinline)) int classify(int value) {
    switch (value) {
        case 0: return 11;
        case 1: return 17;
        case 2: return 23;
        case 3: return 31;
        case 4: return 47;
        case 5: return 59;
        default: return -1;
    }
}

int main(void) {
    const int inputs[] = {-1, 0, 1, 2, 3, 4, 5, 6};
    for (unsigned i = 0; i < sizeof inputs / sizeof inputs[0]; ++i)
        printf("%d:%d%s", inputs[i], classify(inputs[i]), i == 7 ? "\n" : " ");
    return 0;
}
