from hashlib import sha1
import hmac
import json
import logging
import os

from authlib.flask.client import OAuth
from flask import Flask, abort, flash, make_response, redirect, request, render_template, session, url_for
from loginpass import create_flask_blueprint, Twitter

from game import Game

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

#
# Headline pages for users
#

@app.route('/')
def index():
    wizard = game.wizard.lookup(sub=session.get('sub'))
    return render_template('index.html', wizard=wizard, user=wizard) # FIXME wizards are no mere users

@app.route('/add-spell')
def add_spell():
    spell = game.spell.lookup(url=request.args.get('url'))
    wizard = game.wizard.lookup(sub=session.get('sub'))
    if wizard:
        if wizard.add_spell(spell):
            flash("You have gained the new spell: %s!" % spell.name)
        else:
            flash("The spell %s was known to you of old, O mighty wizard!" % spell.name)
    else:
        spell_urls = session.get('spell_urls','').split(' ')
        spell_urls.append(spell.url)
        session['spell_urls'] = ' '.join(spell_urls)
        flash("Please log in, O mighty wizard.")
    return redirect(url_for('index'))

#
# Miscelleneous user-visible stuff
#

@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.ico')

@app.route('/privacy')
def privacy():
    user = game.wizard.lookup(sub=session.get('sub'))
    return render_template('privacy.html', user=user)

@app.route('/tos')
def tos():
    user = game.wizard.lookup(sub=session.get('sub'))
    return render_template('tos.html', user=user)

@app.route('/login')
def login():
    if 'development' == app.config.get('ENV'):
        if 'http://localhost:5000/' != request.url_root:
            return redirect('http://localhost:5000/login')
        session['sub'] = -1
        game.wizard.lookup(sub=-1, username='_test')
        return redirect(url_for('index'))
    else:
        return redirect('/twitter/login')

@app.route('/logout')
def logout():
    [session.pop(key) for key in list(session.keys())]
    app.logger.debug (session)
    flash("You have been logged out.")
    return redirect(url_for('index'))

def page_not_found(e):
    # note that we set the 404 status explicitly
    flash("404 page not found")
    return (render_template('result.html'), 404)

@app.errorhandler(403)
def permission_denied(e):
    return redirect(url_for('login'))

@app.route('/webhook', methods=['POST'])
def webhook():
    app.logger.debug('Headers: %s', request.headers)
    app.logger.debug('Body: %s', request.get_data()) 
    return 'OK'


twitter_bp = create_flask_blueprint(Twitter, oauth, handle_authorize)
app.register_blueprint(twitter_bp, url_prefix='/twitter')
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
