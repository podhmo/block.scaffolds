import os.path
import sys
from pyramid.scaffolds.template import Template
from .coc import GetCoC

def safe_makedirs(template, output_dir, opts=None):
    if not template.exists(output_dir):
        template.out("Creating directory %s" % output_dir)
        if not (opts and opts.simulate):
            template.makedirs(output_dir)

class CombinedTemplate(object):
    _template_cls_list = None

    def __init__(self, name):
        self.templates = [cls(name) for cls in self._template_cls_list]

    def run(self, command, output_dir, vars): # this is not fail safe.
        for t in self.templates:
            t.run(command, output_dir, vars)

class TemplateFromToplevel(Template):
    out_ = sys.stdout
    GetCoC = GetCoC
    coc_file = "coc.json"

    def pre(self, command, output_dir, vars):
        if "coc" in vars:
            raise ValueError("coc is reserved word. sorry.")

        start_point = os.path.dirname(output_dir)
        self.getcoc = GetCoC(start_point, command.options, coc_file=self.coc_file)
    
    def write_files(self, command, output_dir, vars):
        toplevel = self.getcoc.module_top
        vars["toplevel"] = toplevel
        vars["coc"] = self.getcoc.coc
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
