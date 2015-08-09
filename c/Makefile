all: libalib.a

libalib.a: output.o parsing.o bytes.o Makefile
	ar rcs libalib.a output.o parsing.o bytes.o

output.o: output.c
	gcc -c output.c -o output.o

parsing.o: parsing.c
	gcc -c parsing.c -o parsing.o

bytes.o: bytes.c
	gcc -c bytes.c -o bytes.o

clean:
	rm *.o *.a

