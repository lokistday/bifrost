#include <stddef.h>
int parse(const unsigned char *data, size_t size,
          const unsigned char **payload, size_t *length) {
    if (!data || !payload || !length || size < 2) return 0;
    size_t n = ((size_t)data[0] << 8) | data[1];
    if (n > 8 || size - 2 != n) return 0;
    *payload = data + 2;
    *length = n;
    return 1;
}
