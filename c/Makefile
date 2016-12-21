FLAGS_DEBUG = -g -O0
CPPFLAGS += -g -O0 -std=c++11

all: libautils.a test

libautils.a: output.o parsing.o bytes.o subprocess.o filesys.o crc.o base64.o Makefile
	ar rcs libautils.a output.o parsing.o bytes.o subprocess.o filesys.o crc.o base64.o

output.o: output.c
	gcc $(CFLAGS) -c output.c -o output.o

parsing.o: parsing.c
	gcc $(CFLAGS) -c parsing.c -o parsing.o

bytes.o: bytes.c
	gcc $(CFLAGS) -c bytes.c -o bytes.o

subprocess.o: subprocess.c
	gcc $(CFLAGS) -c subprocess.c -o subprocess.o

filesys.o: filesys.c
	gcc $(CFLAGS) -c filesys.c -o filesys.o

crc.o: crc.c
	gcc $(CFLAGS) -c crc.c -o crc.o

base64.o: base64.c
	gcc $(CFLAGS) -c base64.c -o base64.o

test: test.cpp
	g++ $(CPPFLAGS) subprocess.o test.cpp -o test

install:
	install -d /usr/local/include/autils
	install -m 644 ./*.h /usr/local/include/autils
	install ./libautils.a /usr/local/lib

clean:
	rm *.o *.a test

