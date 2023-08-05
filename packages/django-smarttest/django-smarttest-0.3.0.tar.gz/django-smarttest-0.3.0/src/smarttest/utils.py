import logging
import importlib
import os

log = logging.getLogger(__name__)
DEFAULT_IGNORE_DIRS = ['migrations']


def _find_all_files_in_tree(directory, ignore_dirs=None):
    if ignore_dirs is None:
        ignore_dirs = DEFAULT_IGNORE_DIRS
    for dir_name, dirnames, filenames in os.walk(directory):
        # filter out ignored directories
        if os.path.basename(dir_name) not in ignore_dirs:
            for file_name in filenames:
                yield os.path.join(dir_name, file_name)


def load_all_modules(directory, ignore_dirs=None):
    """ Load all modules from given directory. """

    # find all files in tree
    paths = _find_all_files_in_tree(directory, ignore_dirs)
    # filter only python files
    paths = (os.path.splitext(path) for path in paths)
    paths = (path for path, ext in paths if ext == '.py')
    # create module paths
    modules = (path.replace('/', '.') for path in paths)
    # import modules
    for module_path in modules:
        try:
            importlib.import_module(module_path)
        except ImportError as e:
            log.warning(repr(e))
