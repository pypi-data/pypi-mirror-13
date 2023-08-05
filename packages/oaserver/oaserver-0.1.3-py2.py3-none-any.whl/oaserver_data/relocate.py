"""
try to relocate a virtualenv
usage
create virtualenv
install stuff

copy virtualenv directory to new location
launch relocate from new root dir of virtualenv
python relocate.py
"""

from os import chmod, getcwd, listdir
from os.path import islink
from os.path import join as pj
import stat
import sys

root = getcwd()

print(root)

# modify shebang line of scripts in bin
# scripts are all files that start with shebang #! .../python
print("shebang")

if "win" in sys.platform:
    bin_dir = "Scripts"
else:
    bin_dir = "bin"

for fname in listdir(bin_dir):
    pth = pj(bin_dir, fname)
    if not islink(pth):
        with open(pth, 'rb') as f:
            header = f.readline()
            data = f.read()
            f.close()
            if header.startswith("#!") and "python" in header:
                with open(pth, 'wb') as f:
                    f.write("#! %s/%s/python\n" % (root, bin_dir))
                    f.write(data)
                    f.close()

# create inve bash file
print("inve")

txt = """#!/%s/sh
export VIRTUAL_ENV="%s"
export PATH="$VIRTUAL_ENV/bin:$PATH"
export LD_LIBRARY_PATH="$VIRTUAL_ENV/lib/lib"
unset PYTHON_HOME

PS1="(`basename \"$VIRTUAL_ENV\"`)[\u@\h \W]\$"
export PS1

exec "${@:-$SHELL}"
""" % (bin_dir, root)

with open(pj(bin_dir, "inve"), 'w') as f:
    f.write(txt)
    f.close()
    chmod(pj(bin_dir, "inve"), 0775)
