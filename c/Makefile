CPPFLAGS += -std=c++11

#--<BOILERPLATE_START>---------------------------------------------------------
# OS DETECTION -> set compiler, define variable for source files to know
UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Darwin)
    $(info ******** compiling for MACOS! ********)
    CC = clang
    CPP = clang++
    CFLAGS += -D OS_IS_MACOS
endif
ifeq ($(UNAME_S),Linux)
    $(info ******** compiling for LINUX! ********)
    CC = gcc
    CPP = g++
    CFLAGS += -D OS_IS_LINUX
endif
ifeq ($(UNAME_S),FreeBSD)
    $(info ******** compiling for FreeBSD! ********)
    CC = cc
    CFLAGS += -D OS_IS_FREEBSD
endif
ifeq (CC,"")
    $(error unable to detect OS!)
endif

# release will be empty unless supplied on make command line
RELEASE ?=
ifeq ($(RELEASE),)
$(info MAKEFILE DEBUG MODE, PRINTS PRESENT)
CFLAGS += -g -O0 -DDEBUG=1
CPPFLAGS += -g -O0 -DDEBUG=1
else
$(info MAKEFILE RELEASE MODE)
endif
#--<BOILERPLATE_END>-----------------------------------------------------------

all: libautils.a test

OBJ_FILES = base64.o bytes.o crc.o debug.o filesys.o output.o parsing.o subprocess.o md5.o
OBJ_FILES += filesys_cpp.o misc_cpp.o

all: $(OBJ_FILES) libautils.a test

# RECIPES for objects
# objects pattern rule, eg:
# foo.o: foo.c foo.h
#     $(CC) $(CFLAGS) -c foo.c
%.o: %.c %.h
	$(CC) $(CFLAGS) -c $<

%_cpp.o: %.cpp %.hpp
	$(CPP) $(CPPFLAGS) -c $< -o $@

# RECIPE for library
libautils.a: $(OBJ_FILES)
	if [ -a libautils.a ]; \
		then \
	rm libautils.a; \
	fi;
	ar -r libautils.a $(OBJ_FILES)

test: test.cpp libautils.a
	$(CPP) $(CPPFLAGS) test.cpp libautils.a -o test

install:
	install -d /usr/local/include/autils
	install -m 644 ./*.h /usr/local/include/autils
	install -m 644 ./*.hpp /usr/local/include/autils
	install ./libautils.a /usr/local/lib

clean:
	rm *.o *.a test
	rm -rf test.dSYM
