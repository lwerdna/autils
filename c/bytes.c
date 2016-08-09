#include <stdio.h>
#include <stdint.h>
#include <string.h>

/******************************************************************************
 PARSE/PRINT
******************************************************************************/
int 
parse_nib(char *str, unsigned char *val)
{
    int rc = -1;
    char c = *str;

    if(c>='0' && c<='9') {
        *val = c-'0';
        rc = 0;
    }
    else if(c>='a' && c<='f') {
        *val = 10 + (c-'a');
        rc = 0;
    }
    else if(c>='A' && c<='F') {
        *val = 10 + (c-'A');
        rc = 0;
    }
    else {
        printf("ERROR: %s('%c', ...)\n", __func__, c);
    }

    return rc;
}

/* will parse 1 or 2 characters from its input 
    ... 0 characters results in error
    ... > 2 characters results in parsing of just the first two */
int 
parse_value_hex(char *str, int limit, uint64_t *result)
{
    int i, rc = -1;
    uint64_t value;

    /* discards optional "0x" prefix */
    if(str[0]=='0' && (str[1]=='x' || str[1]=='X')) {
        str += 2;
    }

    /* empty string is error */
    if(!(*str))
        goto cleanup;

    /* loop over nibbles */
    for(value=0, i=0; str[i] && i<limit; ++i) { 
        unsigned char nib;

        if(parse_nib(str+i, &nib)) {
            goto cleanup;
        }

        value = (value<<4) + nib;
    }

    /* made it this far? success */
    *result = value;
    rc = 0;

    /* done */
    cleanup:

    if(rc) {
        printf("ERROR: %s(\"%s\", ...)\n", __func__, str);
    }

    return rc;
}

int 
parse_uint8_hex(char *str, uint8_t *result)
{
    int rc=-1;
    uint64_t value;

    if(parse_value_hex(str, 2, &value)) {
        printf("ERROR: %s(\"%s\", ...)\n", __func__, str);
        goto cleanup;
    }

    rc = 0;
    *result = value & 0xFF;

    cleanup:
    return rc;
}

int 
parse_uint16_hex(char *str, uint16_t *result)
{
    int rc=-1;
    uint64_t value;

    if(parse_value_hex(str, 4, &value)) {
        printf("ERROR: %s(\"%s\", ...)\n", __func__, str);
        goto cleanup;
    }

    rc = 0;
    *result = value & 0xFFFF;

    cleanup:
    return rc;
}

int 
parse_uint32_hex(char *str, uint32_t *result)
{
    int rc=-1;
    uint64_t value;

    if(parse_value_hex(str, 8, &value)) {
        printf("ERROR: %s(\"%s\", ...)\n", __func__, str);
        goto cleanup;
    }

    rc = 0;
    *result = value & 0xFFFFFFFF;

    cleanup:
    return rc;
}

int 
parse_uint64_hex(char *str, uint64_t *result)
{
    int rc=-1;
    uint64_t value;

    if(parse_value_hex(str, 16, &value)) {
        printf("ERROR: %s(\"%s\", ...)\n", __func__, str);
        goto cleanup;
    }

    rc = 0;
    *result = value;

    cleanup:
    return rc;
}

int
parse_uintptr_hex(char *str, uintptr_t *result)
{
    int rc=-1;
    uint64_t value;

    // strategy: parse a 64-bit type, cast it down to the the intptr_t
    // ..provided that uint64_t envelopes uintptr_t
    #if UINT64_MAX > UINTPTR_MAX
    #pragma ERROR "not prepared for pointers larger than 64 bits"
    #endif

    if(parse_value_hex(str, 32, &value)) {
        printf("ERROR: %s(\"%s\", ...)\n", __func__, str);
        goto cleanup;
    }

    rc = 0;
    *result = (uintptr_t)value;

    cleanup:
    return rc;
}
