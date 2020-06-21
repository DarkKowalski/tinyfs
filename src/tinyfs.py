#!/usr/bin/env python

import os
import sys
import errno
import logging
from fuse import FUSE, FuseOSError, Operations

class TinyFS(Operations):
    def __init__(self, root):
        self.root = root

    def _fullpath(self, path):
        if path.startswith("/"):
            path = path[1:]
        path = os.path.join(self.root, path)
        return path

    def access(self, path, mode):
        #logging.info("Filesystem Operation: access " + path)
        fullpath = self._fullpath(path)
        if not os.access(fullpath, mode):
            raise FuseOSError(errno.EACCES)

    def chmod(self, path, mode):
        #logging.info("Filesystem Operation: chmod " + path)
        fullpath = self._fullpath(path)
        return os.chmod(fullpath, mode)

    def chown(self, path, uid, gid):
        #logging.info("Filesystem Operation: chown " + path)
        fullpath = self._fullpath(path)
        return os.chown(fullpath, uid, gid)

    def getattr(self, path, fh=None):
        #logging.info("Filesystem Operation: getattr " + path)
        fullpath = self._fullpath(path)
        st = os.lstat(fullpath)
        return dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime',
                                                        'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))

    def readdir(self, path, fh):
        #logging.info("Filesystem Operation: readdir " + path)
        fullpath = self._fullpath(path)
        dirents = ['.', '..']
        if os.path.isdir(fullpath):
            dirents.extend(os.listdir(fullpath))
        for r in dirents:
            yield r

    def readlink(self, path):
        #logging.info("Filesystem Operation: readlink " + path)
        pathname = os.readlink(self._fullpath(path))
        if pathname.startswith("/"):
            return os.path.relpath(pathname, self.root)
        else:
            return pathname

    def mknod(self, path, mode, dev):
        #logging.info("Filesystem Operation: mknod " + path)
        return os.mknod(self._fullpath(path), mode, dev)

    def rmdir(self, path):
        #logging.info("Filesystem Operation: rmdir " + path)
        fullpath = self._fullpath(path)
        return os.rmdir(fullpath)

    def mkdir(self, path, mode):
        #logging.info("Filesystem Operation: mkdir " + path)
        return os.mkdir(self._fullpath(path), mode)

    def statfs(self, path):
        #logging.info("Filesystem Operation: statfs " + path)
        fullpath = self._fullpath(path)
        stv = os.statvfs(fullpath)
        return dict((key, getattr(stv, key)) for key in ('f_bavail', 'f_bfree',
                                                         'f_blocks', 'f_bsize', 'f_favail', 'f_ffree', 'f_files', 'f_flag',
                                                         'f_frsize', 'f_namemax'))

    def unlink(self, path):
        #logging.info("Filesystem Operation: unlink " + path)
        return os.unlink(self._fullpath(path))

    def symlink(self, name, target):
        #logging.info("Filesystem Operation: symlink " + name + " to " + target)
        return os.symlink(name, self._fullpath(target))

    def rename(self, old, new):
        #logging.info("Filesystem Operation: rename " + old + " to " + new)
        return os.rename(self._fullpath(old), self._fullpath(new))

    def link(self, target, name):
        #logging.info("Filesystem Operation: link " + name + " to " + target)
        return os.link(self._fullpath(target), self._fullpath(name))

    def utimens(self, path, times=None):
        #logging.info("Filesystem Operation: utimens " + path)
        return os.utime(self._fullpath(path), times)

    def open(self, path, flags):
        logging.info("File Operation: open " + path)
        fullpath = self._fullpath(path)
        return os.open(fullpath, flags)

    def create(self, path, mode, fi=None):
        logging.info("File Operation: create " + path)
        fullpath = self._fullpath(path)
        return os.open(fullpath, os.O_WRONLY | os.O_CREAT, mode)

    def read(self, path, length, offset, fh):
        logging.info("File Operation: read " + path)
        os.lseek(fh, offset, os.SEEK_SET)
        return os.read(fh, length)

    def write(self, path, buf, offset, fh):
        logging.info("File Operation: write " + path)
        os.lseek(fh, offset, os.SEEK_SET)
        return os.write(fh, buf)

    def truncate(self, path, length, fh=None):
        logging.info("File Operation: truncate " + path)
        fullpath = self._fullpath(path)
        with open(fullpath, 'r+') as f:
            f.truncate(length)

    def flush(self, path, fh):
        logging.info("File Operation: flush " + path)
        return os.fsync(fh)

    def release(self, path, fh):
        logging.info("File Operation: release " + path)
        return os.close(fh)

    def fsync(self, path, fdatasync, fh):
        logging.info("File Operation: fsync " + path)
        return self.flush(path, fh)


def main(mountpoint, root):
    logging.basicConfig(format="[%(asctime)s] [%(levelname)s] %(message)s",
                        level=logging.INFO,
                        datefmt='%Y-%m-%d %H:%M:%S')
    FUSE(TinyFS(root), mountpoint, nothreads=True, foreground=True)


if __name__ == '__main__':
    main(sys.argv[2], sys.argv[1])
