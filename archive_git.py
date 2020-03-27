import numpy as np
import matplotlib.pyplot as plt
import json
import sys
import time
import os
import glob
import shutil
import datetime
from optparse import OptionParser


def create_tempdir(flag=1):
    print(datetime.date.today())
    datenm = "{0:%Y%m%d}".format(datetime.date.today())
    dirnum = len(glob.glob("./temp_" + datenm + "*/"))
    if flag == -1 or dirnum == 0:
        tmpdir = "./temp_{}{:03}/".format(datenm, dirnum)
        os.makedirs(tmpdir)
        fp = open(tmpdir + "not_ignore.txt", "w")
        fp.close()
    else:
        tmpdir = "./temp_{}{:03}/".format(datenm, dirnum - 1)
    print(tmpdir)
    return tmpdir


if __name__ == '__main__':
    argvs = sys.argv
    parser = OptionParser()
    parser.add_option("--dir", dest="dir", default=None)
    parser.add_option("--name", dest="name", default="Repo")
    parser.add_option("--sdir", dest="sdir", default="./")
    opt, argc = parser.parse_args(argvs)
    print(opt, argc)

    if opt.dir == None:
        tmpdir = create_tempdir()
    else:
        tmpdir = opt.dir
    tarnum = len(glob.glob(tmpdir + opt.name + "*.tar.gz")) + 1
    tar_name = '{}{}_{:03}.tar.gz'.format(tmpdir, opt.name, tarnum)
    print(tarnum)

    #
    # Compression
    # tar -zcvf filename.tar.gz directoryname
    #
    # Thaw
    # tar -zxvf filename.tar.gz
    #
    os.system('git archive HEAD ' + opt.sdir + ' --output=' + tar_name)
