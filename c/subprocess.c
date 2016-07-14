#include <stdio.h> // for STDIN_FILENO, etc.
#include <unistd.h> // for execve()
#include <sys/wait.h> // for wait(), waitpid()

// TODO: figure this out for windoze

/*
    eg:
        exec_name = "/usr/bin/openssl"
        argv = {"/usr/bin/openssl", "s_client", "-connect", "smtp.gmail.com:464", "-crlf", "ign_eof", NULL }
        child_stdout = &fd_c_o
        child_stdin = &fd_c_i

    since execvp() is used ('p' as in path) the given executable name will be searched within the
    path, so you don't need to fully qualify it

    */
int
launch_halfway(char *exec_name, char *argv[], pid_t *child_pid_out, int *child_stdout, 
    int *child_stdin)
{
    int rc = -1;
    int i;
    ssize_t n;
    pid_t child_pid;

    /* these fd's used to send commands down to child */
    int fds_down[2];
    /* these fd's used to read output from child (he writes up to us) */
    int fds_up[2];

    /* create pipes */
    pipe(fds_down);
    pipe(fds_up);

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

        /* now execute child, which inherits file descriptors */
        execvp(exec_name, argv);

        //printf("ERROR: execvp() allowed fall-thru\n");
    }
    /* parent activity */
    else {
        //printf("spawned child process: %d\n", child_pid);

        close(fds_down[0]); 
        close(fds_up[1]);
        if(child_pid_out) *child_pid_out = child_pid;
        if(child_stdout) *child_stdout = fds_up[0];
        if(child_stdin) *child_stdin = fds_down[1];

        rc = 0;
    }

    cleanup:
    return rc;
}

int
launch(char *exec_name, char *argv[], int *ret_code, char *outbuf, int size)
{
    int rc = -1;

    int pid, out=-1, in=-1, stat;

    if(0 != launch_halfway(exec_name, argv, &pid, &out, &in)) {
        //printf("ERROR: launch_halfway()\n");
        goto cleanup;
    }
   
    if(waitpid(pid, &stat, 0) != pid) {
        //printf("ERROR: waitpid() didn't return pid\n");
        goto cleanup;
    }

    /* if caller wanted output, read it */
    if(outbuf) {
        read(out, outbuf, size);
    }

    //printf("subprocess returned %d\n", stat);
    if(ret_code) *ret_code = stat;

    rc = 0;
    cleanup:
    if(out<0) close(out);
    if(in<0) close(in);
    return rc;
}

