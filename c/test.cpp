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
#include "subprocess.h"
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
			printf("ERROR! ls()\n");
			goto cleanup;
		}
		for(auto i=results.begin(); i!=results.end(); ++i)
			printf("%s\n", i->c_str());

		printf("\nlisting all %s/*.c:\n", cwd.c_str());
		printf("------------------------------------\n");
		results.clear();
		if(filesys_ls(AUTILS_FILESYS_LS_EXT, ".c", cwd, results, true)) {
			printf("ERROR! ls()\n");
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
			printf("ERROR! ls()\n");
			goto cleanup;
		}
		for(auto i=results.begin(); i!=results.end(); ++i)
			printf("%s\n", i->c_str());

		printf("\nlisting all %s/test*:\n", cwd.c_str());
		printf("------------------------------------\n");
		results.clear();
		if(filesys_ls(AUTILS_FILESYS_LS_STARTSWITH, "test", cwd, results)) {
			printf("ERROR! ls()\n");
			goto cleanup;
		}
		for(auto i=results.begin(); i!=results.end(); ++i) {
			string basename;
			filesys_basename(*i, basename);
			printf("%s (basename: %s)\n", i->c_str(), basename.c_str());
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
			printf("ERROR! launch()\n");
			goto cleanup;
		}

		printf("full launch (1/2), python version is: %s\n", buf_stderr);

		if(0 != launch(one, argv, &rc, buf_stdout, 64, buf_stderr, 64)) {
			printf("ERROR! launch()\n");
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
				printf("ERROR! launch_ex()\n");
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
					printf("ERROR! read()\n"); goto cleanup;
					case 0:
					printf("ERROR! eof reaches on yes?!\n"); goto cleanup;
					case 1:
						printf("0x%02X", buf);
						if(!isspace(buf)) printf("('%c') ", buf);
						else printf(" ");
						break;
					default:
					printf("ERROR! read() returned unexpected %d\n", rc);
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

	printf("done\n");

	rc = 0;
	cleanup:
    return rc;
}
