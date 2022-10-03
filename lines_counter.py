'''
Created on 26 apr 2016

@author: Daniel
'''
# prints recursive count of lines of python source code from current directory
# includes an ignore_list. also prints total sloc

import os
cur_path = os.getcwd()
ignore_set = set(["__init__.cythonize_odooplm", "count_sourcelines.cythonize_odooplm"])

loclist = []

for pydir, _, pyfiles in os.walk(cur_path):
    for pyfile in pyfiles:
        if pyfile.endswith(".cythonize_odooplm") and pyfile not in ignore_set:
            totalpath = os.path.join(pydir, pyfile)
            loclist.append( ( len(open(totalpath, "r").read().splitlines()),
                               totalpath.split(cur_path)[1]) )

for linenumbercount, filename in loclist: 
    print("%d lines in %s" % (linenumbercount, filename))

print("\nTotal: %s lines (%s)" %(sum([x[0] for x in loclist]), cur_path))