
uint16_t bswap16(uint16_t x);
uint32_t bswap32(uint32_t x);
uint64_t bswap64(uint64_t x);
uint16_t fetch16(uint8_t *data, bool swap);
uint32_t fetch32(uint8_t *data, bool swap);
uint64_t fetch64(uint8_t *data, bool swap);
void set16(uint8_t *addr, uint32_t val, bool swap);
void set32(uint8_t *addr, uint32_t val, bool swap);
void set64(uint8_t *addr, uint64_t val, bool swap);

int parse_uint8_hex(const char *str, uint8_t *result);
int parse_uint16_hex(const char *str, uint16_t *result);
int parse_uint32_hex(const char *str, uint32_t *result);
int parse_uint64_hex(const char *str, uint64_t *result);
int parse_uintptr_hex(const char *str, uintptr_t * result);


