# coding: utf-8


from hashlib import sha512
from datetime import datetime, timezone
from time import time
from base64 import urlsafe_b64encode
from os import urandom
import requests
from flask.sessions import SessionInterface, SecureCookieSession
from flask.helpers import total_seconds
from .model import BlogModel


class DBSession(SecureCookieSession):
    pass


class DBSessionInterface(SessionInterface):
    session_class = DBSession

    def gen_sid(self, app):
        raw_sid = str(time()).encode('ascii') + urandom(16) + app.secret_key.encode('utf-8')

        return urlsafe_b64encode(sha512(raw_sid).digest()[:63]).decode('ascii')

    def open_session(self, app, request):
        db = BlogModel.get_db()
        sid = request.cookies.get(app.session_cookie_name)
        if not sid:
            return self.session_class({'sid': self.gen_sid(app)})
        
        if sid == app.secret_key:
            # admin
            return self.session_class({
                'sid': self.gen_sid(app),
                'uid': 0,
                'username': 'admin'
            })
        
        max_age = total_seconds(app.permanent_session_lifetime)
        data = db.load_session(sid, max_age)
        if data is None:
            return self.session_class({'sid': self.gen_sid(app)})
        return self.session_class(data)

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

        db_expires = expires
        if db_expires is None:
            db_expires = datetime.utcnow() + app.permanent_session_lifetime

        db = BlogModel.get_db()
        db.save_session(session['sid'], 
                        db_expires.replace(tzinfo=timezone.utc).timestamp(), 
                        dict(session))
            
        response.set_cookie(app.session_cookie_name, session['sid'],
                            expires=expires, httponly=httponly,
                            domain=domain, path=path, secure=secure)



def check_recaptcha(app, resp):
    data = {
        'secret': app.config['CAPTCHA_SECRET_KEY'],
        'response': resp
    }

    # avoid gfw
    url = 'https://sym01.ws/recaptcha/api/siteverify'
    try:
        r = requests.post(url, data=data)
        ret = r.json()
        return ret['success']
    except:
        return False
