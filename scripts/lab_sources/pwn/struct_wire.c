/* Inspect host layout separately; explicitly encode a seven-byte wire record. */
#include <limits.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

_Static_assert(CHAR_BIT == 8, "This exercise requires eight-bit bytes");
struct record { unsigned char type; uint32_t code; uint16_t count; };

static void encode(unsigned char out[7], const struct record *value) {
    out[0] = value->type;
    for (size_t i = 0; i < 4; ++i) out[1 + i] = (unsigned char)(value->code >> (24 - 8 * i));
    out[5] = (unsigned char)(value->count >> 8);
    out[6] = (unsigned char)value->count;
}

static int decode(const unsigned char *data, size_t size, struct record *out) {
    if (!data || size != 7) return 0;
    out->type = data[0];
    out->code = ((uint32_t)data[1] << 24) | ((uint32_t)data[2] << 16)
                | ((uint32_t)data[3] << 8) | (uint32_t)data[4];
    out->count = (uint16_t)(((uint16_t)data[5] << 8) | (uint16_t)data[6]);
    return 1;
}

int main(int argc, char **argv) {
    if (argc == 2 && strcmp(argv[1], "--layout") == 0) {
        printf("struct_size=%zu type_offset=%zu code_offset=%zu count_offset=%zu\n",
               sizeof(struct record), offsetof(struct record, type), offsetof(struct record, code),
               offsetof(struct record, count));
        return 0;
    }
    if (argc != 1) return 2;
    const struct record input = {1, UINT32_C(0x01020304), UINT16_C(0x0506)};
    struct record decoded = {0};
    unsigned char wire[7];
    encode(wire, &input);
    printf("wire_bytes=%zu hex=", sizeof wire);
    for (size_t i = 0; i < sizeof wire; ++i) printf("%02x", (unsigned)wire[i]);
    putchar('\n');
    if (!decode(wire, sizeof wire, &decoded)) return 2;
    printf("roundtrip=%s\n", input.type == decoded.type && input.code == decoded.code
           && input.count == decoded.count ? "True" : "False");
    printf("short=%s\n", decode(wire, sizeof wire - 1, &decoded) ? "ACCEPT" : "REJECT");
    return 0;
}
