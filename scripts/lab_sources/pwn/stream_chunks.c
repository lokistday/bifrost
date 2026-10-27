/* Deterministic short-read/write adapters; not sockets or an OS scheduler. */
#include <stdio.h>
#include <string.h>

struct reader { const unsigned char *data; size_t size, offset, chunk, calls; };
struct writer { unsigned char data[32]; size_t used, chunk, calls; int stalled; };

static size_t read_some(struct reader *r, unsigned char *out, size_t wanted) {
    ++r->calls;
    size_t count = r->size - r->offset;
    if (count > wanted) count = wanted;
    if (count > r->chunk) count = r->chunk;
    memcpy(out, r->data + r->offset, count);
    r->offset += count;
    return count;
}

static int read_exact(struct reader *r, unsigned char *out, size_t wanted) {
    size_t used = 0;
    while (used < wanted) {
        size_t count = read_some(r, out + used, wanted - used);
        if (count == 0) return 0;
        used += count;
    }
    return 1;
}

static int frame(struct reader *r, char out[17]) {
    unsigned char header[2], body[16];
    if (!read_exact(r, header, 2)) return 0;
    size_t size = ((size_t)header[0] << 8) | header[1];
    if (size > sizeof body || !read_exact(r, body, size)) return 0;
    memcpy(out, body, size);
    out[size] = '\0';
    return 1;
}

static size_t write_some(struct writer *w, const unsigned char *data, size_t wanted) {
    ++w->calls;
    if (w->stalled) return 0;
    size_t count = wanted < w->chunk ? wanted : w->chunk;
    if (count > sizeof w->data - w->used) return 0;
    memcpy(w->data + w->used, data, count);
    w->used += count;
    return count;
}

static int write_all(struct writer *w, const unsigned char *data, size_t size) {
    size_t used = 0;
    while (used < size) {
        size_t count = write_some(w, data + used, size - used);
        if (count == 0) return 0;
        used += count;
    }
    return 1;
}

int main(void) {
    const unsigned char input[] = {0, 5, 'B', 'I', 'F', 'R', 'O'};
    struct reader full = {input, sizeof input, 0, 2, 0};
    struct reader short_body = {input, 5, 0, 2, 0};
    char payload[17];
    int complete = frame(&full, payload);
    printf("complete=%s payload=%s reads=%zu\n", complete ? "OK" : "REJECT", complete ? payload : "-", full.calls);
    int truncated = frame(&short_body, payload);
    printf("truncated=%s reads=%zu\n", truncated ? "ACCEPT" : "REJECT", short_body.calls);
    struct writer writer = {{0}, 0, 2, 0, 0};
    if (!write_all(&writer, input, sizeof input)) return 2;
    printf("written=%zu calls=%zu\n", writer.used, writer.calls);
    struct writer stalled = {{0}, 0, 2, 0, 1};
    printf("stalled=%s\n", write_all(&stalled, input, sizeof input) ? "ACCEPT" : "REJECT");
    return 0;
}
