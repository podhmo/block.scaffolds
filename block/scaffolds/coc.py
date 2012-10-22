import os.path
import json
from collections import namedtuple

TopLevelCoC = namedtuple("TopLevelCoC", "app_top module_top coc")

class GetCoC(object):
    _cocfile = "coc.json"
    def __init__(self, start_point, opts, coc_file=None):
        if coc_file:
            self._coc_file = coc_file
        self.opts = opts

        values = self.find_toplevel_upper(start_point, opts)
        if values is None:
            values = self.find_toplevel_downer(start_point, opts)
            if values is None:
                raise RuntimeError("can't find toplevel from %s" % start_point)
        self.app_top, self.module_top, self.coc = values

    def is_module_top(self, path, opts=None):
        return os.path.exists(os.path.join(path, "../", self._cocfile))

    def is_app_top(self, path):
        return os.path.exists(os.path.join(path, self._cocfile))

    def coc_from_app_top(self, app_top):
        cocpath = os.path.join(app_top, self._cocfile)

        if not os.path.exists(cocpath):
            raise RuntimeError("%s is not found" % cocpath)
        with open(cocpath, "r") as rf:
            return json.load(rf)
        
    def find_toplevel_upper(self, start_point, opts):
        module_top = find_toplevel_upper(start_point, opts, is_toplevel=self.is_module_top)
        if module_top is None:
            return None
        app_top = os.path.join(module_top, "../")
        return TopLevelCoC(app_top=app_top,
                            module_top=module_top,
                            coc=self.coc_from_app_top(app_top))

    def find_toplevel_downer(self, start_point, opts):
        if not self.is_app_top(start_point):
            return None
        app_top = start_point
        coc  = self.coc_from_app_top(app_top)
        return TopLevelCoC(app_top=app_top,
                            module_top=os.path.join(coc["package"]), ##xxx.
                            coc=coc)
                            
def is_toplevel(path, opts=None):
    return os.path.exists(os.path.join(path,"../coc.json"))

def find_toplevel_upper(cwd, opts=None, is_toplevel=is_toplevel):
    path = os.path.normpath(cwd)
    if is_toplevel(path):
        return path

    fnames = path.split("/") #not support windows

    ## "a/b/c" -> [a,b,c] -> [[a],[a,b],[a,b,c]] -> [[a,b,c],[a,b],[a]]
    acc = []
    candidates = []

    for fname in fnames:
        acc.append(fname)
        candidates.append("/".join(acc))
    candidates = reversed(candidates)

    for f in candidates:
        if is_toplevel(f,opts):
            return f
