__version__ = '0.1.5'


from flask import Blueprint


class SynplaNVD3(object):
    """NVD3 JS functionality for SynPla."""

    def __init__(self, app=None):
        self.app = app

        if self.app:
            self.init_app(self.app)

    def init_app(self, app):
        """ Configures synpla-nvd3."""

        blueprint = Blueprint(
            'nvd3',
            __name__,
            static_folder='static',
            static_url_path=app.static_url_path + '/nvd3')

        app.register_blueprint(blueprint)
