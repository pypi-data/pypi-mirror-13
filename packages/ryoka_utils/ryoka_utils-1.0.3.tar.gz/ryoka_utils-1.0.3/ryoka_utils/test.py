#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from sys import exit
from utils import Utils
from mail import SendMail
from os import chdir, mkdir, getcwd, access, R_OK, W_OK, X_OK
from os.path import abspath, dirname, exists, join, isdir, basename

class Test:
    def __init__(self):
        self.c_dir = abspath(dirname(__file__))
        self.utils = Utils()
        self.mail = SendMail()
        self.test_dir = join(self.c_dir, ".tmp")
        self.utils.mkdir(self.test_dir)
        self.test_list = {
            "all_test": self.all_test,
            "pushd": self.pushd,
            "popd": self.popd,
            "join_dirs": self.join_dirs,
            "is_type": self.is_type,
            "mkdir": self.mkdir,
            "remove": self.remove,
            "rename": self.rename,
            "copy": self.copy,
            "chmod": self.chmod,
            "zip_tar": self.zip_tar,
            "unzip_tar": self.unzip_tar,
#            "send_mail": self.send_mail,
        }
        self.selected_test = "all_test"
        self.testing_function = ""

    def select_test(self, test_name):
        self.selected_test = test_name

    def check_correct(self, check_pattern):
        if (not check_pattern):
            self.error_test()

    def check_incorrect(self, check_pattern):
        if (check_pattern):
            self.error_test()

    def pushd(self):
        self.testing_function = "pushd"
        print("test %s..." % (self.testing_function))
        self.utils.pushd(self.test_dir)
        self.check_correct(abspath(getcwd()) == abspath(self.test_dir))
        self.utils.popd()

    def popd(self):
        self.testing_function = "popd"
        popd_dir = self.utils.join_dirs([self.test_dir, "popd"])
        self.utils.mkdir(popd_dir)
        self.utils.pushd(self.test_dir)
        self.utils.pushd(popd_dir)
        self.check_correct(abspath(getcwd()) == abspath(popd_dir))
        self.utils.popd()
        self.check_correct(abspath(getcwd()) == abspath(self.test_dir))
        self.utils.popd()

    def join_dirs(self):
        self.testing_function = "join_dirs"
        print("test %s..." % (self.testing_function))
        self.check_correct(self.test_dir + "/test1" == self.utils.join_dirs([self.test_dir, "test1"]))
        self.check_correct(self.test_dir + "/test1/test2" == self.utils.join_dirs([self.test_dir, "test1", "test2"]))

    def create_test_file(self, path):
        fd = open(path, "w")
        fd.write("Test file.")
        fd.close()

    def is_type(self):
        self.testing_function = "is_type"
        print("test %s..." % (self.testing_function))
        test_path = self.utils.join_dirs([self.test_dir, "testfile.txt"])
        self.create_test_file(test_path)
        self.check_correct(self.utils.is_type(self.test_dir, "dir"))
        self.check_incorrect(self.utils.is_type(self.test_dir, "file"))
        self.check_correct(self.utils.is_type(test_path, "file"))
        self.check_incorrect(self.utils.is_type(__file__, "dir"))

    def mkdir(self):
        self.testing_function = "mkdir"
        print("test %s..." % (self.testing_function))
        test_path = self.utils.join_dirs([self.test_dir, "test1"])
        test_path2 = self.utils.join_dirs([self.test_dir, "test1", "test2", "test3"])
        self.utils.mkdir(test_path)
        self.check_correct(self.utils.is_type(test_path, "dir"))
        self.utils.mkdir(test_path2)
        self.check_correct(self.utils.is_type(test_path2, "dir"))

    def remove(self):
        self.testing_function = "remove"
        print("test %s..." % (self.testing_function))
        test_path = self.utils.join_dirs([self.test_dir, "test1"])
        test_path2 = self.utils.join_dirs([self.test_dir, "test_file.txt"])
        self.utils.mkdir(test_path)
        self.utils.remove(test_path)
        self.check_incorrect(self.utils.is_type(test_path, "dir"))
        self.create_test_file(test_path2)
        self.utils.remove(test_path2)
        self.check_incorrect(self.utils.is_type(test_path2, "file"))

    def rename(self):
        self.testing_function = "rename"
        print("test %s..." % (self.testing_function))
        src_path = self.utils.join_dirs([self.test_dir, "src_dir"])
        src_file_path = self.utils.join_dirs([src_path, "test_file.txt"])
        dst_path = self.utils.join_dirs([self.test_dir, "dst_dir"])
        self.utils.mkdir(src_path)
        self.create_test_file(src_file_path)
        self.utils.rename(src_path, dst_path)
        self.check_correct(self.utils.is_type(dst_path, "dir"))
        self.check_incorrect(self.utils.is_type(src_path, "dir"))
        self.check_correct(self.utils.is_type(self.utils.join_dirs([dst_path, basename(src_file_path)]), "file"))
        self.clean()
        self.utils.mkdir(src_path)
        self.create_test_file(src_file_path)
        dst_file_path = self.utils.join_dirs([self.test_dir, "dst_test_file.txt"])
        self.utils.rename(src_file_path, dst_file_path)
        self.check_correct(self.utils.is_type(dst_file_path, "file"))
        self.check_incorrect(self.utils.is_type(src_file_path, "file"))

    def copy(self):
        self.testing_function = "copy"
        print("test %s..." % (self.testing_function))
        src_path = self.utils.join_dirs([self.test_dir, "test1"])
        src_file_path = self.utils.join_dirs([src_path, "test_file.txt"])
        src_file_path2 = self.utils.join_dirs([src_path, "test_file2.txt"])
        dst_path = self.utils.join_dirs([self.test_dir, "test2"])
        dst_file_path = self.utils.join_dirs([dst_path, "test_file.txt"])
        dst_file_path2 = self.utils.join_dirs([dst_path, "test_file2.txt"])
        self.utils.mkdir(src_path)
        self.create_test_file(src_file_path)
        self.utils.copy(src_path, dst_path)
        self.check_correct(self.utils.is_type(dst_path, "dir"))
        self.check_correct(self.utils.is_type(src_path, "dir"))
        self.check_correct(self.utils.is_type(dst_file_path, "file"))
        self.check_correct(self.utils.is_type(src_file_path, "file"))
        self.clean()
        self.utils.mkdir(src_path)
        self.create_test_file(src_file_path)
        self.utils.mkdir(dst_path)
        self.utils.copy(src_file_path, dst_file_path)
        self.check_correct(self.utils.is_type(dst_file_path, "file"))
        self.check_correct(self.utils.is_type(src_file_path, "file"))
        self.create_test_file(src_file_path2)
        self.utils.copy(src_path, dst_path)
        self.check_correct(self.utils.is_type(dst_file_path2, "file"))

    def chmod(self):
        self.testing_function = "chmod"
        print("test %s..." % (self.testing_function))
        test_path = self.utils.join_dirs([self.test_dir, "test_dir"])
        test_file_path = self.utils.join_dirs([self.test_dir, "test_file.txt"])
        self.utils.mkdir(test_path)
        self.create_test_file(test_file_path)
        self.utils.chmod(test_path, 0000)
        self.check_incorrect(access(test_path, R_OK))
        self.check_incorrect(access(test_path, W_OK))
        self.check_incorrect(access(test_path, X_OK))
        self.utils.chmod(test_file_path, 0000)
        self.check_incorrect(access(test_path, R_OK))
        self.check_incorrect(access(test_path, W_OK))
        self.check_incorrect(access(test_path, X_OK))
        self.utils.chmod(test_path, 0777)
        self.check_correct(access(test_path, R_OK))
        self.check_correct(access(test_path, W_OK))
        self.check_correct(access(test_path, X_OK))
        self.utils.chmod(test_file_path, 0777)
        self.check_correct(access(test_path, R_OK))
        self.check_correct(access(test_path, W_OK))
        self.check_correct(access(test_path, X_OK))

    def zip_tar(self):
        self.testing_function = "zip_tar"
        print("test %s..." % (self.testing_function))
        src_dir = self.utils.join_dirs([self.test_dir, "test_dir"])
        src_file = self.utils.join_dirs([src_dir, "test_file.txt"])
        self.utils.mkdir(src_dir)
        self.create_test_file(src_file)
        self.utils.zip_tar_bz2(src_dir, src_dir + ".tar.bz2")
        self.check_correct(self.utils.is_type(src_dir + ".tar.bz2", "file"))
        self.utils.zip_tar_gz(src_dir, src_dir + ".tar.gz")
        self.check_correct(self.utils.is_type(src_dir + ".tar.gz", "file"))

    def unzip_tar(self):
        self.testing_function = "unzip_tar"
        print("test %s..." % (self.testing_function))
        src_dir = self.utils.join_dirs([self.test_dir, "test_dir"])
        src_file = self.utils.join_dirs([src_dir, "test_file.txt"])
        self.utils.mkdir(src_dir)
        self.create_test_file(src_file)
        self.utils.pushd(self.test_dir)
        self.utils.zip_tar_bz2(basename(src_dir), src_dir + ".tar.bz2")
        self.utils.zip_tar_gz(basename(src_dir), src_dir + ".tar.gz")
        self.utils.popd()
        self.utils.remove(src_dir)
        self.utils.unzip_tar_bz2(src_dir + ".tar.bz2", dirname(src_dir))
        self.check_correct(self.utils.is_type(src_dir, "dir"))
        self.check_correct(self.utils.is_type(src_file, "file"))
        self.utils.remove(src_dir)
        self.utils.unzip_tar_gz(src_dir + ".tar.gz", dirname(src_dir))
        self.check_correct(self.utils.is_type(src_dir, "dir"))
        self.check_correct(self.utils.is_type(src_file, "file"))

    def send_mail(self):
        self.mail.set_from_address("ryoya.digion@gmail.com")
        self.mail.set_to_address("ryoya.kamikawa@digion.com")
        self.mail.set_title("Test mail.")
        self.mail.set_body("Test mail body.")
        self.mail.set_password("DigiOn0411")
        self.mail.send()

    def all_test(self):
        for key in self.test_list.keys():
            if (key == "all_test"):
                continue
            self.clean()
            self.test_list[key]()

    def error(self):
        self.__del__()
        exit()

    def success_test(self):
        print("Success test : %s" % self.selected_test)

    def error_test(self):
        print("Error test. : %s" % (self.testing_function))
        self.error()

    def error_arg(self):
        print("Invalid arguments.")
        self.error()

    def check_selected_test(self):
        for test in self.test_list.keys():
            if (self.selected_test == test):
                return
        self.error_arg()

    def execute(self):
        self.check_selected_test()
        self.clean()
        self.test_list[self.selected_test]()
        self.success_test()

    def clean(self):
        self.utils.remove(self.test_dir)
        self.utils.mkdir(self.test_dir)

    def __del__(self):
        self.utils.remove(self.test_dir)

def parse_arguments():
    argv = sys.argv
    argc = len(argv)

    if (argc == 1):
        return ""

    return argv[1]

if __name__ == '__main__':
    test = Test()

    test_name = parse_arguments()

    if (test_name != ""):
        test.select_test(test_name)
    test.execute()

    test.__del__()
    del test
