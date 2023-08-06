from flask import Blueprint
from .jinja_globals import render_field, csrf_setup
from .filters import timesince, percent_escape
from .overrides import FlaskView
class Boilerplate(object):

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):

        self.app = app

        app.config.setdefault('CSRF_ENABLED', True)
        app.config.setdefault('SENTRY_ENABLED', False)
        app.config.setdefault('BEHIND_REVERSE_PROXY', False)
        app.config.setdefault('REDIS_SESSIONS_ENABLED', False)
        app.config.setdefault('REDIS_SESSIONS_DB', 1)
        app.config.setdefault('REDIS_SESSIONS_HOST', '127.0.0.1')
        app.config.setdefault('REDIS_SESSIONS_PORT', 6379)
        app.config.setdefault('REDIS_SESSIONS_PICKLE_PROTO', 3)
        app.config.setdefault('BABEL_ENABLED', False)

        

        bp = Blueprint('boilerplate', __name__, template_folder='templates')
        self.app.register_blueprint(bp)

        # Inject various globals into jinja
        app.jinja_env.globals['csrf_setup'] = csrf_setup
        app.jinja_env.globals['render_field'] = render_field
        app.jinja_env.filters['percent_escape'] = percent_escape
        app.jinja_env.filters['time_since'] = timesince


        if app.config.get('CSRF_ENABLED'):
            from flask_wtf.csrf import CsrfProtect
            app.csrf = CsrfProtect(app)


        if app.config.get('BEHIND_REVERSE_PROXY'):
            from .ReverseProxied import ReverseProxied
            app.wsgi_app = ReverseProxied(app.wsgi_app)


        if app.config.get('SENTRY_ENABLED') and not app.debug:
            from raven.contrib.flask import Sentry
            app.sentry = Sentry(app)

        if app.config.get('REDIS_SESSIONS_ENABLED'):
            from .RedisSessionInterface import RedisSessionInterface
            from redis import Redis


            redis = Redis(
                host=app.config.get('REDIS_SESSIONS_HOST'),
                port=app.config.get('REDIS_SESSIONS_PORT'),
                db=app.config.get('REDIS_SESSIONS_DB')
            )
            app.session_interface = RedisSessionInterface(
                redis=redis, 
                pickle_protocol=app.config.get('REDIS_SESSIONS_PICKLE_PROTO')
            )

        if app.config.get('BABEL_ENABLED'):
            from flask.ext.babel import Babel
            from .filters import local_date, local_date_time
            app.babel = Babel(app)
            app.jinja_env.filters['local_date'] = local_date
            app.jinja_env.filters['local_date_time'] = local_date_time

        return True
