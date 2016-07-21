#include <stdio.h>
#include <stdarg.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>

void
base64_encode(unsigned char *data, int len, char *out)
{
    char *lookup = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
    int mod_table[] = {0, 2, 1};
    int out_len = 4 * ((len + 2) / 3);
    int i, j;

    for(i=0, j=0; i<len;) {
        uint32_t octet_a = i < len ? (unsigned char)data[i++] : 0;
        uint32_t octet_b = i < len ? (unsigned char)data[i++] : 0;
        uint32_t octet_c = i < len ? (unsigned char)data[i++] : 0;

        uint32_t triple = (octet_a << 0x10) + (octet_b << 0x08) + octet_c;

        out[j++] = lookup[(triple >> 3 * 6) & 0x3F];
        out[j++] = lookup[(triple >> 2 * 6) & 0x3F];
        out[j++] = lookup[(triple >> 1 * 6) & 0x3F];
        out[j++] = lookup[(triple >> 0 * 6) & 0x3F];
    }

    for(i=0; i<mod_table[len % 3]; i++)
        out[out_len - 1 - i] = '=';

    out[out_len] = '\0';
}

/* from Jouni Malinen */
unsigned char *
base64_decode(const unsigned char *src, size_t len)
{
	unsigned char dtable[256], *out, *pos, in[4], block[4], tmp;
	size_t i, count, olen;

	const unsigned char base64_table[64] =
		"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

	memset(dtable, 0x80, 256);
	for (i = 0; i < sizeof(base64_table); i++)
		dtable[base64_table[i]] = i;
	dtable['='] = 0;

	count = 0;
	for (i = 0; i < len; i++) {
		if (dtable[src[i]] != 0x80)
			count++;
	}

	if (count % 4)
		return NULL;

	olen = count / 4 * 3;
	pos = out = malloc(count);
	if (out == NULL)
		return NULL;

	count = 0;
	for (i = 0; i < len; i++) {
		tmp = dtable[src[i]];
		if (tmp == 0x80)
			continue;

		in[count] = src[i];
		block[count] = tmp;
		count++;
		if (count == 4) {
			*pos++ = (block[0] << 2) | (block[1] >> 4);
			*pos++ = (block[1] << 4) | (block[2] >> 2);
			*pos++ = (block[2] << 6) | block[3];
			count = 0;
		}
	}

	if (pos > out) {
		if (in[2] == '=')
			pos -= 2;
		else if (in[3] == '=')
			pos--;
	}

	return out;
}
