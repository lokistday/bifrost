#include <stddef.h>
/* Input is caller-owned. On success set payload/length. No allocation.
   Implement first; tests should fail while this returns 0 for every input. */
int parse(const unsigned char *data, size_t size,
          const unsigned char **payload, size_t *length) {
    (void)data; (void)size; (void)payload; (void)length;
    return 0;
}
