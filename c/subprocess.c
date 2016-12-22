#include <stdio.h> // for STDIN_FILENO, etc.
#include <unistd.h> // for execve()
#include <sys/wait.h> // for wait(), waitpid()
#include <signal.h> // kill()

// TODO: figure this out for windoze

/* launch a subprocess, returning pid, stdin, stdout, stderr

	caller is responsible for closing descriptors, optionally terminating child

    eg:
        exec_name = "/usr/bin/openssl"
        argv = {"/usr/bin/openssl", "s_client", "-connect", "smtp.gmail.com:464", "-crlf", "ign_eof", NULL }
        child_stdout = &fd_c_o
        child_stdin = &fd_c_i

    since execvp() is used ('p' as in path) the given executable name will be searched within the
    path, so you don't need to fully qualify it

	

    */
int
launch_ex(char *exec_name, char *argv[], pid_t *child_pid_out, int *child_stdin, 
    int *child_stdout, int *child_stderr)
{
    int rc = -1;
    int i;
    ssize_t n;
    pid_t child_pid;

    /* these fd's used to send commands down to child */
    int fds_down[2];
    /* these fd's used to read output from child (he writes up to us) */
    int fds_up[2];
    int fds_extra[2];

    /* create pipes */
    pipe(fds_down);
    pipe(fds_up);
    pipe(fds_extra);

    /* fork */
    child_pid = fork();
    if(child_pid == -1) {
        //printf("ERROR: fork()\n");
        goto cleanup;
    }

    /* child activity */
    if(child_pid == 0) {
        /* close writer from down pipes (we read from parent) */
        close(fds_down[1]); 
        /* close reader from up pipes (we write to parent) */
        close(fds_up[0]);
        close(fds_extra[0]);

        /* duplicate the down rx pipe onto stdin */
        i = dup2(fds_down[0], STDIN_FILENO);
        if(i >= 0) {
            //printf("dup2() on STDIN returned: %d\n", i);
        } 
        else {
            //perror("dup2()");
            goto cleanup;
        }

        /* //printf() WILL NOT WORK AFTER dup2() IS DONE */

        /* duplicate the up tx pipe onto stdout */
        i = dup2(fds_up[1], STDOUT_FILENO);
        if(i >= 0) {
            //printf("dup2() on STDOUT returned: %d\n", i);
            while(0);
        } 
        else {
            //perror("dup2()");
            goto cleanup;
        }

        i = dup2(fds_extra[1], STDERR_FILENO);
        if(i >= 0) {
            //printf("dup2() on STDOUT returned: %d\n", i);
            while(0);
        } 
        else {
            //perror("dup2()");
            goto cleanup;
        }

        /* now execute child, which inherits file descriptors */
        execvp(exec_name, argv);

        //printf("ERROR: execvp() allowed to fall-thru\n");
    }
    /* parent activity */
    else {
        //printf("spawned child process: %d\n", child_pid);

        close(fds_down[0]); 
        close(fds_up[1]);
        close(fds_extra[1]);

        if(child_pid_out) *child_pid_out = child_pid;

        if(child_stdin) *child_stdin = fds_down[1];
		else close(fds_down[1]);
        if(child_stdout) *child_stdout = fds_up[0];
		else close(fds_up[0]);
        if(child_stderr) *child_stderr = fds_extra[0];
		else close(fds_extra[0]);

        rc = 0;
    }

    cleanup:
    return rc;
}

int
launch(char *exec_name, char *argv[], int *ret_code, char *buf_stdout,
    int buf_stdout_sz, char *buf_stderr, int buf_stderr_sz)
{
    int rc = -1;

    int pid, in=-1, out=-1, err=-1, stat;

    if(0 != launch_ex(exec_name, argv, &pid, &in, &out, &err)) {
        goto cleanup;
    }

    /* if caller wanted output, read it */
    if(buf_stdout) read(out, buf_stdout, buf_stdout_sz);
    if(buf_stderr) read(err, buf_stderr, buf_stderr_sz);

	if(0 != kill(pid, SIGTERM)) {
		goto cleanup;
	}

    if(waitpid(pid, &stat, 0) != pid) {
        goto cleanup;
    }

    //printf("subprocess returned %d\n", stat);
    if(ret_code) {
		*ret_code = WEXITSTATUS(stat);
	}

    rc = 0;
    cleanup:
    if(in>=0) close(in);
    if(out>=0) close(out);
    if(err>=0) close(err);
    return rc;
}

