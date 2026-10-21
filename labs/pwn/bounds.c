/* Deliberate LOCAL teaching error. Compile with AddressSanitizer first. */
#include <stdio.h>
int main(void) {
    int values[3] = {10, 20, 30};
    for (int i = 0; i <= 3; ++i) printf("%d\n", values[i]);
    return 0;
}
