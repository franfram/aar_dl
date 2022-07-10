import os, sys

def abspath(path):
    path = os.path.abspath(path)
    if os.name == 'nt' and path[:2] != '\\\\':
        path = '\\\\?\\' + path
    return path

def root_abspath(*dirs):
    return os.path.join(_root_folder, *dirs)

_root_folder = abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))

sys.path.insert(0, os.path.join(_root_folder, 'scripts'))
