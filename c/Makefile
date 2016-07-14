all: libautils.a

libautils.a: output.o parsing.o bytes.o subprocess.o Makefile
	ar rcs libautils.a output.o parsing.o bytes.o subprocess.o

output.o: output.c
	gcc -c output.c -o output.o

parsing.o: parsing.c
	gcc -c parsing.c -o parsing.o

bytes.o: bytes.c
	gcc -c bytes.c -o bytes.o

subprocess.o: subprocess.c
	gcc -c subprocess.c -o subprocess.o

install:
	install -d /usr/local/include/autils
	install -m 644 ./bytes.h /usr/local/include/autils
	install -m 644 ./output.h /usr/local/include/autils
	install -m 644 ./parsing.h /usr/local/include/autils
	install -m 644 ./subprocess.h /usr/local/include/autils
	install ./libautils.a /usr/local/lib

clean:
	rm *.o *.a

