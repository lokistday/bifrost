#define _POSIX_C_SOURCE 200809L
/* Linux/WSL, private mkdtemp directory and single-component names only. */
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

static int open_regular(int directory, const char *name) {
    if (!name || !*name || strchr(name, '/') || strcmp(name, ".") == 0 || strcmp(name, "..") == 0) {
        errno = EINVAL;
        return -1;
    }
    int fd = openat(directory, name, O_RDONLY | O_NOFOLLOW | O_CLOEXEC | O_NONBLOCK);
    if (fd < 0) return -1;
    struct stat info;
    if (fstat(fd, &info) != 0 || !S_ISREG(info.st_mode)) {
        close(fd);
        errno = EINVAL;
        return -1;
    }
    return fd;
}

int main(void) {
    char path[] = "/tmp/bifrost-open-XXXXXX";
    if (!mkdtemp(path)) { perror("mkdtemp"); return 2; }
    int directory = open(path, O_RDONLY | O_DIRECTORY | O_CLOEXEC);
    int created = -1, reader = -1;
    int status = 2;
    if (directory < 0) goto cleanup;
    created = openat(directory, "note.txt", O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC, 0600);
    if (created < 0) goto cleanup;
    if (close(created) != 0) { created = -1; goto cleanup; }
    created = -1;
    reader = open_regular(directory, "note.txt");
    if (reader < 0) goto cleanup;
    puts("regular=ACCEPT");
    int again = openat(directory, "note.txt", O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC, 0600);
    if (again >= 0) { close(again); goto cleanup; }
    if (errno != EEXIST) goto cleanup;
    puts("second_create=EXISTS");
    if (symlinkat("note.txt", directory, "alias.txt") != 0) goto cleanup;
    int alias = open_regular(directory, "alias.txt");
    if (alias >= 0) { close(alias); goto cleanup; }
    puts("symlink=REJECT");
    if (unlinkat(directory, "note.txt", 0) != 0) goto cleanup;
    struct stat info;
    if (fstat(reader, &info) != 0 || !S_ISREG(info.st_mode)) goto cleanup;
    puts("opened_object=STILL_REGULAR");
    status = 0;
cleanup:
    if (created >= 0) close(created);
    if (reader >= 0) close(reader);
    if (directory >= 0) {
        unlinkat(directory, "alias.txt", 0);
        unlinkat(directory, "note.txt", 0);
        close(directory);
    }
    if (rmdir(path) != 0) status = 2;
    if (status) fputs("file-boundary exercise failed\n", stderr);
    return status;
}
