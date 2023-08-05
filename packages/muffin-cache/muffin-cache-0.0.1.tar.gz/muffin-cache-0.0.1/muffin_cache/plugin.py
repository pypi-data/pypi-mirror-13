""" Support cache in Muffin framework. """

import asyncio

from muffin.plugins import BasePlugin
from muffin_redis import Plugin as RPlugin


class Plugin(BasePlugin):

    """ Cache Plugin. """

    name = 'cache'
    defaults = {
        'lifetime': 60 * 30
    }
    dependencies = {'redis': RPlugin}

    def __init__(self, *args, **kwargs):
        """ Initialize the Plugin. """
        super().__init__(*args, **kwargs)

    def setup(self, app):
        """ Setup self. """
        super().setup(app)

    @asyncio.coroutine
    def start(self, app):
        """ Start plugin. """
        pass

    def finish(self, app):
        """ Finish plugin. """
        pass
