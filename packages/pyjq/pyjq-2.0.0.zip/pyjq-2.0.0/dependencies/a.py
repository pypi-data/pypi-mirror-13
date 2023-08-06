import tarfile
import posixpath

def get_members(tar):
    for tarinfo in tar.getmembers():
        posixpath.
        tarinfo.name = tarinfo.name[offset:]
        yield tarinfo

tar = tarfile.open("jq-1.5.tar.gz")
tar.extractall(path, get_members(tar))
