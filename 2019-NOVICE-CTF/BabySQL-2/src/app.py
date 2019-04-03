#!/usr/bin/env python3

from time import time, sleep
from functools import wraps
from hashlib import md5
from random import randint
import pymysql.cursors
from flask import Flask, render_template, request, abort, Response
# import ZODB

app = Flask(__name__)

@app.template_filter('hash')
def hash_filter(s):
    return md5(s.encode('utf-8') + b'360#^)').hexdigest()


def control_rate(f):
    @wraps(f)
    def foo(*args, **kwargs):
        ip = request.remote_addr
        # try:
        #     db = ZODB.DB('/tmp/rate_control.fs')
        #     with db.transaction() as conn:
        #         root = conn.root()
        #         last_visit = root.get(ip, 0)
        #         print(last_visit)
        #         root[ip] = time()
        # finally:
        #     db.close()
        
        for k in request.values:
            v = request.values.get(k).lower()
            if v.find('and') > -1 or v.find('&&') > -1 or v.find('or') > -1 or v.find('||') > -1:
                sleep(randint(1, 4))

            if v.find('sleep') > -1:
                sleep(randint(5, 10))

        # if last_visit > time() - 1:
        #     abort(Response('频率太快啦~\(≧▽≦)/~啦啦啦'))
        
        return f(*args, **kwargs)

    return foo


@app.route('/')
@control_rate
def index():
    return render_template('index.html')


@app.route('/', methods=['POST'])
@control_rate
def slogan():
    _id = request.form.get('rand', '').strip()[:50]
    if len(_id) == 0:
        abort(404)

    try:
        text = get_slogan(_id)
    except (pymysql.err.ProgrammingError, pymysql.err.InternalError) as e:
        text = str(e)
    data = {
        'id': _id,
        'text': text
    }

    return render_template('slogan.html', data=data)


def get_slogan(_id):
    connection = pymysql.connect(
        host='127.0.0.1',
        user='baby',
        password='baby@360',
        db='baby',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor)

    with connection.cursor() as cur:
        cur.execute("SELECT text %s FROM slogan WHERE id='%s'" %(',1'*randint(0,100), _id))
        data = cur.fetchone()

        return data and data.get('text')


if __name__ == '__main__':
    app.run(debug=True)