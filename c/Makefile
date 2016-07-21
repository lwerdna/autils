all: libautils.a

libautils.a: output.o parsing.o bytes.o subprocess.o filesys.o crc.o base64.o Makefile
	ar rcs libautils.a output.o parsing.o bytes.o subprocess.o filesys.o crc.o base64.o

output.o: output.c
	gcc -c output.c -o output.o

parsing.o: parsing.c
	gcc -c parsing.c -o parsing.o

bytes.o: bytes.c
	gcc -c bytes.c -o bytes.o

subprocess.o: subprocess.c
	gcc -c subprocess.c -o subprocess.o

filesys.o: filesys.c
	gcc -c filesys.c -o filesys.o

crc.o: crc.c
	gcc -c crc.c -o crc.o

base64.o: base64.c
	gcc -c base64.c -o base64.o

install:
	install -d /usr/local/include/autils
	install -m 644 ./*.h /usr/local/include/autils
	install ./libautils.a /usr/local/lib

clean:
	rm *.o *.a

