#include <dirent.h>
#include <unistd.h> // getcwd()

#include <vector>
#include <string>
using namespace std;

#include "filesys.hpp"

int 
filesys_ls(int type, string val, string where, vector<string> &results, bool addPath)
{
	// TODO: FindFirstFileA stuff on windows

	DIR *dp;
	struct dirent *ep;
	int val_n = val.size();

	dp = opendir(where.c_str());
	if(dp == NULL) return -1;

	while((ep = readdir(dp))) {
		string fileName = string(ep->d_name);

		if(type == AUTILS_FILESYS_LS_EXT) {
			if(fileName.size() < val_n) continue;
			string ext = fileName.substr(fileName.size()-val_n, string::npos);
			if(ext != val) continue;
		}
		else
		if(type == AUTILS_FILESYS_LS_STARTSWITH) {
			if(fileName.size() < val_n) continue;
			string prefix = fileName.substr(0, val_n);
			if(prefix != val) continue;
		}
		
		if(addPath)		
			results.push_back(where + "/" + fileName);
		else
			results.push_back(fileName);
	}

	closedir(dp);

	return 0;
}

int
filesys_cwd(string &result)
{
	char cwd[PATH_MAX];

	if(cwd != getcwd(cwd, PATH_MAX)) return -1;

	result = cwd;

	return 0;
}

int
filesys_basename(string path, string &result)
{
	char buf[PATH_MAX];
	int len = path.size();
	if(len >= PATH_MAX) return -1;
	strcpy(buf, path.c_str());
	if(strlen(buf) != len) return -1;
	
	for(int i=len-1; i>=0; --i) {
		/* if slash, return everything after */
		if(buf[i] == '/' || buf[i] == '\\') {
			result = buf+i+1;
			return 0;
		}
	}

	/* if no slashes found, return the whole string */
	result = buf;
	return 0;			
}
