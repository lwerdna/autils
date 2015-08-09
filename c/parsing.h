int parse_byte_list(char **str_bytes, int n_bytes, uint8_t *result);
int parse_addr_range(int ac, char **av, uintptr_t *addr, unsigned int *len);

int parse_bytelist(int ac, char **av, uint8_t *bytes);

int parse_addr_range_bytelist(int ac, char **av, uintptr_t *addr, uint32_t *len, uint8_t *bytes);

int parse_addr_bytelist(int ac, char **av, uintptr_t *addr, uint8_t *bytes);

int parse_values_array_hex(char **strings, uint32_t len, uint8_t *data, uint32_t *len_data);

int parse_mac(char *mac, unsigned char *bytes);
