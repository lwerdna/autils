#if defined (__cplusplus)
extern "C" {
#endif

void debug(char *fmt, ...);
void debug_err(char *fmt, ...);
void debug_dump_bytes(const unsigned char *buf, int len, unsigned int addr);
int debug_defined();

#define ERR_CLEANUP(...) { debug_err(__VA_ARGS__); debug("\n"); goto cleanup; }

#if defined (__cplusplus)
}
#endif
