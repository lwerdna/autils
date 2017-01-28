#include <stdint.h>

uint32_t crc32(uint32_t crc, const void *buf, size_t size);
int crc32_file(char *fpath, uint32_t *result);

