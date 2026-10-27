/* Keep the format literal. Observe snprintf's required length and termination. */
#include <stdio.h>

int main(int argc, char **argv) {
    const char *text = argc > 1 ? argv[1] : "%s%n";
    char message[8];
    int needed = snprintf(message, sizeof message, "[%s]", text);
    if (needed < 0) { puts("FORMAT_ERROR"); return 2; }
    printf("literal=%s\n", text);
    printf("required=%d capacity=%zu truncated=%s\n", needed, sizeof message,
           (size_t)needed >= sizeof message ? "yes" : "no");
    printf("stored=%s\n", message);
    return 0;
}
