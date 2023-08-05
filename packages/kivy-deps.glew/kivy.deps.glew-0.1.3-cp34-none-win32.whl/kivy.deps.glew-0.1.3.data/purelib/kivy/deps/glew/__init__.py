
"""The following code is required to make the dependency binaries available to
kivy when it imports this package.
"""

__all__ = ('dep_bins', )

import sys
from os.path import dirname, join, isdir
import ctypes


dep_bins = []
"""A list of paths that contain the binaries of this distribution.
Can be used e.g. with pyinstaller to ensure it copies all the binaries.
"""

# See https://github.com/numpy/numpy/wiki/windows-dll-notes#python-dlls
# and https://pytools.codeplex.com/workitem/1627
try:
    _AddDllDirectory = ctypes.windll.kernel32.AddDllDirectory
    _AddDllDirectory.argtypes = [ctypes.c_wchar_p]
    # Needed to initialize AddDllDirectory modifications
    ctypes.windll.kernel32.SetDefaultDllDirectories(0x1000)
except AttributeError:
    _AddDllDirectory = ctypes.windll.kernel32.SetDllDirectoryW
    _AddDllDirectory.argtypes = [ctypes.c_wchar_p]

_root = sys.prefix
dep_bins = [join(_root, 'share', 'glew', 'bin')]
if isdir(dep_bins[0]):
    _AddDllDirectory(dep_bins[0])
else:
    dep_bins = []


