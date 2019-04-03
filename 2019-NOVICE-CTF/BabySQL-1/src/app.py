#!/usr/bin/env python3

from hashlib import md5
import pymysql.cursors
from flask import Flask, render_template, request, abort

app = Flask(__name__)

@app.template_filter('hash')
def hash_filter(s):
    return md5(s.encode('utf-8') + b'360#^)').hexdigest()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def slogan():
    _id = request.form.get('rand', '').strip()
    if len(_id) == 0:
        abort(404)

    data = {
        'id': _id,
        'text': get_slogan(_id)
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
        cur.execute("SELECT text FROM slogan WHERE id=%s" %_id)
        data = cur.fetchone()
        return data and data.get('text')


if __name__ == '__main__':
    app.run(debug=True)