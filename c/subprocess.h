int launch_ex(char *exec_name, char *args[], pid_t *child_pid, 
    int *child_stdin, int *child_stdout, int *child_stderr);

int launch(char *exec_name, char *args[], int *ret_code, char *stdout_buf,
    int stdout_buf_sz, char *stderr_buf, int stderr_buf_size);

