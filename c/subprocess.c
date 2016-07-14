#include <stdio.h> // for STDIN_FILENO, etc.
#include <unistd.h> // for execve()

/*
    eg:
        path_exec = "/usr/bin/openssl"
        argv = {"/usr/bin/openssl", "s_client", "-connect", "smtp.gmail.com:464", "-crlf", "ign_eof", NULL }
        child_stdout = &fd_c_o
        child_stdin = &fd_c_i
    */
int
fork_and_launch(char *path_exec, char *const argv[], int *child_pid, int *child_stdout, 
    int *child_stdin)
{
    int rc = -1;
    int i;
    ssize_t n;
    pid_t childpid;

    /* these fd's used to send commands down to child */
    int fds_down[2];
    /* these fd's used to read output from child (he writes up to us) */
    int fds_up[2];

    /* create pipes */
    pipe(fds_down);
    pipe(fds_up);

    /* fork */
    childpid = fork();
    if(childpid == -1) {
        //printf("ERROR: fork()\n");
        goto cleanup;
    }

    /* child activity */
    if(childpid == 0) {
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
            perror("dup2()");
            goto cleanup;
        }

        /* NO PRINTF() WORK AFTER dup2() IS DONE */

        /* duplicate the up tx pipe onto stdout */
        i = dup2(fds_up[1], STDOUT_FILENO);
        if(i >= 0) {
            //printf("dup2() on STDOUT returned: %d\n", i);
            while(0);
        } 
        else {
            perror("dup2()");
            goto cleanup;
        }

        /* now execute child, which inherits file descriptors */
        execv(path_exec, argv);

        //printf("ERROR: execv()\n");
    }
    /* parent activity */
    else {
        //printf("spawned child process: %d\n", childpid);

        close(fds_down[0]); 
        close(fds_up[1]);
        *child_stdout = fds_up[0];
        *child_stdin = fds_down[1];

        rc = 0;
    }

    cleanup:
    return rc;
}
