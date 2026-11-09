#include <stdio.h>
#include <string.h>

static int gate(const char *s) {
    if (strlen(s) != 4) return 0;
    if (s[0] != 'K' || s[3] != '7') return 0;
    return (unsigned char)s[1] + (unsigned char)s[2] == 150;
}
int main(int argc, char **argv) {
    if (argc != 2) {
        fputs("usage: mystery ASCII_TEXT\n", stderr);
        return 2;
    }
    puts(gate(argv[1]) ? "accept" : "reject");
    return 0;
}
