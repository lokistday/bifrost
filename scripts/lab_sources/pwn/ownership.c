/* The result is owned by the caller; the temporary alias is only borrowed. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static char *make_note(const char *text) {
    size_t length = strlen(text);
    char *result = malloc(length + 1);
    if (!result) return NULL;
    memcpy(result, text, length + 1);
    return result;
}

static void show_note(const char *borrowed) {
    printf("borrowed=%s\n", borrowed);
}

int main(void) {
    char *owner = make_note("Bifrost");
    if (!owner) { puts("ALLOCATION_FAILED"); return 2; }
    show_note(owner);
    free(owner);
    owner = NULL;
    printf("owner_is_null=%s\n", owner == NULL ? "yes" : "no");
    return 0;
}
