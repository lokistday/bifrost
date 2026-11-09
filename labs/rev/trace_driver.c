#include <stdio.h>
unsigned int trace_steps(unsigned int x);
int main(void) {
    unsigned int inputs[] = {5, 7, 8};
    for (unsigned int i = 0; i < 3; ++i) {
        printf("x=%u result=%u\n", inputs[i], trace_steps(inputs[i]));
    }
    return 0;
}
