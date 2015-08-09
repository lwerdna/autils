#build, targetting your host machine
-just run make with gcc/ld/ar in path

#build, targetting android
-download the NDK, setup CCOMPILER and NDK_SYSROOT variable, example:
```
a@ubuntu:~/code/alib/c$ echo $CCOMPILER
/home/a/android-ndk-r10e/toolchains/arm-linux-androideabi-4.9/prebuilt/linux-x86_64/bin/arm-linux-androideabi-
a@ubuntu:~/code/alib/c$ echo $NDK_SYSROOT
/home/a/android-ndk-r10e/platforms/android-19/arch-arm
```
-make -f Makefile-ndk

#build, targetting something else
-define CCOMPILER and adapt the Makefile-ndk to supply your compiler with appropriate sysroot

