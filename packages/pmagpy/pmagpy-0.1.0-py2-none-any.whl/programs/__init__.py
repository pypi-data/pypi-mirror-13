print "calling programs/__init__.py"

import sys
from os import path
print sys.argv
command = path.split(sys.argv[0])[-1]
print command

from prog_env import prog_env
mpl_env = prog_env.get(command[:-3])
print 'command[:-3]', command[:-3]
print 'mpl_env', mpl_env
import matplotlib
if mpl_env:
    matplotlib.use(mpl_env)
else:
    matplotlib.use("TKAgg")


import generic_magic
import sio_magic
import CIT_magic
import _2G_bin_magic
import HUJI_magic
import HUJI_magic_new
import LDEO_magic
import IODP_srm_magic
import IODP_dscr_magic
import PMD_magic
import TDT_magic
import JR6_jr6_magic
import JR6_txt_magic
import BGC_magic


__all__ = [generic_magic, sio_magic, CIT_magic, _2G_bin_magic, HUJI_magic, HUJI_magic_new, LDEO_magic, IODP_srm_magic, IODP_dscr_magic, PMD_magic, TDT_magic, JR6_jr6_magic, JR6_txt_magic, BGC_magic]

print "done with programs/__init__.py"
