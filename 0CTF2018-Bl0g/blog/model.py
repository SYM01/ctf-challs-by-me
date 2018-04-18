# coding: utf-8

import json
from time import time
from hashlib import sha256
from hmac import HMAC
import pymysql
from flask import current_app as app
from flask import g


class BlogModel(object):
    def __init__(self):
        self.conn = pymysql.connect(host=app.config['DB_HOST'],
                                    port=app.config['DB_PORT'],
                                    user=app.config['DB_USER'],
                                    password=app.config['DB_PASS'],
                                    database=app.config['DB_NAME'],
                                    charset=app.config.get('DB_CHARSET', 'utf8')
                                    )
        
    @classmethod
    def get_db(cls):
        db = getattr(g, '_blog_model', None)
        if db is None:
            db = g._blog_model = cls()

        return db

    def load_session(self, sid, max_age):
        with self.conn.cursor() as cur:
            cur.execute("SELECT expires, data FROM bl0g_sessions WHERE sid=%s", (sid,))
            data = cur.fetchone()

            if data is None:
                return None

            # expired
            if time() - int(data[0]) > max_age:
                return None

            return json.loads(data[1])

    def save_session(self, sid, expires, data):
        data_str = json.dumps(data)
        with self.conn.cursor() as cur:
            cur.execute("INSERT INTO bl0g_sessions (sid, expires, data) VALUES (%s, %s, %s) "
                        "ON DUPLICATE KEY UPDATE expires=%s, data=%s", 
                        (sid, expires, data_str, expires, data_str))
            
            self.conn.commit()

    def login(self, username, password, ip='0.0.0.0'):
        '''login(username, password) -> user_data or None.'''
        with self.conn.cursor() as cur:
            cur.execute("SELECT uid, username, password, INET_NTOA(last_ip) "
                        "FROM bl0g_users WHERE username=%s", (username,))
            row = cur.fetchone()
            if row is None or row[2] != self._gen_hash(password):
                return None
            
            cur.execute("UPDATE bl0g_users SET last_ip=INET_ATON(%s) WHERE uid=%s",
                        (ip, row[0]))
            self.conn.commit()
            return {
                'uid': int(row[0]),
                'username': row[1],
                'last_ip': row[3]
            }

    def regsiter(self, username, password):
        with self.conn.cursor() as cur:
            cur.execute("INSERT IGNORE INTO bl0g_users (username, password)"
                        "VALUES (%s, %s)", (username, self._gen_hash(password)))
            
            self.conn.commit()
            return cur.lastrowid

    def _gen_hash(self, password):
        return HMAC(app.secret_key.encode('utf-8'), 
                    password.encode('utf-8'), sha256).hexdigest()


    '''
    CREATE TABLE `bl0g_articles` (
        `aid` int(10) unsigned NOT NULL AUTO_INCREMENT,
        `uid` int(10) unsigned NOT NULL,
        `title` varchar(256) NOT NULL,
        `page_effect` varchar(45) NOT NULL,
        `content` text NOT NULL,
        PRIMARY KEY (`aid`),
        KEY `articles_uid_aid` (`uid`,`aid`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 |
    '''
    def count_article(self, uid):
        with self.conn.cursor() as cur:
            cur.execute("SELECT COUNT(1) FROM bl0g_articles WHERE uid=%s", (uid,))
            ret = cur.fetchone()
            return ret[0]

    def new_article(self, uid, title, content, page_effect):
        with self.conn.cursor() as cur:
            cur.execute("INSERT INTO bl0g_articles (uid, title, page_effect, content)"
                        "VALUES (%s, %s, %s, %s)", (uid, title, page_effect, content))
            self.conn.commit()
            return cur.lastrowid
        
    def get_article(self, aid):
        with self.conn.cursor() as cur:
            cur.execute("SELECT aid, uid, title, page_effect, content FROM bl0g_articles "
                        "WHERE aid=%s", (aid,))
            data = cur.fetchone()
            if not data:
                return None
            
            return {
                'aid': int(data[0]),
                'uid': int(data[1]),
                'title': data[2],
                'page_effect': data[3],
                'content': data[4]
            }
        
    def list_articles(self, uid, offset, limit=10):
        with self.conn.cursor() as cur:
            cur.execute("SELECT aid, title, page_effect, SUBSTR(content, 1, 128) FROM bl0g_articles "
                        "WHERE uid=%s ORDER BY aid DESC LIMIT %s, %s", (uid, offset, limit))
            data = cur.fetchall()
            ret = []
            for row in data:
                ret.append({
                    'aid': int(row[0]),
                    'title': row[1],
                    'page_effect': row[2],
                    'brief': row[3]
                })

            return ret

            
    '''
    CREATE TABLE `bl0g_comments` (
    `cid` int(10) unsigned NOT NULL AUTO_INCREMENT,
    `aid` int(10) unsigned NOT NULL,
    `uid` int(10) unsigned NOT NULL,
    `comment` text NOT NULL,
    PRIMARY KEY (`cid`),
    KEY `comments_aid_cid` (`aid`,`cid`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    '''
    def count_comments(self, aid):
        with self.conn.cursor() as cur:
            cur.execute("SELECT COUNT(1) FROM bl0g_comments WHERE aid=%s", (aid,))
            ret = cur.fetchone()
            return ret[0]

    def new_comment(self, aid, uid, comment):
        with self.conn.cursor() as cur:
            cur.execute("INSERT INTO bl0g_comments (aid, uid, comment)"
                        "VALUES (%s, %s, %s)", (aid, uid, comment))
            self.conn.commit()
            return cur.lastrowid
        
    def list_comments(self, aid, offset, limit=10):
        with self.conn.cursor() as cur:
            cur.execute("SELECT aid, uid, comment FROM bl0g_comments "
                        "WHERE aid=%s ORDER BY cid DESC LIMIT %s, %s", (aid, offset, limit))
            data = cur.fetchall()
            ret = []
            for row in data:
                ret.append({
                    'aid': int(row[0]),
                    'uid': int(row[1]),
                    'comment': row[2]
                })

            return ret