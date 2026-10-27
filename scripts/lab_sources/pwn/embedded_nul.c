/* Binary buffers have explicit lengths; an embedded NUL ends a C string early. */
#include <stdio.h>
#include <string.h>

static int ascii_text(const unsigned char *data, size_t size) {
    if (!data || size == 0 || size > 32) return 0;
    for (size_t i = 0; i < size; ++i)
        if (data[i] < 0x20 || data[i] > 0x7e) return 0;
    return 1;
}

int main(void) {
    const unsigned char data[] = {'A', 'B', 0, 'C', 'D'};
    const unsigned char plain[] = {'A', 'B', 'C', 'D'};
    printf("buffer_bytes=%zu string_length=%zu\n", sizeof data, strlen((const char *)data));
    printf("hex=");
    for (size_t i = 0; i < sizeof data; ++i) printf("%02x", (unsigned)data[i]);
    putchar('\n');
    printf("text_contract=%s\n", ascii_text(data, sizeof data) ? "ACCEPT" : "REJECT_NUL");
    printf("plain_text=%s\n", ascii_text(plain, sizeof plain) ? "ACCEPT" : "REJECT");
    return 0;
}
