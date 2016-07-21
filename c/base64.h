#define B64_MAX(N) ((N+2)/3)*4+1

void
base64_encode(unsigned char *data, int len, char *out);
unsigned char *
base64_decode(const unsigned char *src, size_t len);
