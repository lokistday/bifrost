#include <stdio.h>
#include <stdlib.h>
int main(void) {
    int local = 7;
    int values[3] = {10, 20, 30};
    int *heap = malloc(sizeof *heap);
    if (!heap) return 1;
    *heap = 9;
    printf("local=%d heap=%d\n", local, *heap);
    for (size_t i = 0; i < sizeof values / sizeof values[0]; ++i)
        printf("%d%s", values[i], i == 2 ? "\n" : " ");
    free(heap);
    heap = NULL;
    return 0;
}
