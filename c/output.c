#include <stdio.h>
#include <stdint.h>
#include <inttypes.h>

void dump_mem(void *buf_, int len, uintptr_t addr, int chunk)
{
	uint8_t *buf = buf_;
	int i, cursor=0;
	char ascii[17];

	//printf("dumping at 0x%08X (len:0%X)\n", buf, len);

	for(cursor=0; cursor<len; cursor+=16) {
		int chunks_this_line, spaces_this_line;
		int bytes_remaining = len - cursor;
		int bytes_this_line = 16;

		if(bytes_remaining < 16)
			bytes_this_line = bytes_remaining/chunk * chunk;

		chunks_this_line = bytes_this_line/chunk;
		spaces_this_line = (16-bytes_this_line)/chunk;

		/* write address */
		printf("%08" PRIxPTR ": ", addr + cursor);

		/* write the chunks, eg: 41 or 4141 or 41414141 or 4141414141414141 */
		for(i=0; i<chunks_this_line; ++i) {
			switch(chunk) {
				case 1:
					printf("%02X ", buf[cursor+i]);
					break;
				case 2:
					printf("%04X ", *(uint16_t *)(buf+cursor+2*i));
					break;
				case 4:
					printf("%08"PRIx32" ", *(uint32_t *)(buf+cursor+4*i));
					break;
				case 8:
					printf("%016"PRIx64" ", *(uint64_t *)(buf+cursor+8*i));
					break;
			}
		}

		/* write the spaces, eg: "   " or "     " or ... */
		for(i=0; i<spaces_this_line; ++i) {
			switch(chunk) {
				case 1:
					printf("   "); break;
				case 2:
					printf("     "); break;
				case 4:
					printf("         "); break;
				case 8:
					printf("                 "); break;
			}
		}

		/* write the ascii */
		for(i=0; i<16; ++i) {
			uint8_t b = buf[cursor+i];

			if(i >= bytes_this_line) {
				ascii[i] = ' ';
				continue;
			}

			if(b>=' ' && b<'~')
				ascii[i] = b;
			else
				ascii[i] = '.';
		}

		ascii[16] = '\0';
		printf(" %s\n", ascii);
	}
}

void dump_u8(void *buf, int len, uintptr_t addr)
{
	dump_mem(buf, len, addr, 1);
}

void dump_u16(void *buf, int len, uintptr_t addr)
{
	dump_mem(buf, len, addr, 2);
}

void dump_u32(void *buf, int len, uintptr_t addr)
{
	dump_mem(buf, len, addr, 4);
}

void dump_u64(void *buf, int len, uintptr_t addr)
{
	dump_mem(buf, len, addr, 8);
}
