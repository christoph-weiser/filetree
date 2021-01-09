#!/usr/bin/env python3

"""
filetree.py - Compare File and Directory structures

The Filetree class does represent a file/direcory structure,
while the Dirtree class can be used to represent a directory
only structure.

The Module does also provide the nesecarry routines
to compare these trees against each other.

"""

import os
import re
import copy

from hashlib import md5
from collections import namedtuple
from warnings import warn


class Basetree:

    def __init__(self, path, name=""):
        self.name = name
        self._abspath = self._parse_path_argument(path)
        self.leadingpath, self.rootdir= self._seperate_path(self._abspath)
        self._elemlist = []
        self._applied_filters = []


    def __repr__(self):
        return "<class 'filetree.Basetree'>"


    def __len__(self):
        return self.size


    def __iter__(self):
        for elem in self.elements:
            yield elem


    def __getitem__(self, key):
        return self._elemlist[key]


    def __ge__(self, other):
        return  self.size >= other.size


    def __lt__(self, other):
        return  self.size < other.size


    def __le__(self, other):
        return  self.size <= other.size


    def __ne__(self, other):
        return not self.__eq__(other)


    def __gt__(self, other):
        return  self.size > other.size


    def _parse_path_argument(self, path):
        """ Parse the provided path argument and
        return the absolute path to the root.

        Args:
            path (str): path to root of tree

        Returns:
            str: absolute path to root.

        """
        cwd = os.getcwd()
        if path.endswith("/"):
            path = path[0:-1]
        if path.startswith("/"):
            abspath = path
        elif path.startswith("./"):
            path = path[2:]
            abspath = "/".join([cwd, path])
        else:
            abspath = "/".join([cwd, path])
        return abspath


    def _seperate_path(self, path):
        """ Seperate the leading path and the directory of
        interest. /leading/path/to/directory

        Args:
            path: (str) The path to seperate.

        Returns:
            tuple: leadingpath, directory

        """
        path_elements = path.split("/")
        leadingpath = "/" + "/".join(path_elements[1:-1]) + "/"
        if not path_elements[-1]:
            directory = path_elements[-2]
        else:
            directory = path_elements[-1]
        return leadingpath, directory


    def _create_abslist(self, tree, dirsonly=False):
        """ Create a list for all elements in the tree with
        their respective absolute path.

        Args:
            tree (generator): walk object containing the tree.
            dirsonly (bool): generate a tree of directories only. 

        Returns:
            (list) absolute path to all elements in tree.

        """
        elem_list = []
        for root, dirs, files in tree:
            if dirsonly:
                for entry in dirs:
                    if root:
                        elem_list.append("{}/{}".format(root, entry))
                    else:
                        elem_list.append("{}".format(entry))
            else:
                for entry in files:
                    if root:
                        elem_list.append("{}/{}".format(root, entry))
                    else:
                        elem_list.append("{}".format(entry))
        return elem_list


    def _create_rellist(self, abslist, path):
        """ Creates a list relative to a root dir
        from a abslist.

        Args:
            abslist (list): list with absolute path
            path (str): path to root directory.

        Returns:
            list: elements in tree relative to the root.

        """
        return [p[len(path) + 1:] for p in abslist]


    def compare(self, tree, method):
        """ compare the tree against another tree.

        Args:
            tree (Tree): Tree object to compare against.
            method (str): comparison type (size, set, binary)

        Returns:
            namedtuple with comparison results.

        """
        if method == "size":
            res = compare_size(self, tree)
        elif method == "set":
            res = compare_set(self, tree)
        elif method in ["binary", "bin"]:
            res = compare_binary(self, tree)
        return res


    def filter(self, expression, inplace=False, regex=False, invert=False):
        """ Filter the elements of the Tree by name

        Args:
            expression (str): expression for matching.
            inplace (bool, default True): modify the Tree based on matches.
            regex (bool, default False): make expression regular expression.
            invert (bool, default False): invert the match results

        Returns:
            Tree, None: depening on inplace option.

        """
        filtered = []
        if not regex:
            expression = ".*{}.*".format(expression)
        for name in self.elements:
            if invert:
                if not re.fullmatch(expression, name):
                    filtered.append(name)
            else:
                if re.fullmatch(expression, name):
                    filtered.append(name)

        if invert:
            expression = "!><{}".format(expression)

        if inplace:
            self.elements = filtered
            self._applied_filters.append(expression)
        else:
            selfcopy = copy.deepcopy(self)
            selfcopy.elements = filtered
            selfcopy._applied_filters.append(expression)
            return selfcopy


    @property
    def size(self):
        """ total number of elements in tree """
        return len(self._elemlist)


    @property
    def elements(self):
        """ list of elements in tree """
        return self._elemlist


    @elements.setter
    def elements(self, arg):
        """set the list of elements in tree """
        self._elemlist = arg


    @property
    def path(self):
        """ absolute path to the root directory of the tree.  """
        return self._abspath


    @property
    def applied_filters(self):
        """ returns the filters applied to the tree """
        return self._applied_filters



class Filetree(Basetree):
    """ The Filetree class represents the files
    in a directory structure (Details below).

    Args:
    -----
        path (str): the path to the root directory
        name (str, optional): name for the Filetree object

    Properties:
    -----------
        files (list): relpath/filename for all files in tree
        absfiles (list): abspath/filename for all files in tree
        size (int): number of elements in tree
        path (str): absolute path to root dir.
        applied_filters (list): filters applied to orignal tree.

    Generator:
    ----------
        When used as a generator the Filetree
        yields the files of the sorted tree.

    Description:
    ------------
        A filetree object is a representation of
        a directory tree containing files.

        root
           |--dira
           |     |--filea
           |     |--fileb
           |     |--subdir
           |             |--filea
           |             |--fileb
           |--dirb
                 |--filea
                 |--fileb

        It can be compared to other filetrees in
        terms of its size, its set and binary
        content.

        A filetree can also be filtered to match
        certain patterns.
    ------------
    """

    def __init__(self, path, name=""):
        super().__init__(path, name)
        abslist = self._create_abslist(os.walk(self._abspath))
        self._elemlist = self._create_rellist(abslist, self._abspath)
        self._elemlist.sort()
        os.listdir(self._abspath)


    def __repr__(self):
        return "<class 'filetree.Filetree'>"


    def __str__(self):
        filters = "> <&> <".join(self._applied_filters)
        return "Filetree object named: <{}>.\n" \
               "Has Root at: <{}>\n" \
               "Has <{}> Elements: \n" \
               "Filters <{}>\n".format(self.name, self._abspath, self.size, filters)


    def __eq__(self, other):
        return (self.compare(other, "set").result and
                self.compare(other, "binary").result)


    @property
    def files(self):
        """ relative filenames in tree """
        return self._elemlist


    @property
    def absfiles(self):
        """ absolute filenames in tree """
        return [self._abspath + "/" + x for x in self._elemlist]


class Dirtree(Basetree):
    """ The Dirtree class represents the directories
    in a directory structure (Details below).

    Args:
    -----
        path (str): the path to the root directory
        name (str, optional): name for the Dirtree object

    Properties:
    -----------
        directories (list): relpath/name for all directories in tree
        absdirectories (list): abspath/name for all directories in tree
        size (int): number of elements in tree
        path (str): absolute path to root dir.
        applied_filters (list): filters applied to orignal tree.

    Generator:
    ----------
        When used as a generator the Dirtree
        yields the directories of the sorted tree.

    Description:
    ------------
        A Dirtree object is a representation of a 
        Directory structure.

        root
           |--dira
           |     |
           |     |--subdir
           |             |
           |             |--subsubdir
           |--dirb
                 |
                 |--subdira
                 |--subdirb

        It can be compared to other Dirtrees in
        terms of its size and its set of elements.

        A Dirtree can also be filtered to match
        certain patterns.
    ------------
    """

    def __init__(self, path, name=""):
        super().__init__(path, name)
        abslist = self._create_abslist(os.walk(self._abspath), True)
        self._elemlist = self._create_rellist(abslist, self._abspath)
        self._elemlist.sort()


    def __repr__(self):
        return "<class 'filetree.Dirtree'>"


    def __str__(self):
        filters = "> <&> <".join(self._applied_filters)
        return "Dirtree object named: <{}>.\n" \
               "Has Root at: <{}>\n" \
               "Has <{}> Elements: \n" \
               "Filters <{}>\n".format(self.name, self._abspath, self.size, filters)


    def __eq__(self, other):
        return (self.compare(other, "set").result)


    @property
    def directories(self):
        """ relative directories in tree """
        return self._elemlist


    @property
    def absdirectories(self):
        """ absolute directories in tree """
        return [self._abspath + "/" + x for x in self._elemlist]



def compare_size(tree_a, tree_b):
    """Analyze if there is a difference in the number
    of files between to Tree objects.

    Args:
        tree_a (Tree): comparison object a
        tree_b (Tree): comparison object b

    Returns:
        result (namedtuple): comparison result with properties:
            result (boolean): comparison outcome
            size_a (int): size of Tree A 
            size_b (int): size of Tree B

    """
    result = namedtuple("result", ["result", "size_a", "size_b"])

    result.na = tree_a.size
    result.nb = tree_b.size

    if result.na == result.nb:
        result.result = True
    else:
        result.result = False
    return result


def compare_set(tree_a, tree_b):
    """ Compare to filetrees by comparing
    their element sets.

    Args:
        set_a (Tree): comparison object a
        set_b (Tree): comparison object b

    Returns:
        result (namedtuple): comparison result with properties
            result (boolean): comparison outcome
            missing_a (set): missing files in tree a
            missing_b (set): missing files in tree b

    """
    result = namedtuple("result", ["result", "missing_a", "missing_b"])

    set_a = set(tree_a.elements)
    set_b = set(tree_b.elements)

    if set_a == set_b:
        result.result = True
        diff_a = []
        diff_b = []
    else:
        result.result = False
        diff_a = list(set_b.difference(set_a))
        diff_b = list(set_a.difference(set_b))

    result.missing_a = diff_a
    result.missing_b = diff_b
    return result


def compare_binary(tree_a, tree_b, hashmethod=md5):
    """Analyze any difference in the files in the Trees. 
    This excludes files that are not present in both trees.

    Note:
    This function is only usefull when operating on Filetree
    objects.

    Args:
        tree_a (Tree): tree a to compare
        tree_b (Tree): tree b to compare
        hashmethod (function): hash function to compare binary
                           file content with. (md5, sha1, sha256)

    Returns:
        result (namedtuple): comparison result with properties
            result (boolean): comparison outcome
            diff (list): files with binary difference

    """

    result = namedtuple("result", ["result", "diff"])

    if not (isinstance(tree_a, Filetree) and isinstance(tree_b, Filetree)):
        warn("Binary Comparison for Dirtree's is meaningless", UserWarning)
        result.result = True
        result.diff = None
        return result

    else:
        set_result = compare_set(tree_a, tree_b)
        try:
            allfiles = set(tree_a.files).union(set(tree_b.files))
            excluded = set(set_result.missing_a).union(set(set_result.missing_b))
            comp_set = allfiles.difference(excluded)
        except TypeError:
            comp_set = tree_a.files
        diff = []
        for filename in comp_set:
            if _hash(f"{tree_a.path}/{filename}") != _hash(f"{tree_b.path}/{filename}"):
                diff.append(filename)
        result.diff = diff
        if len(diff) == 0:
            result.result = True
        else:
            result.result = False
    return result


def _hash(filepath, method=md5):
    hasher = method()
    with open(filepath, 'rb') as file:
        chunk = 0
        while chunk != b'':
            chunk = file.read(1024)
            hasher.update(chunk)
    return hasher.hexdigest()
