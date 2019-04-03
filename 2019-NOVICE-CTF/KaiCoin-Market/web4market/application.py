#!/usr/bin/env python3
# coding: utf-8

import string
from time import time
from random import sample
from functools import wraps
from base64 import urlsafe_b64decode, urlsafe_b64encode
from flask import Flask, request, url_for, session, redirect, render_template, \
    make_response, flash, abort
from flask.sessions import SecureCookieSessionInterface, SecureCookieSession, total_seconds, BadSignature
from captcha.image import ImageCaptcha
import pyaes


app = Flask(__name__)
app.config.from_pyfile('config.py')
import model


# Cookie encryption
class EncryptedCookieInterface(SecureCookieSessionInterface):
    def __init__(self, *args, **kwargs):
        super(SecureCookieSessionInterface, self).__init__(*args, **kwargs)
        secret_key = app.config.get('SECRET_KEY', '')
        if len(secret_key) >= 32:
            self.key = secret_key[:32].encode('utf-8')
        else:
            self.key = secret_key.zfill(32).encode('utf-8')
        
    def _encrypt(self, val):
        aes = pyaes.AESModeOfOperationCTR(self.key)
        data = aes.encrypt(val)
        return urlsafe_b64encode(data)

    def _decrypt(self, cipher):
        aes = pyaes.AESModeOfOperationCTR(self.key)
        data = urlsafe_b64decode(cipher)
        return aes.decrypt(data)

    def open_session(self, app, request):
        s = self.get_signing_serializer(app)
        if s is None:
            return None
        val = request.cookies.get(app.session_cookie_name)
        try:
            val = self._decrypt(val)
        except:
            val = None

        if not val:
            return self.session_class()
        max_age = total_seconds(app.permanent_session_lifetime)
        try:
            data = s.loads(val, max_age=max_age)
            return self.session_class(data)
        except BadSignature:
            return self.session_class()

    def save_session(self, app, session, response):
        domain = self.get_cookie_domain(app)
        path = self.get_cookie_path(app)

        if not session:
            if session.modified:
                response.delete_cookie(app.session_cookie_name,
                                       domain=domain, path=path)
            return

        if not self.should_set_cookie(app, session):
            return

        httponly = self.get_cookie_httponly(app)
        secure = self.get_cookie_secure(app)
        expires = self.get_expiration_time(app, session)
        val = self.get_signing_serializer(app).dumps(dict(session))
        val = self._encrypt(val)
        response.set_cookie(app.session_cookie_name, val,
                            expires=expires, httponly=httponly,
                            domain=domain, path=path, secure=secure)


app.session_interface = EncryptedCookieInterface()


@app.context_processor
def utility_processor():
    return dict(current_time=time)

def auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'uid' not in session:
            return redirect(url_for('login'))
        
        return f(*args, **kwargs)

    return decorated_function


@app.route('/')
@auth
def index():
    uid = session.get('uid')
    logged_user = session.get('username', 'NaN')
    m = model.Model()
    balance = m.get_user_balance(uid)
    offers = m.list_last_offers()
    trades = m.list_last_trades(uid)
    return render_template('index.html', logged_user=logged_user, balance=balance,
                           offers=offers, trades=trades)

@app.route('/offer', methods=['POST'])
@auth
def new_offer():
    uid = session.get('uid')

    captcha = request.form.get('captcha', '').strip()
    stored_captcha = session.get('captcha_text', None)
    session.pop('captcha_text', '')

    if stored_captcha is None or captcha.lower() != stored_captcha.lower():
        flash('验证码错误，请重试')
        return redirect(url_for('index'), 302)
    
    PREDEFINED_TYPE = (True, False)

    try:
        trade_type = int(request.form.get('trade_type', ''))
        sale_coin = PREDEFINED_TYPE[trade_type]
        trade_amount = float(request.form.get('trade_amount', ''))
        trade_rate = float(request.form.get('trade_rate', ''))
        if trade_rate < 0.0054 or trade_rate > 0.0059:
            raise ValueError('Rate out of range')
    except Exception:
        flash('输入数据不合法，请重新输入')
        return redirect(url_for('index'), 302)

    m = model.Model()
    ret = m.create_offer(uid, trade_amount, trade_rate, sale_coin)
    if ret is None:
        flash('账户余额不足，无法发布交易')
    
    else:
        flash('交易发布成功')
    
    return redirect(url_for('index'), 302)

@app.route('/offers/<int:id>', methods=["DELETE", "POST"])
@auth
def deal_with_offers(id):
    uid = session.get('uid')
    m = model.Model()
    offer_data = m.get_offer(id)
    if offer_data is None:
        abort(404)

    if request.method == 'POST':
        if int(offer_data['uid']) == int(uid):
            abort(404)
        
        ret = m.accept_offer(id, uid)
        if ret == -2:
            flash('非法交易！')
        elif ret == -1:
            flash('卖家或买家账户余额不足')
        else:
            flash('预交易成功，等待对方确认')
    else:
        if int(offer_data['uid']) != int(uid):
            abort(404)
        m.delete_offer(id, True)
    
    return 'OK'

@app.route('/trades/<int:id>', methods=["DELETE", "POST"])
@auth
def deal_with_trades(id):
    uid = session.get('uid')
    m = model.Model()
    trade_data = m.get_trade(id)
    if trade_data is None or int(trade_data['from_uid']) != int(uid):
        abort(404)

    if request.method == 'POST':
        ret = m.confirm_trade(id)
        if ret == -2:
            flash('非法交易！')
        elif ret == -1:
            flash('卖家或买家账户余额不足')
        else:
            flash('交易成功')
    else:
        m.delete_trade(id, True)
    
    return 'OK'

@app.route('/buy_flag')
@auth
def buy_flag():
    uid = session.get('uid')
    logged_user = session.get('username', 'NaN')
    m = model.Model()
    balance_data = m.get_user_balance(uid)
    if int(balance_data['money']) < 2000 or int(balance_data['coin']) < 2000:
        flash('账户至少需要 2000 RMB与 2000 KaiCoin才能进入商店')
        return redirect(url_for('index'), 302)
    
    m.change_user_balance(uid, -2000, -2000, True)
    return render_template('flag.html', logged_user=logged_user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    captcha = request.form.get('captcha', '').strip()

    if len(username) == 0 or len(password) == 0 or len(captcha) == 0:
        flash('信息不完整')
        return render_template('login.html', username=username)
    
    stored_captcha = session.get('captcha_text', None)
    session.pop('captcha_text', '')

    if stored_captcha is None or captcha.lower() != stored_captcha.lower():
        flash('验证码错误，请重试')
        return render_template('login.html', username=username)

    m = model.Model()
    ret = m.login(username, password)
    if ret is None:
        flash('用户名或密码错误')
        return render_template('login.html', username=username)

    session['uid'] = ret['uid']
    session['username'] = ret['username']
    return redirect(url_for('index'), 302)


@app.route('/logout')
def logout():
    session.pop('uid', None)
    return redirect(url_for('login'), 302)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    captcha = request.form.get('captcha', '').strip()

    if len(username) == 0 or len(password) == 0 or len(captcha) == 0:
        flash('信息不完整')
        return render_template('register.html', username=username)
    
    stored_captcha = session.get('captcha_text', None)
    session.pop('captcha_text', '')

    if stored_captcha is None or captcha.lower() != stored_captcha.lower():
        flash('验证码错误，请重试')
        return render_template('register.html', username=username)

    m = model.Model()
    ret = None
    try:
        ret = m.register(username, password)
    except model.IllegalUserInput:
        flash('用户名不合法')
    except model.EntryDulicateError:
        flash('用户名已存在')

    if ret is None:
        return render_template('register.html', username=username)


    m.set_user_balance(ret['uid'], 1, 0.0056, True)
    flash('首次登陆系统将赠送1元红包与0.0056个KaiCoin')

    session['uid'] = ret['uid']
    session['username'] = ret['username']
    return redirect(url_for('index'), 302)


@app.route('/captcha')
def captcha():
    img_captcha = ImageCaptcha()
    text = ''.join(sample(string.ascii_letters, 5))
    session['captcha_text'] = text
    img = img_captcha.generate(text)
    resp = make_response(img.read())
    resp.headers['Content-Type'] = 'image/png'

    return resp



if __name__ == '__main__':
    app.run(debug=True, threaded=True)
