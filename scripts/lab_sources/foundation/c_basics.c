#include <stddef.h>
#include <stdio.h>
#include <string.h>

static int sum_values(const int *items, size_t count) {
    int total = 0;
    for (size_t i = 0; i < count; ++i) {
        total += items[i];
    }
    return total;
}

int main(void) {
    int values[] = {2, 5, 8};
    char label[] = "LAB";
    size_t count = sizeof values / sizeof values[0];
    printf("count=%zu first=%d sum=%d\n", count, values[0], sum_values(values, count));
    printf("capacity=%zu text_length=%zu terminator=%d\n", sizeof label, strlen(label), (int)label[3]);
    return 0;
}
