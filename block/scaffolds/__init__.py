from pyramid.scaffolds import PyramidTemplate
from .template import CombinedTemplate
from .template import TemplateFromToplevel


class ProjectTemplate(PyramidTemplate):
    _template_dir = 'project'
    summary = '-- block.scaffolds -- Project template'

class ViewTemplate(TemplateFromToplevel):
    summary = "-- block.scaffolds -- View files"
    _template_dir = "view"

class ModelTemplate(TemplateFromToplevel):
    summary = "-- block.scaffolds -- Model files"
    _template_dir = "model"

class NewFunctionTemplate(CombinedTemplate):
    _template_cls_list = [ViewTemplate, ModelTemplate]
    summary = '-- block.scaffolds -- view,models files'
