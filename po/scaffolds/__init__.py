from pyramid.scaffolds import PyramidTemplate
from .template import CombinedTemplate
from .template import TemplateFromToplevel


class ProjectTemplate(PyramidTemplate):
    _template_dir = 'project'
    summary = '-- po.scaffolds -- Project template'

class ViewTemplate(TemplateFromToplevel):
    summary = "-- po.scaffolds -- View files"
    _template_dir = "view"

class ModelTemplate(TemplateFromToplevel):
    summary = "-- po.scaffolds -- Model files"
    _template_dir = "model"

class NewFunctionTemplate(CombinedTemplate):
    _template_cls_list = [ViewTemplate, ModelTemplate]
    summary = '-- po.scaffolds -- view,models files'
