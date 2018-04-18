#!/usr/bin/env python3

from uuid import uuid4
from hashlib import sha1
from hmac import HMAC
from base64 import b64encode
from functools import wraps
from urllib.parse import urlparse, urljoin
import re

from flask import Flask, render_template, request, make_response, \
                  session, url_for, redirect, flash, abort
from .utils import DBSessionInterface, check_recaptcha
from .model import BlogModel
from .driver import spawn_chrome
from . import config

app = Flask(__name__, static_url_path='/assets')
app.config.from_object(config)
app.session_interface = DBSessionInterface()
app.session_cookie_name


def recaptcha_csp(func):
    @wraps(func)
    def _recaptcha_csp(*args, **kwargs):
        resp = make_response(func(*args, **kwargs))
        resp.headers['Content-Security-Policy'] = "default-src 'none'; script-src 'nonce-{}' 'strict-dynamic'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; media-src 'self'; font-src 'self' data:; connect-src 'self'; frame-src https://www.google.com/recaptcha/; base-uri 'none'".format(request.nonce)
        
        return resp
    return _recaptcha_csp


@app.errorhandler(404)
@app.errorhandler(500)
def page_not_found(e):
    return render_template('error.html', err=e), getattr(e, 'code', 500)

@app.before_request
def prepare():
    request.nonce = b64encode(HMAC(app.secret_key.encode('utf-8'), uuid4().bytes, sha1).digest()).decode('utf-8')


@app.after_request
def sec_enhance(resp):
    csp = resp.headers.get('Content-Security-Policy', None)
    if csp is None:
        resp.headers.add('Content-Security-Policy', "script-src 'self' 'unsafe-inline'")
        resp.headers.add('Content-Security-Policy', "default-src 'none'; script-src 'nonce-{}' 'strict-dynamic'; style-src 'self'; img-src 'self' data:; media-src 'self'; font-src 'self' data:; connect-src 'self'; base-uri 'none'".format(request.nonce))

    resp.headers['Server'] = "0Server/0.9"
    return resp


@app.route('/')
def home():
    if 'uid' not in session:
        return redirect(url_for('.login', next=request.path))

    page = request.args.get('p', 1)
    page = int(page)
    if page <= 0:
        return abort(404)

    db = BlogModel.get_db()
    total_articles = db.count_article(session['uid'])
    page_limit = app.config['MAX_ITEMS_IN_PAGE']
    max_page = (total_articles - 1) // page_limit + 1

    if max_page > 0 and page > max_page:
        return abort(404)
    
    offset = page_limit * (page - 1)
    articles = db.list_articles(session['uid'], offset, page_limit)

    return render_template('articles_list.html', articles=articles, page=page, max_page=max_page)


P_LEGAL_CONTENT = re.compile(r'^[a-zA-Z\,\.\s]+$')
@app.route('/new', methods=['GET', 'POST'])
def new_article():
    if 'uid' not in session:
        return redirect(url_for('.login', next=request.path))

    title = request.form.get('title', '').strip()[:256]
    content = request.form.get('content', '').strip()
    page_effect = request.form.get('effect', '').strip()[:70]

    if request.method == 'POST':
        db = BlogModel.get_db()

        if len(title) == 0 or len(content) == 0 or len(page_effect) == 0:
            flash("Information incomplete!")
        elif P_LEGAL_CONTENT.match(title) is None or P_LEGAL_CONTENT.match(content) is None:
            flash("Illegal char(s) in Title or Content!")
        elif not db.new_article(session['uid'], title, content, page_effect):
            flash("Unable to create new article.")
        else:
            flash("The new article has been created.")
            return redirect(url_for(".home"))

    return render_template("new.html", title=title, content=content, page_effect=page_effect)


@app.route("/article/<int:id>", methods=['GET', 'POST'])
def article(id):
    if 'uid' not in session:
        return redirect(url_for('.login', next=request.path))
        
    db = BlogModel.get_db()
    data = db.get_article(id)
    if not data:
        return abort(404)
    
    uid = int(session['uid'])
    if uid != 0 and uid != data['uid']:
        return abort(404)

    if request.method == 'POST':
        comment = request.form.get('comment', '').strip()
        if len(comment) == 0:
            flash("Comment MUST NOT be empty.")
        elif not db.new_comment(id, uid, comment):
            flash("Unable to create new comment.")
        else:
            flash("The new comment has been created.")

    page = request.args.get('p', 1)
    page = int(page)

    total_comments = db.count_comments(id)
    page_limit = app.config['MAX_ITEMS_IN_PAGE']
    max_page = (total_comments - 1) // page_limit + 1
    
    offset = page_limit * (page - 1)
    comments = db.list_comments(id, offset, page_limit)
    for item in comments:
        if item['uid'] == 0:
            item['username'] = 'admin'
        elif item['uid'] == uid:
            item['username'] = 'YOU'

    return render_template('article.html', data=data, comments=comments, page=page, max_page=max_page)


@app.route("/submit", methods=['GET', 'POST'])
@recaptcha_csp
def submit():
    if 'uid' not in session:
        return redirect(url_for('.login', next=request.path))

    if request.method == 'POST':
        url = request.form.get('url', '').strip()
        recaptcha = request.form.get('g-recaptcha-response', '').strip()
        if len(url) == 0 or not url.startswith(request.url_root):
            flash("The URL is illegal!")
        elif len(recaptcha) == 0:
            flash("Missing reCAPTCHA token!")
        elif not check_recaptcha(app, recaptcha):
            flash("U r a robot?")
        else:
            o = urlparse(request.url_root)
            landing_page = urljoin(request.url_root, url_for('static', filename='js/config.js'))
            ret = spawn_chrome(session['uid'], landing_page, 
                               url, request.headers['Host'], app)
            if ret is None:
                flash("The admin(No.{}) had checked your url.".format(str(session['uid'])))
                return redirect(url_for('.home'))
            
            flash("Unexpected error occurred")
            # flash("Unexpected error occurred: {}.".format(str(ret)))

    return render_template('submit.html')


@app.route('/flag')
def flag():
    if 'uid' not in session:
        return redirect(url_for('.login', next=request.path))
    
    uid = int(session['uid'])
    if uid == 0:
        return app.secret_key
    
    return 'flag{ONLY_4dmin_can_r3ad_7h!s}'


P_LEGAL_NEXT_URL = re.compile(r'^(/$|/[a-z]+)')
@app.route("/login", methods=['GET', 'POST'])
@recaptcha_csp
def login():
    next_url = request.args.get('next', url_for('.home'))
    if next_url == url_for(".login"):
        next_url = url_for(".home")

    # restirct redirect domain
    mo = P_LEGAL_NEXT_URL.match(next_url)
    if not mo:
        next_url = url_for(".home")

    if 'uid' in session:
        return redirect(next_url)

    if request.method == 'POST':
        username = request.form.get('username', '').strip()[:45]
        password = request.form.get('password', '').strip()
        recaptcha = request.form.get('g-recaptcha-response', '').strip()
        if len(username) == 0 or len(password) == 0:
            flash("Login information is incomplete!")
        elif len(recaptcha) == 0:
            flash("Missing reCAPTCHA token!")
        elif not check_recaptcha(app, recaptcha):
            flash("U r a robot?")
        else:
            db = BlogModel()
            user_data = db.login(username, password, request.remote_addr)
            if user_data is not None:
                session.update(user_data)
                return redirect(next_url)
            
            flash("Unable to log in using current information.")

    return render_template('login.html')

@app.route("/logout")
def logout():
    if 'uid' in session:
        session.pop('uid')
    return redirect(url_for(".login"))


@app.route("/register", methods=['GET', 'POST'])
@recaptcha_csp
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()[:45]
        password = request.form.get('password', '').strip()
        password2 = request.form.get('password2', '').strip()
        recaptcha = request.form.get('g-recaptcha-response', '').strip()
        if len(username) == 0 or len(password) == 0:
            flash("Register information is incomplete!")
        elif len(recaptcha) == 0:
            flash("Missing reCAPTCHA token!")
        elif password != password2:
            flash("Password mismatch!")
        elif not check_recaptcha(app, recaptcha):
            flash("U r a robot?")
        else:
            db = BlogModel()
            uid = db.regsiter(username, password)
            if uid is not None and uid > 0:
                flash("Your registration has been successful.")
                return redirect(url_for('.login'))

            flash("Username exists, plz try another one.")

    return render_template('register.html')
