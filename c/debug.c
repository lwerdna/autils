#include <stdio.h>
#include <stdarg.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>

#include "osincludes.h"
#include "output.h"

void debug(char *fmt, ...) 
{
    va_list args;
    va_start(args, fmt);
    #ifdef DEBUG
    vprintf(fmt, args);
    #endif
    va_end(args);
}

void debug_err(char *fmt, ...) 
{
    va_list args;
    va_start(args, fmt);
    #ifdef DEBUG
    printf("ERROR: ");
    vprintf(fmt, args);
    printf("\n");
    #ifdef OS_IS_WINDOWS
    printf("GetLastError(): 0x%08X\n", GetLastError());
    #endif
    perror("perror():");
    #endif
    va_end(args);
}

void debug_dump_u8(uint8_t *buf, int len, unsigned int addr)
{
	#ifdef DEBUG
	dump_u8(buf, len, addr);
	#endif
}

int debug_defined()
{
	#ifdef DEBUG
	return 1;
	#else
	return 0;
	#endif
}

