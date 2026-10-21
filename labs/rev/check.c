#include <stdio.h>
#include <string.h>
int check(const char *text) {
    return strlen(text) == 7 && strcmp(text, "BIFROST") == 0;
}
int main(int argc, char **argv) {
    if (argc != 2) { puts("usage: check WORD"); return 2; }
    puts(check(argv[1]) ? "match" : "no match");
    return 0;
}
