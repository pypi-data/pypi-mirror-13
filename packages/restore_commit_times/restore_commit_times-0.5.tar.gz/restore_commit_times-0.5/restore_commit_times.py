#!/usr/bin/env python
# encoding: utf-8

"""Restore files mtime from Git commit times

    Usage: %s [-q] <repo1> [<repo2>]

"""

import logging
import os
import sys

import git

log = logging.getLogger(__name__)


def restore_commit_times(path):

    log.debug("Restoring file mtimes for path: %s", path)

    def walk(tree):
        ret = list()
        for i in tree:
            ret.append(i)
            if i.type == 'tree':
                ret.extend(walk(i))
        return ret

    repo = git.Repo(path)

    def find_mtimes(repo):
        objects = walk(repo.tree())
        t = repo.head.commit
        tt = t.traverse()
        ret = {}
        while objects:
            hashes = set(i.binsha for i in walk(t.tree))
            # iterate over reversed list to be able to remove elements by index
            for n, i in reversed(list(enumerate(objects))):
                if i.binsha not in hashes:
                    del objects[n]
                else:
                    if i.path not in ret or t.authored_date < ret[i.path]:
                        ret[i.path] = t.authored_date
            try:
                t = next(tt)
            except StopIteration:
                break
        return ret

    for i, mtime in find_mtimes(repo).items():
        fname = os.path.join(path, i)
        log.debug("%s %s", mtime, fname)
        os.utime(fname, (mtime, mtime), follow_symlinks=False)

    for sm in repo.submodules:
        sm_repo = git.Repo(os.path.join(repo.git_dir, 'modules', sm.name))
        for i, mtime in find_mtimes(sm_repo).items():
            fname = os.path.join(path, sm.path, i)
            log.debug("%s %s", mtime, fname)
            os.utime(fname, (mtime, mtime), follow_symlinks=False)


def main():

    if '-q' in sys.argv:
        logging.basicConfig(level=logging.INFO, format="%(message)s")
        sys.argv.remove('-q')
    else:
        logging.basicConfig(level=logging.DEBUG, format="%(message)s")

    if len(sys.argv) < 2:
        sys.stderr.write(__doc__ % sys.argv[0])
        return 1

    for path in sys.argv[1:]:
        restore_commit_times(path)


if __name__ == "__main__":
    main()
