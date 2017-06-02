#include <dirent.h>
#include <unistd.h> // getcwd()
#include <stdio.h>
#include <stdlib.h>

#include <sys/stat.h>
#include <sys/types.h>

#include <vector>
#include <string>
using namespace std;

#include "filesys.hpp"

int
filesys_read(string path, string mode, vector<uint8_t> &result, string &error)
{
	int rc = -1;
	long remaining;
	unsigned char buf[4096];

	FILE *fp = NULL;

	const char *fpath = path.c_str();
	const char *fmode = mode.c_str();

	fp = fopen(fpath, fmode);
	if(!fp) {
		error = "fopen()";
		goto cleanup;
	}

	fseek(fp, 0, SEEK_END);
	remaining = ftell(fp);
	rewind(fp);

	result.clear();

	while(remaining) {
		/* chunkSz = min(remaining, buffer) */
		int chunkSz = sizeof(buf);
		if(remaining < sizeof(buf))
			chunkSz = remaining;

		/* read to buffer */
		if(fread(buf, chunkSz, 1, fp) != 1) {
			error = "fread()";
			goto cleanup;
		}

		/* append to result */
		std::copy(buf, buf+chunkSz, std::back_inserter(result));

		remaining -= chunkSz;
	}

	rc = 0;
	cleanup:
	if(fp) fclose(fp);
	return rc;
}

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

int 
filesys_copy(string src, string dst, string& err)
{
	int rc = -1;
	long left;
	unsigned char buf[4096];
	FILE *fpsrc=NULL, *fpdst=NULL;

	fpsrc = fopen(src.c_str(), "r");
	if(!fpsrc) {
		err = "couldn't open source";
		goto cleanup;
	}

	fseek(fpsrc, 0, SEEK_END);
	left = ftell(fpsrc);
	rewind(fpsrc);

	fpdst = fopen(dst.c_str(), "wb");
	if(!fpdst) {
		err = "couldn't open destination";
		goto cleanup;
	}

	while(left) {
		/* chunk = min(remaining, buffer) */
		int chunk = sizeof(buf);
		if(left < sizeof(buf))
			chunk = left;

		/* read/write */
		if(fread(buf, chunk, 1, fpsrc) != 1) {
			err = "fread() didn't read all requested bytes";
			goto cleanup;
		}

		if(fwrite(buf, chunk, 1, fpdst) != 1) {
			err = "fwrite() didn't write all requested bytes";
			goto cleanup;
		}

		left -= chunk;
	}

	/* owner, permissions */
	struct stat fst;
	fstat(fileno(fpsrc), &fst);
	fchown(fileno(fpdst), fst.st_uid, fst.st_gid);
	fchmod(fileno(fpdst), fst.st_mode);

	rc = 0;

	cleanup:
	if(fpsrc) {
		fclose(fpsrc);
		fpsrc = NULL;
	}
	if(fpdst) {
		fclose(fpdst);
		fpdst = NULL;
	}

	return rc;
}


