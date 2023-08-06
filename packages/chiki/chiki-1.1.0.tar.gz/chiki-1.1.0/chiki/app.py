# coding: utf-8
import os
import redis
import traceback
from flask import Blueprint, current_app, Response, render_template
from flask import abort, request, redirect
from flask.ext.babelex import Babel
from flask.ext.mail import Mail
from .jinja import init_jinja
from .logger import init_logger
from .oauth import init_oauth
from .settings import TEMPLATE_ROOT
from ._flask import Flask

__all__ = [
    "init_app", 'init_web', 'init_api', "init_admin", "start_error",
]


def init_babel(app):
    """ 初始化语言本地化 """

    babel = Babel(app)

    @babel.localeselector
    def get_locale():
        return 'zh_Hans_CN'


def init_redis(app):
    if app.config.get('REDIS'):
        conf = app.config.get('REDIS')
        app.redis = redis.StrictRedis(
            host=conf.get('host', '127.0.0.1'),
            port=conf.get('port', 6379),
            password=conf.get('password', ''),
            db=conf.get('db', 0),
        )


def init_error_handler(app):
    """ 错误处理 """

    @app.errorhandler(403)
    def error_403(error):
        return render_template('403.html'), 403

    @app.errorhandler(404)
    def error_404(error):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def error_500(error):
        return render_template('500.html'), 500


def before_request():
    """ Admin 权限验证 """

    auth = request.authorization
    username = current_app.config.get('ADMIN_USERNAME')
    password = current_app.config.get('ADMIN_PASSWORD')
    if username and not (auth 
            and auth.username == username 
            and auth.password == password):
        return Response(u'请登陆', 401, {'WWW-Authenticate': 'Basic realm="login"'})


def init_app(init=None, config=None, pyfile=None, 
        template_folder='templates', index=False, error=True):
    """ 创建应用 """

    app = Flask(__name__, template_folder=template_folder)
    if config: app.config.from_object(config)
    if pyfile: app.config.from_pyfile(pyfile)

    ENVVAR = app.config.get('ENVVAR')
    if ENVVAR and os.environ.get(ENVVAR): 
        app.config.from_envvar(app.config['ENVVAR'])

    app.static_folder = app.config.get('STATIC_FOLDER')
    app.mail = Mail(app)

    init_babel(app)
    init_redis(app)
    init_jinja(app)
    init_logger(app)
    init_oauth(app)

    if error:
        init_error_handler(app)
    
    if callable(init):
        init(app)

    if index:
        @app.route('/')
        def index():
            return redirect(app.config.get('INDEX_REDIRECT'))

    blueprint = Blueprint('chiki', __name__,
        template_folder=os.path.join(TEMPLATE_ROOT, 'chiki'))
    app.register_blueprint(blueprint)

    if os.environ.get('CHIKI_BACK') == 'true':
        @app.route('/chiki_back')
        def chiki_back():
            return 'true'

    return app


def init_web(init=None, config=None, pyfile=None, 
        template_folder='templates', index=False, error=True):
    app = init_app(init, config, pyfile, template_folder, index, error)
    app.is_web = True
    app.is_api = False
    return app


def init_api(init=None, config=None, pyfile=None, 
        template_folder='templates', index=False, error=False):
    app = init_app(init, config, pyfile, template_folder, index, error)
    app.is_web = False
    app.is_api = True
    return app


def init_admin(init=None, config=None, pyfile=None, 
        template_folder='templates', index=True, error=True):
    """ 创建后台管理应用 """

    app = init_app(init, config, pyfile, template_folder, index, error)

    @app.before_request
    def _before_request():
        return before_request()

    return app


def start_error(init=None, config=None):
    app = init_app(config=config)
    app.logger.error(traceback.format_exc())
    exit()
