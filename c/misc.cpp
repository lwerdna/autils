#include <ctype.h> // isdigit()
#include <unistd.h> // pid_t, for launch()
#include <string.h>

#include <string>
using namespace std;

extern "C" {
#include "subprocess.h"
}

int 
misc_get_py_ver(string &ver)
{
	int rc, rc_sub;
	char buf_stdout[64] = {0};
	char buf_stderr[64] = {0};
	char s_python[] = "python";
	char s_V[] = "-V";
	char *argv[3] = {s_python, s_V, NULL};
	char *buf_ver = NULL;
	
	rc = launch(s_python, argv, &rc_sub, buf_stdout, 64, buf_stderr, 64, true);

	if(rc) return -1;
	if(rc_sub) return -2;
	/* prior to Python 3.4, version information went to stderr */
	if(*buf_stdout == 'P')
		buf_ver = buf_stdout;
	else if(*buf_stderr == 'P')
		buf_ver = buf_stderr;
	else
		return -3;

	/* now buf_ver points to either stdout or stderr buf */
	if(strncmp(buf_ver, "Python ", 7)) return -4;
	if(!isdigit(buf_ver[7])) return -5;
	if(buf_ver[8] != '.') return -6;
	if(!isdigit(buf_ver[9])) return -7;
	if(buf_ver[10] != '.') return -8;

	buf_ver[10] = '\0';
	
	ver = buf_ver + 7;

	return 0;
}

