from hashlib import sha1
import hmac
import json
import logging
import os

from authlib.flask.client import OAuth
from flask import Flask, abort, flash, make_response, redirect, request, render_template, session, url_for
from loginpass import create_flask_blueprint

OAUTH_BACKENDS = [ Twitter ]

# FIXME use a real cache
class Cache(object):
    def __init__(self):
        self._data = {}

    def get(self, k):
        return self._data.get(k)

    def set(self, k, v, timeout=None):
        self._data[k] = v

    def delete(self, k):
        if k in self._data:
            del self._data[k]

# Basic setup
app = Flask(__name__)
app.config.from_pyfile('config.py')
bootstrap = Bootstrap(app)
oauth = OAuth(app, Cache())

def handle_authorize(remote, token, user_info):
    app.logger.debug(user_info)
    user = game.wizard.lookup(sub=user_info['sub'],
                              username = user_info['preferred_username'])
    session['sub'] = user.sub
    where = session.get('destination')
    if where:
        del(session['destination'])
        return redirect(where)
    return redirect(url_for('index'))

def get_user():
    user = game.wizard.lookup(host=session.get('host'), sub=session.get('sub'))
    if user is None:
        session['destination'] = request.path
        abort(403) # Forbidden
    if not user.balance:
        return redirect(url_for('index'))
    return user

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def page_not_found(e):
    # note that we set the 404 status explicitly
    flash("404 page not found")
    return (render_template('result.html'), 404)

@app.errorhandler(403)
def permission_denied(e):
    return redirect(url_for('login'))

github_bp = create_flask_blueprint(GitHub, oauth, handle_authorize)
app.register_blueprint(github_bp, url_prefix='/github')
app.logger.setLevel(logging.DEBUG)
start_demo_db = False
if 'development' == app.config.get('ENV'):
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        # This is the process that will be killed and restarted.
        # Can't do anything here, so just wait for the end.
        time.sleep(3600)
    start_demo_db = True
app.logger.info("App %s started. Env is %s" % (__name__, app.config.get('ENV')))
app.logger.debug("Logging at DEBUG level.")
game = Game(applog=app.logger, start_demo_db=start_demo_db)
app.logger.debug("Game connected.")

if 'development' == app.config.get('ENV'):
    app.logger.info('''

##########################################################################
#                                                                        #
# Welcome to the local test environment.                                 #
#                                                                        #
##########################################################################
''')


# vim: autoindent textwidth=100 tabstop=4 shiftwidth=4 expandtab softtabstop=4 filetype=python
