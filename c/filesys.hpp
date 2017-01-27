#define AUTILS_FILESYS_LS_ANY 0
#define AUTILS_FILESYS_LS_EXT 1
#define AUTILS_FILESYS_LS_STARTSWITH 3
#define AUTILS_FILESYS_LS_EXEC 4

int filesys_cwd(string &result);

int filesys_ls(int type, string val, string where, vector<string> &results, bool addPath=false);

int filesys_basename(string path, string &result);

int filesys_copy(string src, string dst, string& err);

