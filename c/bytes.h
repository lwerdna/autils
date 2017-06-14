void print_hexdump(unsigned char *buf, int len, unsigned int addr);

int parse_uint8_hex(const char *str, uint8_t *result);
int parse_uint16_hex(const char *str, uint16_t *result);
int parse_uint32_hex(const char *str, uint32_t *result);
int parse_uint64_hex(const char *str, uint64_t *result);
int parse_uintptr_hex(const char *str, uintptr_t * result);


