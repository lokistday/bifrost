/* Check before multiply/add; exercise does not allocate huge buffers. */
#include <stdint.h>
#include <stdio.h>

static int allocation_size(size_t count, size_t element, size_t header, size_t *out) {
    if (!element || count > (SIZE_MAX - header) / element) return 0;
    *out = header + count * element;
    return 1;
}

int main(void) {
    size_t bytes = 0;
    int ok = allocation_size(3, 4, 8, &bytes);
    printf("small=%s bytes=%zu\n", ok ? "OK" : "REJECT", bytes);
    ok = allocation_size(SIZE_MAX, 4, 8, &bytes);
    printf("huge=%s\n", ok ? "OK" : "REJECT");
    ok = allocation_size(0, 4, 8, &bytes);
    printf("empty=%s bytes=%zu\n", ok ? "OK" : "REJECT", bytes);
    ok = allocation_size(1, 0, 8, &bytes);
    printf("zero-element=%s\n", ok ? "OK" : "REJECT");
    return 0;
}
