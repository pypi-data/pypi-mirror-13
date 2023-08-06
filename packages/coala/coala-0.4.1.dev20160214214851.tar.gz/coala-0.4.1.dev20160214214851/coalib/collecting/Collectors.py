import os

from coalib.collecting.Importers import iimport_objects
from coalib.misc.Decorators import yield_once
from coalib.output.printers.LOG_LEVEL import LOG_LEVEL
from coalib.parsing.Globbing import iglob, fnmatch


def _get_kind(bear_class):
    try:
        return bear_class.kind()
    except NotImplementedError:
        return None


def _import_bears(file_path, kinds):
    # recursive imports:
    for bear_list in iimport_objects(file_path,
                                     names='__additional_bears__',
                                     types=list):
        for bear_class in bear_list:
            if _get_kind(bear_class) in kinds:
                yield bear_class
    # normal import
    for bear_class in iimport_objects(file_path,
                                      attributes='kind',
                                      local=True):
        if _get_kind(bear_class) in kinds:
            yield bear_class


@yield_once
def icollect(file_paths):
    """
    Evaluate globs in file paths and return all matching files.

    :param file_paths:  file path or list of such that can include globs
    :return:            iterator that yields paths of all matching files
    """
    if isinstance(file_paths, str):
        file_paths = [file_paths]

    for file_path in file_paths:
        for match in iglob(file_path):
            yield match


def collect_files(file_paths, ignored_file_paths=None, limit_file_paths=None):
    """
    Evaluate globs in file paths and return all matching files

    :param file_paths:         file path or list of such that can include globs
    :param ignored_file_paths: list of globs that match to-be-ignored files
    :param limit_file_paths:   list of globs that the files are limited to
    :return:                   list of paths of all matching files
    """
    valid_files = list(filter(os.path.isfile, icollect(file_paths)))
    valid_files = remove_ignored(valid_files, ignored_file_paths or [])
    valid_files = limit_paths(valid_files, limit_file_paths or [])
    return valid_files


def collect_dirs(dir_paths, ignored_dir_paths=None):
    """
    Evaluate globs in directory paths and return all matching directories

    :param dir_paths:         file path or list of such that can include globs
    :param ignored_dir_paths: list of globs that match to-be-ignored dirs
    :return:                  list of paths of all matching directories
    """
    valid_dirs = list(filter(os.path.isdir, icollect(dir_paths)))
    return remove_ignored(valid_dirs, ignored_dir_paths or [])


@yield_once
def icollect_bears(bear_dirs, bear_globs, kinds, log_printer):
    """
    Collect all bears from bear directories that have a matching kind.

    :param bear_dirs:   directory name or list of such that can contain bears
    :param bear_globs:  globs of bears to collect
    :param kinds:       list of bear kinds to be collected
    :param log_printer: log_printer to handle logging
    :return:            iterator that yields a tuple with bear class and
                        which bear_glob was used to find that bear class.
    """
    for bear_dir in filter(os.path.isdir, icollect(bear_dirs)):
        for bear_glob in bear_globs:
            for matching_file in iglob(
                    os.path.join(bear_dir, bear_glob + '.py')):

                try:
                    for bear in _import_bears(matching_file, kinds):
                        yield bear, bear_glob
                except BaseException as exception:
                    log_printer.log_exception(
                        "Unable to collect bears from {file}. Probably the "
                        "file is malformed or the module code raises an "
                        "exception.".format(file=matching_file),
                        exception,
                        log_level=LOG_LEVEL.WARNING)


def collect_bears(bear_dirs, bear_globs, kinds, log_printer):
    """
    Collect all bears from bear directories that have a matching kind.

    :param bear_dirs:   directory name or list of such that can contain bears
    :param bear_globs:  globs of bears to collect
    :param kinds:       list of bear kinds to be collected
    :param log_printer: log_printer to handle logging
    :return:            tuple of list of matching bear classes based on kind.
                        The lists are in the same order as `kinds`
    """
    bears_found = tuple([] for i in range(len(kinds)))
    bear_globs_with_bears = set()
    for bear, glob in icollect_bears(bear_dirs, bear_globs, kinds, log_printer):
        index = kinds.index(_get_kind(bear))
        bears_found[index].append(bear)
        bear_globs_with_bears.add(glob)

    empty_bear_globs = set(bear_globs) - set(bear_globs_with_bears)
    for glob in empty_bear_globs:
        log_printer.warn("No bears were found matching '{}'.".format(glob))

    return bears_found


def remove_ignored(file_paths, ignored_globs):
    """
    Removes file paths from list if they are ignored.

    :param file_paths:    file path string or list of such
    :param ignored_globs: list of globs that match to-be-ignored file paths
    :return:              list without those items that should be ignored
    """
    file_paths = list(set(file_paths))
    reduced_list = file_paths[:]

    for file_path in file_paths:
        for ignored_glob in ignored_globs:
            if fnmatch(file_path, ignored_glob):
                reduced_list.remove(file_path)
                break

    return reduced_list


def limit_paths(file_paths, limit_globs):
    """
    Limits file paths from list based on the given globs.

    :param file_paths:  file path string or list of such
    :param limit_globs: list of globs to limit the file paths by
    :return:            list with only those items that in the limited globs
    """
    file_paths = list(set(file_paths))
    limited_list = file_paths[:]

    for file_path in file_paths:
        for limit_glob in limit_globs:
            if not fnmatch(file_path, limit_glob):
                limited_list.remove(file_path)
                break

    return limited_list
