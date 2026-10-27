/* A tiny invented wire format: 2-byte big-endian length, then payload. */
#include <stdint.h>
#include <stdio.h>

static int payload_length(const unsigned char *data, size_t size, size_t *out) {
    if (!data || size < 2) return 0;
    size_t length = ((size_t)data[0] << 8) | data[1];
    if (length != size - 2) return 0;
    *out = length;
    return 1;
}

int main(void) {
    const unsigned char normal[] = {0, 3, 'B', 'I', 'F'};
    const unsigned char short_header[] = {0};
    const unsigned char short_body[] = {0, 4, 'B', 'I', 'F'};
    const unsigned char extra[] = {0, 1, 'B', 'I'};
    size_t length = 0;
    int ok = payload_length(normal, sizeof normal, &length);
    if (ok) printf("normal=OK length=%zu\n", length);
    else puts("normal=REJECT");
    printf("short-header=%s\n", payload_length(short_header, sizeof short_header, &length) ? "OK" : "REJECT");
    printf("short-body=%s\n", payload_length(short_body, sizeof short_body, &length) ? "OK" : "REJECT");
    printf("extra-byte=%s\n", payload_length(extra, sizeof extra, &length) ? "OK" : "REJECT");
    return 0;
}
