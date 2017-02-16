#include <stdio.h>
#include <string.h>

#include <unistd.h> // pid_t
#include <signal.h>
#include <sys/wait.h> // waitpid

#include <string>
#include <vector>
using namespace std;

extern "C"
{
#include "filesys.h"
#include "subprocess.h"
#include "crc.h"
#include "md5.h"
}
#include "filesys.hpp"
#include "misc.hpp"

int main(int ac, char **av)
{
	int rc = -1;

	if(ac <= 1) {
		printf("eg: %s subprocess\n", av[0]);
		goto cleanup;
	}

	/*************************************************************************/
	/* test misc */
	/*************************************************************************/
	if(!strcmp(av[1], "misc")) {
		string ver;
		misc_get_py_ver(ver);
		printf("python version: %s\n", ver.c_str());
	}

	/*************************************************************************/
	/* test filesys */
	/*************************************************************************/
	if(!strcmp(av[1], "filesys")) {
		vector<string> results;
		string cwd;
		filesys_cwd(cwd);

		printf("listing all %s/*\n", cwd.c_str());
		printf("------------------------------------\n");
		if(filesys_ls(AUTILS_FILESYS_LS_ANY, "", cwd, results)) {
			printf("ERROR: ls()\n");
			goto cleanup;
		}
		for(auto i=results.begin(); i!=results.end(); ++i)
			printf("%s\n", i->c_str());

		printf("\nlisting all %s/*.c:\n", cwd.c_str());
		printf("------------------------------------\n");
		results.clear();
		if(filesys_ls(AUTILS_FILESYS_LS_EXT, ".c", cwd, results, true)) {
			printf("ERROR: ls()\n");
			goto cleanup;
		}
		for(auto i=results.begin(); i!=results.end(); ++i) {
			string basename;
			filesys_basename(*i, basename);
			printf("%s (basename: %s)\n", i->c_str(), basename.c_str());
		}

		printf("\nlisting all %s/*.cpp:\n", cwd.c_str());
		printf("------------------------------------\n");
		results.clear();
		if(filesys_ls(AUTILS_FILESYS_LS_EXT, ".cpp", cwd, results)) {
			printf("ERROR: ls()\n");
			goto cleanup;
		}
		for(auto i=results.begin(); i!=results.end(); ++i)
			printf("%s\n", i->c_str());

		printf("\nlisting all %s/test*:\n", cwd.c_str());
		printf("------------------------------------\n");
		results.clear();
		if(filesys_ls(AUTILS_FILESYS_LS_STARTSWITH, "test", cwd, results)) {
			printf("ERROR: ls()\n");
			goto cleanup;
		}
		for(auto i=results.begin(); i!=results.end(); ++i) {
			string basename;
			filesys_basename(*i, basename);
			printf("%s (basename: %s)\n", i->c_str(), basename.c_str());
		}

		printf("\ncopying %s/test to %s/test_copy:\n", cwd.c_str(), cwd.c_str());
		printf("------------------------------------\n");
		results.clear();
		string err;
		if(filesys_copy("test", "test_copy", err)) {
			printf("ERROR: %s\n", err.c_str());
			goto cleanup;
		}

		printf("\n");
	}

	/*************************************************************************/
	/* test subprocess */
	/*************************************************************************/
	if(!strcmp(av[1], "subprocess")) {	
		char one[] = "python";
		char two[] = "-V";
		char *argv[3] = {one, two, NULL};

		char zone[] = "yes";
		char *zargv[2] = {zone, NULL};
		int child_stdout;

		char buf_stdout[64], buf_stderr[64];

		if(0 != launch(one, argv, &rc, buf_stdout, 64, buf_stderr, 64)) {
			printf("ERROR: launch()\n");
			goto cleanup;
		}

		printf("full launch (1/2), python version is: %s\n", buf_stderr);

		if(0 != launch(one, argv, &rc, buf_stdout, 64, buf_stderr, 64)) {
			printf("ERROR: launch()\n");
			goto cleanup;
		}
			
		printf("full launch (2/2), python version is: %s\n", buf_stderr);

		close(child_stdout);
	}

	/*************************************************************************/
	/* test subprocess (stress test!) 
		use ps, task manager, activity monitor, whatever to make sure a ton of
		yes processes aren't adding up */
	/*************************************************************************/
	if(!strcmp(av[1], "subprocess2")) {	
		char zone[] = "yes";
		char *zargv[2] = {zone, NULL};
		int child_stdout, stat;
		pid_t child_pid;

		for(int j=0; 1; ++j) {
			if(0 != launch_ex(
				zone, // "yes"
				zargv, // {"yes", NULL}
				&child_pid, // child pid (don't care)
				NULL, // child stdin (don't care)
			    &child_stdout, // child stdout
				NULL // child stderr (don't care)
			)) {
				printf("ERROR: launch_ex()\n");
				goto cleanup;
			}

			printf("reading 100 bytes from continuous output stream of \"yes\""
			  " (pid=%d)\n", child_pid);

			for(int i=0; i<100; ++i) {
				int rc;
				char buf;
				rc = read(child_stdout, &buf, 1);
				switch(rc) {
					case -1:
					printf("ERROR: read()\n"); goto cleanup;
					case 0:
					printf("ERROR: eof reaches on yes?!\n"); goto cleanup;
					case 1:
						printf("0x%02X", buf);
						if(!isspace(buf)) printf("('%c') ", buf);
						else printf(" ");
						break;
					default:
					printf("ERROR: read() returned unexpected %d\n", rc);
				}
			}
			printf("\n");
		
			close(child_stdout);

			printf("killing...\n");
			if(0 != kill(child_pid, SIGTERM)) {
				printf("ERROR: kill()\n");
				goto cleanup;
			}

			printf("waitpid...\n");	
		    if(waitpid(child_pid, &stat, 0) != child_pid) {
				printf("ERROR: waitpid()\n");
				goto cleanup;
			}
		}
	}

	/*************************************************************************/
	/* test subprocess (stress test again!) */
	/*************************************************************************/
	if(!strcmp(av[1], "subprocess3")) {	
		char one[] = "python";
		char two[] = "--help";
		char *argv[3] = {one, two, NULL};
		char buf_stdout[4], buf_stderr[4];

		for(int i=0; i<100; ++i) {
			if(0 != launch(one, argv, &rc, buf_stdout, 4, buf_stderr, 4)) {
				printf("ERROR: launch()\n");
				goto cleanup;
			}

			buf_stdout[3] = buf_stderr[3] = '\0';
			printf("launch %d: stdout=%s... stderr=%s...\n",
				i, buf_stdout, buf_stderr);
		}
	}	

	/*************************************************************************/
	/* test crc */
	/*************************************************************************/
	if(!strcmp(av[1], "crc")) {
		char test_path[] = "crc_test_input";

	    // should return 0x414FA339
    	const char *input = "The quick brown fox jumps over the lazy dog";
	    uint32_t result = crc32(0, input, strlen(input));
	    if(result == 0x414FA339) printf("PASS!\n");
		else printf("FAIL!\n");

		if(check_file_exists(test_path)) {
			uint32_t result;
			if(crc32_file(test_path, &result) != 0 ||
			  result != 0x414FA339) {
		    	printf("PASS!\n");
			}
			else printf("FAIL!\n");
		}
	}

	/*************************************************************************/
	/* test md5 */
	/*************************************************************************/
	if(!strcmp(av[1], "md5")) {
    	const char *str0 = "The quick brown fox jumps over the lazy dog";
    	const char *str1 = "The quick brown fox jumps over the lazy dog.";
    	const char *str2 = "";
    
    	char hash_str[33];
    
//    	/* hash a file specified on the command line
//    		(and compare the answer with what you get with, say `md5` or `md5sum`) */
//    	if(ac > 1) {
//    		char *fpath = av[1];
//    
//    		if(md5_file_str(fpath, hash_str)) {
//    			printf("FAIL!\n");
//    			goto cleanup;
//    		}
//    	
//    		printf("MD5 (%s) = %s\n", fpath, hash_str);
//    	}
    
    	md5_buf_str((uint8_t *)str0, strlen(str0), hash_str);
    	printf("MD5(\"%s\") = %s\n", str0, hash_str);
    	printf("(should be 9e107d9d372bb6826bd81d3542a419d6)\n");
    
    	md5_buf_str((uint8_t *)str1, strlen(str1), hash_str);
    	printf("MD5(\"%s\") = %s\n", str1, hash_str);
    	printf("(should be e4d909c290d0fb1ca068ffaddf22cbd0)\n");
    
    	md5_buf_str((uint8_t *)str2, strlen(str2), hash_str);
    	printf("MD5(\"%s\") = %s\n", str2, hash_str);
    	printf("(should be d41d8cd98f00b204e9800998ecf8427e)\n");
	}

	printf("done\n");

	rc = 0;
	cleanup:
    return rc;
}
