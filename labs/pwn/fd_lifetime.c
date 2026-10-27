#define _POSIX_C_SOURCE 200809L
/* dup shares one open-file description and offset, not a separate file copy. */
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

static int write_all(int fd, const char *data, size_t size) {
    size_t used = 0;
    while (used < size) {
        ssize_t count = write(fd, data + used, size - used);
        if (count < 0 && errno == EINTR) continue;
        if (count <= 0) return 0;
        used += (size_t)count;
    }
    return 1;
}

static int read_pair(int fd, char out[3]) {
    size_t used = 0;
    while (used < 2) {
        ssize_t count = read(fd, out + used, 2 - used);
        if (count < 0 && errno == EINTR) continue;
        if (count <= 0) return 0;
        used += (size_t)count;
    }
    out[2] = '\0';
    return 1;
}

int main(void) {
    char path[] = "/tmp/bifrost-fd-XXXXXX";
    int fd = mkstemp(path), duplicate = -1;
    char pair[3];
    if (fd < 0) { perror("mkstemp"); return 2; }
    if (unlink(path) != 0 || !write_all(fd, "ABCDEF", 6) || lseek(fd, 0, SEEK_SET) < 0) goto fail;
    duplicate = dup(fd);
    if (duplicate < 0 || !read_pair(fd, pair)) goto fail;
    printf("first=%s\n", pair);
    if (!read_pair(duplicate, pair)) goto fail;
    printf("via_dup=%s\n", pair);
    if (close(fd) != 0) { fd = -1; goto fail; }
    fd = -1;
    if (!read_pair(duplicate, pair)) goto fail;
    printf("after_close=%s\n", pair);
    char extra;
    ssize_t result;
    do { result = read(duplicate, &extra, 1); } while (result < 0 && errno == EINTR);
    if (result != 0) goto fail;
    puts("last_read=EOF");
    if (close(duplicate) != 0) return 2;
    return 0;
fail:
    perror("descriptor exercise");
    if (fd >= 0) close(fd);
    if (duplicate >= 0) close(duplicate);
    unlink(path);
    return 2;
}
