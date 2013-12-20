/*****************************************************************************/
/* piece representation */
/*****************************************************************************/

/* piece identifiers */
#define PC_ID_MASK 0x7
#define PC_ID_SHR 0
#define PC_ID_GET(x) (((x) & PC_ID_MASK) >> PC_ID_SHR)
#define PC_ID_P 0
#define PC_ID_N 1
#define PC_ID_B 2
#define PC_ID_R 3
#define PC_ID_Q 4
#define PC_ID_K 5

/* piece colors */
#define PC_COL_MASK 0x8
#define PC_COL_SHR 3
#define PC_COL_GET(x) (((x) & PC_COL_MASK) >> PC_COL_SHR)
#define PC_COL_WHITE 0
#define PC_COL_BLACK 1

/* piece values */
#define PC_VAL_MASK 0xF0
#define PC_VAL_SHR 4
#define PC_VAL_GET(x) (((x) & PC_VAL_MASK) >> PC_VAL_SHR)

/* pieces combinations */
#define PC_MAKE(id, col, val) \
    (id << PC_ID_SHR) | (col << PC_COL_SHR) | (val << PC_VAL_SHR)

#define PC_W_P PC_MASK(PC_ID_P, PC_COL_WHITE, 1)
#define PC_W_N PC_MASK(PC_ID_N, PC_COL_WHITE, 3)
#define PC_W_B PC_MASK(PC_ID_B, PC_COL_WHITE, 3)
#define PC_W_R PC_MASK(PC_ID_R, PC_COL_WHITE, 5)
#define PC_W_Q PC_MASK(PC_ID_Q, PC_COL_WHITE, 9)
#define PC_W_K PC_MASK(PC_ID_K, PC_COL_WHITE, -1)
#define PC_B_P PC_MASK(PC_ID_P, PC_COL_BLACK, 1)
#define PC_B_N PC_MASK(PC_ID_N, PC_COL_BLACK, 3)
#define PC_B_B PC_MASK(PC_ID_B, PC_COL_BLACK, 3)
#define PC_B_R PC_MASK(PC_ID_R, PC_COL_BLACK, 5)
#define PC_B_Q PC_MASK(PC_ID_Q, PC_COL_BLACK, 9)
#define PC_B_K PC_MASK(PC_ID_K, PC_COL_BLACK, -1)

/*****************************************************************************/
/* board representation: 0x88 */
/*****************************************************************************/

/*
looks like this, with a8 in top left:

00 01 02 03 04 05 06 07 | 08 09 0A 0B 0C 0D 0E 0F
10 11 12 13 14 15 16 17 | 18 19 1A 1B 1C 1D 1E 1F
20 21 22 23 24 25 26 27 | 28 29 2A 2B 2C 2D 2E 2F
30 31 32 33 34 35 36 37 | 38 39 3A 3B 3C 3D 3E 3F
40 41 42 43 44 45 46 47 | 48 49 4A 4B 4C 4D 4E 4F
50 51 52 53 54 55 56 57 | 58 59 5A 5B 5C 5D 5E 5F
60 61 62 63 64 65 66 67 | 68 69 6A 6B 6C 6D 6E 6F
70 71 72 73 74 75 76 77 | 78 79 7A 7B 7C 7D 7E 7F

> rank rrr and file rrr are stored as binary 0rrr0fff
> get squares on same rank with +1, +2, ...
> get squares on same file with +16, +32, ...

b3 (value 0x08) is toggled depending on if in imaginary board
b7 (value 0x80) to test if >0x7F (off board)

so sqrnum & 0x88 suffices to test if on board

*/

#define SQR_RANK_MASK 0x70
#define SQR_RANK_SHIFT 4
#define SQR_RANK_GET(x) (((x) & SQR_RANK_MASK) >> SQR_RANK_SHIFT)
#define SQR_RANK_CMP(x,y) (((x) & SQR_RANK_MASK) == ((y) & SQR_RANK_MASK))

#define SQR_FILE_MASK 0x07
#define SQR_FILE_SHIFT 0
#define SQR_FILE_GET(x) (((x) & SQR_FILE_MASK) >> SQR_FILE_SHIFT)
#define SQR_FILE_CMP(x,y) (((x) & SQR_FILE_MASK) == ((y) & SQR_FILE_MASK))

typedef uint8_t board88[128];

board88 init_board = { \
    PC_B_R, PC_B_N, PC_B_B, PC_B_Q, PC_B_K, PC_B_B, PC_B_N, PC_B_R, 0,0,0,0,0,0,0,0,
    PC_B_P, PC_B_P, PC_B_P, PC_B_P, PC_B_P, PC_B_P, PC_B_P, PC_B_P, 0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    PC_W_P, PC_W_P, PC_W_P, PC_W_P, PC_W_P, PC_W_P, PC_W_P, PC_W_P, 0,0,0,0,0,0,0,0,
    PC_W_R, PC_W_N, PC_W_B, PC_W_Q, PC_W_K, PC_W_B, PC_W_N, PC_W_R, 0,0,0,0,0,0,0,0
};

