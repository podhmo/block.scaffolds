import os.path
import sys
import json

from pyramid.scaffolds.template import Template

class CombinedTemplate(object):
    _template_cls_list = None

    def __init__(self, name):
        self.templates = [cls(name) for cls in self._template_cls_list]

    def run(self, command, output_dir, vars): # this is not fail safe.
        for t in self.templates:
            t.run(command, output_dir, vars)

def safe_makedirs(template, output_dir, opts=None):
    if not template.exists(output_dir):
        template.out("Creating directory %s" % output_dir)
        if not (opts and opts.simulate):
            template.makedirs(output_dir)

def is_toplevel(path, opts=None):
    return os.path.exists(os.path.join(path,"../info.json"))

def is_already_toplevel(path, opts):
    return os.path.exists(os.path.join(path, "info.json"))

def load_info(infofile):
    if not os.path.exists(infofile):
        raise RuntimeError("info.json not found")
    with open(infofile, "r") as rf:
        return json.load(rf)
    
def find_toplevel_downer(cwd, opts=None, is_already_toplevel=is_already_toplevel):
    if not is_already_toplevel(cwd,opts):
        return None
    infofile = os.path.join(os.path.join(cwd, "info.json"))
    packagename = load_info(infofile)["package"]
    return os.path.join(cwd, packagename)
    
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

    def get_toplevel(self, command, output_dir):
        output_dir = os.path.dirname(output_dir)
        toplevel = find_toplevel_upper(output_dir, command.options)
        toplevel = toplevel or find_toplevel_downer(output_dir, command.options)
        if toplevel is None:
            raise RuntimeError("can't find toplevel from %s" % output_dir)
        return toplevel

    def write_files(self, command, output_dir, vars):
        toplevel = self.get_toplevel(command, output_dir)
        self.out_.write(u"Toplevel directory: %s\n" % toplevel)
        self.write_files_from_topdown(command, toplevel, vars)

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
