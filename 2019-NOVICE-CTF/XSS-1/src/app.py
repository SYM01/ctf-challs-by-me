#!/usr/bin/env python3

from time import time
from uuid import uuid4
from flask import Flask, render_template, session, request, redirect, url_for, flash, abort
from geetest import GeetestLib
import pymysql.cursors
from driver import spawn_chrome


pc_geetest_id = "c3f2cca914cba0b17e2448907bd5d67b"
pc_geetest_key = "38644b462ea7667021c6917a8d0212d1"

app = Flask(__name__)
app.secret_key = 'flag{41064c3f5d42abbe4a8871cb08deb880}'

@app.route('/')
def index():
    user_id = session.get('user_id', None)
    if user_id is None:
        user_id = str(uuid4())
        session['user_id'] = user_id
    
    return redirect(url_for('.home', user_id=user_id))


@app.route('/<user_id>/')
def base_path(user_id):
    abort(404)
        

@app.route('/<user_id>/home/')
@app.route('/<user_id>/home/<path:dummy>')
def home(user_id, dummy=None):
    m = Model()
    data = m.get_list(user_id)
    return render_template('home.html', user_id=user_id, data=data)


@app.route('/<user_id>/new/', methods=['GET', 'POST'])
@app.route('/<user_id>/new/<path:dummy>', methods=['GET', 'POST'])
def new(user_id, dummy=None):
    if request.method != 'POST':
        return render_template('new-post.html', user_id=user_id)

    gt = GeetestLib(pc_geetest_id, pc_geetest_key)
    challenge = request.form[gt.FN_CHALLENGE]
    validate = request.form[gt.FN_VALIDATE]
    seccode = request.form[gt.FN_SECCODE]
    status = session.get(gt.GT_STATUS_SESSION_KEY, None)
    if status:
        success = gt.success_validate(challenge, validate, seccode, user_id)
        del session[gt.GT_STATUS_SESSION_KEY]
    else:
        success = False

    if not success:
        flash("验证失败")
        return render_template('new-post.html', user_id=user_id)

    title = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()
    if len(title) == 0 or len(content) == 0:
        flash("内容为空")
        return render_template('new-post.html', user_id=user_id)

    m = Model()
    m.save(user_id, title, content)
    return redirect(url_for('.home', user_id=user_id))


@app.route('/<user_id>/view/<aid>/')
@app.route('/<user_id>/view/<aid>/<path:dummy>')
def view(user_id, aid, dummy=None):
    m = Model()
    data = m.get(user_id, aid)
    if data is None:
        abort(404)
    
    return '<h1>{}</h1><p>{}</p>'.format(data['title'], data['content'])


@app.route('/<user_id>/submit/', methods=['GET', 'POST'])
@app.route('/<user_id>/submit/<path:dummy>', methods=['GET', 'POST'])
def submit(user_id, dummy=None):
    if request.method != 'POST':
        return render_template('submit.html', user_id=user_id)

    gt = GeetestLib(pc_geetest_id, pc_geetest_key)
    challenge = request.form[gt.FN_CHALLENGE]
    validate = request.form[gt.FN_VALIDATE]
    seccode = request.form[gt.FN_SECCODE]
    status = session.get(gt.GT_STATUS_SESSION_KEY, None)
    if status:
        success = gt.success_validate(challenge, validate, seccode, user_id)
        del session[gt.GT_STATUS_SESSION_KEY]
    else:
        success = False

    if not success:
        flash("验证失败")
        return render_template('submit.html', user_id=user_id)

    url = request.form.get('url', '').strip()
    if len(url) == 0:
        flash("内容为空")
        return render_template('submit.html', user_id=user_id)

    url_pattern = url_for('.base_path', user_id=user_id, _external=True)
    if not url.startswith(url_pattern):
        flash("URL必须以{}为开头".format(url_pattern))
        return render_template('submit.html', user_id=user_id)

    ret = spawn_chrome(user_id, url_pattern, url, request.headers['Host'], app)
    if ret is None:
        flash("Jumbo已经看过你提交的链接了.")
        return redirect(url_for('.home', user_id=user_id))
    
    app.logger.exception(ret)
    flash("Unexpected error occurred")
    return render_template('submit.html', user_id=user_id)


@app.route('/captcha/', methods=["POST"])
@app.route('/captcha/<path:dummy>', methods=["POST"])
def captcha(dummy=None):
    gt = GeetestLib(pc_geetest_id, pc_geetest_key)
    status = gt.pre_process(session.get('user_id', ''))
    session[gt.GT_STATUS_SESSION_KEY] = status
    response_str = gt.get_response_str()
    return response_str



class Model(object):
    def __init__(self):
        self.conn = pymysql.connect(
            host='127.0.0.1',
            user='xss',
            password='xss@360',
            db='xss',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor)

    def save(self, user_id, title, content):
        with self.conn.cursor() as cur:
            cur.execute("INSERT IGNORE INTO articles (uid, aid, title, content) VALUES (%s, %s, %s, %s)", (user_id, int(time()), title, content))
        
        self.conn.commit()
    
    def get_list(self, user_id):
        with self.conn.cursor() as cur:
            cur.execute("SELECT * FROM articles WHERE uid=%s ORDER BY aid DESC limit 100", (user_id,))
            return cur.fetchall()

    def get(self, user_id, aid):
        with self.conn.cursor() as cur:
            cur.execute("SELECT * FROM articles WHERE uid=%s AND aid=%s", (user_id, aid))
            return cur.fetchone()


if __name__ == '__main__':
    app.run(debug=True)
