#include <stdio.h>
#include <string.h>
int main(int argc, char **argv) {
    int state=0, accepted=0;
    for (int i=1; i<argc; ++i) {
        if (!strcmp(argv[i], "login") && !state) { state=1; ++accepted; }
        else if (!strcmp(argv[i], "read") && state) ++accepted;
        else if (!strcmp(argv[i], "logout") && state) { state=0; ++accepted; }
        printf("state=%d\n", state);
    }
    printf("accepted=%d\n", accepted);
    return 0;
}
