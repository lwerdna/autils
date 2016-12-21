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

int main(int ac, char **av)
{
	int rc = -1;

	if(ac <= 1) {
		printf("eg: %s subprocess\n", av[0]);
		goto cleanup;
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

		if(0 != launch_ex(
			zone, // "yes"
			zargv, // {"yes", NULL}
			NULL, // child pid (don't care)
			NULL, // child stdin (don't care)
		    &child_stdout, // child stdout
			NULL // child stderr (don't care)
		)) {
			printf("ERROR! launch_ex()\n");
			goto cleanup;
		}

		printf("reading 100 bytes from continuous output stream of \"yes\"\n");
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

	while(1);

	printf("done\n");

	rc = 0;
	cleanup:
    return rc;
}
