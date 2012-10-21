import os.path
import sys
import json
from pyramid.decorator import reify
from pyramid.scaffolds.template import Template
from collections import namedtuple

class CombinedTemplate(object):
    _template_cls_list = None

    def __init__(self, name):
        self.templates = [cls(name) for cls in self._template_cls_list]

    def run(self, command, output_dir, vars): # this is not fail safe.
        for t in self.templates:
            t.run(command, output_dir, vars)

TopLevelInfo = namedtuple("TopLevelInfo", "app_top module_top info")

class GetInfo(object):
    _infofile = "info.json"
    def __init__(self, start_point, opts, info_file=None):
        if info_file:
            self._info_file = info_file
        self.opts = opts

        values = self.find_toplevel_upper(start_point, opts)
        if values is None:
            values = self.find_toplevel_downer(start_point, opts)
            if values is None:
                raise RuntimeError("can't find toplevel from %s" % start_point)
        self.app_top, self.module_top, self.info = values

    def is_module_top(self, path, opts=None):
        return os.path.exists(os.path.join(path, "../", self._infofile))

    def is_app_top(self, path):
        return os.path.exists(os.path.join(path, self._infofile))

    def info_from_app_top(self, app_top):
        infopath = os.path.join(app_top, self._infofile)

        if not os.path.exists(infopath):
            raise RuntimeError("%s is not found" % infopath)
        with open(infopath, "r") as rf:
            return json.load(rf)
        
    def find_toplevel_upper(self, start_point, opts):
        module_top = find_toplevel_upper(start_point, opts, is_toplevel=self.is_module_top)
        if module_top is None:
            return None
        app_top = os.path.join(module_top, "../")
        return TopLevelInfo(app_top=app_top,
                            module_top=module_top,
                            info=self.info_from_app_top(app_top))

    def find_toplevel_downer(self, start_point, opts):
        if not self.is_app_top(start_point):
            return None
        app_top = start_point
        info  = self.info_from_app_top(app_top)
        return TopLevelInfo(app_top=app_top,
                            module_top=os.path.join(info["package"]), ##xxx.
                            info=info)
                            

def safe_makedirs(template, output_dir, opts=None):
    if not template.exists(output_dir):
        template.out("Creating directory %s" % output_dir)
        if not (opts and opts.simulate):
            template.makedirs(output_dir)

def is_toplevel(path, opts=None):
    return os.path.exists(os.path.join(path,"../info.json"))

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

class TemplateFromToplevel(Template):
    out_ = sys.stdout
    GetInfo = GetInfo
    info_file = "info.json"

    def pre(self, command, output_dir, vars):
        if "info" in vars:
            raise ValueError("info is reserved word. sorry.")

        start_point = os.path.dirname(output_dir)
        self.getinfo = GetInfo(start_point, command.options, info_file=self.info_file)
    
    def write_files(self, command, output_dir, vars):
        toplevel = self.getinfo.module_top
        vars["toplevel"] = toplevel
        vars["info"] = self.getinfo.info
        self.out_.write(u"Toplevel directory: %s\n" % toplevel)
        return self.write_files_from_topdown(command, toplevel, vars)

    def write_files_from_topdown(self, command, output_dir, vars):
        safe_makedirs(self, output_dir, command.options)
        template_dir = self.template_dir()

        self.copydir.copy_dir(
            template_dir,
            output_dir,
            vars,
            verbosity=command.verbosity,
            simulate=command.options.simulate,
            interactive=command.options.interactive,
            overwrite=command.options.overwrite,
            indent=1,
            template_renderer=self.render_template,
            )
