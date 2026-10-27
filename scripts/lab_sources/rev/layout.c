/* Original ELF layout sample. Build on Linux/WSL with -O0. */
#include <stdio.h>

const char banner[] = "BF-LAYOUT";
static int initialized = 7;
static unsigned char zeroed[1024];

int main(void) {
    printf("%s init=%d zero=%u\n", banner, initialized, (unsigned)zeroed[0]);
    return 0;
}
