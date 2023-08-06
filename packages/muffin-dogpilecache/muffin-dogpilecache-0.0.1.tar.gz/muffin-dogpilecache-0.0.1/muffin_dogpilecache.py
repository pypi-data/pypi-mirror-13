""" Support Dogpile Cache in Muffin framework. """
import asyncio

from muffin.plugins import BasePlugin

from dogpile.cache.region import make_region

__version__ = "0.0.1"
__project__ = "muffin-dogpilecache"
__author__ = "Abner Campanha <abnerpc@gmail.com>"
__license__ = "MIT"

class Plugin(BasePlugin):

    """ Dogpile Cache Plugin. """

    name = 'dogpilecache'
    defaults = {
        'test': False,
        'configs': {
            'cache.local.backend': 'dogpile.cache.dbm',
            'cache.local.arguments.filename': './dbmfile.dbm',
        },
        'regions': {'default': 'cache.local.'}
    }

    def __init__(self, *args, **kwargs):
        """ Initialize the Plugin. """
        super().__init__(*args, **kwargs)

    def setup(self, app):
        """ Setup self. """
        super().setup(app)

        if self.cfg.test:
            self.cfg.configs = {'cache.test.backend': 'dogpile.cache.null'}
            for k in self.cfg.regions.keys():
                self.cfg.regions[k] = 'cache.test.'
        
        for k, v in self.cfg.regions.items():
            new_region = make_region()
            new_region.configure_from_config(self.cfg.configs, v)
            setattr(self, k, new_region)

    def start(self, app):
        """ Start plugin. """
        pass

    def finish(self, app):
        """ Finish plugin. """
        pass
