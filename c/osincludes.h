/* OS-sensitive includes, so that individual LibTC modules don't have to
    conditionally include stuff */

// remember you can access all preprocessor macros:
// for clang: `clang -dM -E - < /dev/null`
// for   gcc: `echo "" | cpp -dD`


/* include guard */
#ifndef OSINCLUDES_H
#define OSINCLUDES_H

#if defined(IN_PORT_T)
#define in_port_t __be16
#endif

#if defined(OS_IS_LINUX) || defined(OS_IS_MACOS) || defined(OS_IS_FREEBSD) || defined(OS_IS_ANDROID)
//#pragma message "including common headers for Linux/Mac/FreeBSD/Android"
#include <unistd.h>
#include <signal.h> // kill()
#include <errno.h>
#include <netdb.h>
#include <stdio.h> // for STDIN_FILENO, etc.
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/wait.h> // for wait(), waitpid()
#include <arpa/inet.h>
#include <netinet/in.h>
#include <netinet/ip.h>


#elif defined(OS_IS_WINDOWS)
//#pragma message "including common headers for Windows"

// without this, windows.h includes winsock.h, colliding with stuff in winsock2.h
#define _WINSOCKAPI_
#include <windows.h>
#include <winsock2.h>
#else
#pragma message("must define OS_IS_LINUX, OS_IS_MAC, OS_IS_FREEBSD or OS_IS_WINDOWS")
#endif

#if defined(OS_IS_FREEBSD)
#include <sys/param.h>
#include <sys/module.h>
#endif

#endif /* OSINCLUDES_H */
