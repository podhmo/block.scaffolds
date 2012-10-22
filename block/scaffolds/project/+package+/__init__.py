# -*- coding:utf-8 -*-

import re
from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from .commons.models import (
    DBSession,
    Base
)

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings)
    config.add_static_view('static', 'static', cache_max_age=3600)

    config.include(".models")
    config.include(".views")
    config.include(".cells")
    
    starts_with_test_rx = re.compile("¥.test")
    config.scan(ignore=lambda x : not starts_with_test_rx.search(x))
    return config.make_wsgi_app()
