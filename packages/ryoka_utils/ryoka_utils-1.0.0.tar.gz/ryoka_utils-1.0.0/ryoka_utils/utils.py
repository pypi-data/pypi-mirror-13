#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Import packages
from os import chmod, remove, rename, getcwd, chdir, makedirs, walk, environ
from os.path import abspath, dirname, join, isdir, isfile, exists, basename
from shutil import copyfile, copytree, rmtree
from tarfile import open

class Utils:
    def __init__(self):
        self.c_dir = abspath(dirname(__file__))
        self.path_list = []

    def pushd(self, path):
        self.path_list.append(getcwd())
        chdir(path)

    def popd(self):
        last_idx = len(self.path_list) - 1
        chdir(self.path_list[last_idx])
        del self.path_list[last_idx]

    def join_dirs(self, path_list):
        path = ""
        for idx in range(len(path_list)):
            path = join(path, path_list[idx])
        return path

    def is_type(self, path, type_name):
        if (type_name == "file"):
            if(isfile(path)):
                return True
        elif (type_name == "dir"):
            if (isdir(path)):
                return True
        return False

    def is_root(self):
        return (environ.get("USER") == "root")

    def mkdir(self, path):
        if (not exists(path)):
            makedirs(path)

    def remove(self, path):
        if (self.is_type(path, "file")):
            remove(path)
        elif (self.is_type(path, "dir")):
            rmtree(path)

    def rename(self, src, dst):
        if (exists(dst)):
            self.remove(dst)

        if (isfile(src)):
            rename(src, dst)
        elif (isdir(src)):
            self.remove(dst)
            self.copy(src, dst)
            self.remove(src)

    def copy(self, src, dst):
        if (self.is_type(src, "file") and self.is_type(dirname(dst), "dir") and not self.is_type(dst, "file")):
            copyfile(src, dst)
        elif (self.is_type(src, "file") and self.is_type(dst, "file")):
            self.remove(dst)
            copyfile(src, dst)
        elif (self.is_type(src, "dir")):
            self.remove(dst)
            copytree(src, dst)

    def chmod(self, path, mode):
        if (self.is_type(path, "file") or self.is_type(path, "dir")):
            chmod(path, mode)

    def unzip_tar(self, src, dst):
        tf = open(src)
        tf.extractall(dst)
        tf.close()

    def zip_tar(self, src, dst, mode):
        tf = open(dst, mode)
        for root, dirs, files in walk(src):
            for file_path in files:
                tf.add(self.join_dirs([root, file_path]))
        tf.close() 

    def unzip_tar_bz2(self, src, dst):
        self.unzip_tar(src, dst)

    def unzip_tar_gz(self, src, dst):
        self.unzip_tar(src, dst)

    def zip_tar_bz2(self, src, dst):
        self.zip_tar(src, dst, 'w:bz2')

    def zip_tar_gz(self, src, dst):
        self.zip_tar(src, dst, 'w:gz')


