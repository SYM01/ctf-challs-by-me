# coding: utf-8

from hashlib import sha256
import pymysql
from application import app


class IllegalUserInput(Exception):
    pass


class EntryDulicateError(Exception):
    pass


class Model(object):
    USERNAME_MAXLEN = 128

    def __init__(self):
        self.conn = pymysql.connect(
            host=app.config.get('DB_HOST'),
            user=app.config.get('DB_USER'),
            password=app.config.get('DB_PASS'),
            db=app.config.get('DB_NAME'),
            charset='utf8mb4'
        )

    def _hash(self, username, password):
        return sha256('{}#{}'.format(username, password).encode('utf-8')).hexdigest()

    def login(self, username, password):
        u'''login(username, password) -> {uid, username} or None.'''
        username = username.strip()
        password = password.strip()

        with self.conn.cursor() as cur:
            cur.execute('select uid, username, password from users where '
                        'username=%s limit 1', (username,))
            row = cur.fetchone()

            if row is None:
                return None
        
        pass_hash = self._hash(username, password)

        if pass_hash != row[2]:
            return None

        return dict(uid=row[0], username=row[1])

    def register(self, username, password):
        username = username.strip()
        password = password.strip()

        if len(username) > self.USERNAME_MAXLEN:
            raise IllegalUserInput('Username: {}'.format(username))

        password_hash = self._hash(username, password)

        with self.conn.cursor() as cur:
            cur.execute('insert ignore into users(username, password) values(%s,%s)',
                        (username, password_hash))

            if cur.lastrowid is not None:
                return dict(uid=cur.lastrowid, username=username)
        
        raise EntryDulicateError('Username: {}'.format(username))

    def create_offer(self, uid, amount, rate, sale_coin=True):
        if sale_coin:
            offer_type = 'sale'
            amount_type = 'coin'
            offer_money = amount / rate
            offer_coin = amount

        else:
            offer_type = 'buy'
            amount_type = 'money'
            offer_money = amount
            offer_coin = amount * rate
        
        current_balance = self.get_user_balance(uid)
        if amount > current_balance[amount_type]:
            return None
        
        offer_id = None
        with self.conn.cursor() as cur:
            cur.execute('INSERT INTO offers (uid, money, coin, type) VALUES (%s, %s, %s, %s)',
                        (uid, offer_money, offer_coin, offer_type))
            
            offer_id = cur.lastrowid
        self.conn.commit()

        return offer_id

    def get_offer(self, offer_id):
        ret = None
        with self.conn.cursor() as cur:
            cur.execute('SELECT uid, money, coin, type FROM offers WHERE id=%s', (offer_id,))
            data = cur.fetchone()

            ret = {
                'uid': data[0],
                'money': data[1],
                'coin': data[2],
                'type': data[3]
            }

        return ret

    def list_last_offers(self):
        with self.conn.cursor() as cur:
            cur.execute('SELECT o.id, u.username, o.money, o.coin, o.type FROM offers AS o '
                        'LEFT JOIN users AS u ON u.uid=o.uid ORDER BY o.id DESC LIMIT 40')
            data = cur.fetchall()
        ret = [{'id': i[0], 'name': i[1], 'money': i[2], 'coin': i[3], 'type': i[4]} \
               for i in data]
        return ret
    
    def delete_offer(self, offer_id, commit=False):
        with self.conn.cursor() as cur:
            cur.execute('DELETE FROM offers WHERE id=%s', (offer_id,))
        
        if commit:
            return self.conn.commit()
            
    def accept_offer(self, offer_id, accepter_uid):
        '''
        accept_offer(self, offer_id, accepter_uid) -> -2, -1 or 0

        Returns:
            -2: illegal trade
            -1: balance problem
            0: done
        '''
        offer_data = self.get_offer(offer_id)
        if offer_data is None or int(accepter_uid) == int(offer_data['uid']):
            return -2
        
        # amount type from accepter
        if offer_data['type'] == 'sale':
            amount_type = 'money'
        else:
            amount_type = 'coin'

        balance_data = self.get_user_balance(accepter_uid)
        if balance_data[amount_type] < offer_data[amount_type]:
            return -1
            
        self.create_trade(offer_data, accepter_uid)
        return 0

    def create_trade(self, offer_data, accepter_uid):
        ret = None
        with self.conn.cursor() as cur:
            cur.execute('INSERT INTO pending_trades (from_uid, to_uid, money, coin, type)'
                        'VALUES (%s, %s, %s, %s, %s)', 
                        (offer_data['uid'], accepter_uid, offer_data['money'], offer_data['coin'], 
                         offer_data['type']))

            ret = cur.lastrowid
        
        self.conn.commit()
        return ret

    def get_trade(self, trade_id):
        ret = None
        with self.conn.cursor() as cur:
            cur.execute('SELECT id, from_uid, to_uid, money, coin, type FROM pending_trades WHERE id=%s', (trade_id,))
            data = cur.fetchone()
            ret = {
                'id': data[0],
                'from_uid': data[1],
                'to_uid': data[2],
                'money': data[3],
                'coin': data[4],
                'type': data[5]
            }
        return ret

    def delete_trade(self, trade_id, commit=False):
        with self.conn.cursor() as cur:
            cur.execute('DELETE FROM pending_trades WHERE id=%s', (trade_id,))
        
        if commit:
            return self.conn.commit()

    def confirm_trade(self, trade_id):
        '''
        confirm_trade(self, trade_id) -> -2, -1 or 0

        Returns:
            -2: illegal trade
            -1: balance problem
            0: done
        '''
        data = self.get_trade(trade_id)
        if data is None:
            return -2

        if data['type'] == 'sale':
            money_delta, coin_delta = data['money'], -data['coin']
            from_type, to_type = 'coin', 'money'
        else: # buy
            money_delta, coin_delta = -data['money'], data['coin']
            from_type, to_type = 'money', 'coin'

        self.conn.begin()
        try:
            from_blance = self.get_user_balance(data['from_uid'], True)
            to_blance = self.get_user_balance(data['to_uid'], True)

            if from_blance[from_type] < data[from_type] or \
               to_blance[to_type] < data[to_type]:
                self.conn.rollback()
                return -1

            self.change_user_balance(data['from_uid'], money_delta, coin_delta)
            self.change_user_balance(data['to_uid'], -money_delta, -coin_delta)
            self.delete_trade(trade_id)
            self.conn.commit()
            
            return 0
        except Exception:
            self.conn.rollback()
            raise

        return -2

    def list_last_trades(self, uid):
        with self.conn.cursor() as cur:
            cur.execute('SELECT o.id, u.username, o.money, o.coin, o.type FROM pending_trades AS o '
                        'LEFT JOIN users AS u ON u.uid=o.to_uid WHERE o.from_uid=%s '
                        'ORDER BY o.id DESC LIMIT 40', (uid,))
            data = cur.fetchall()
        ret = [{'id': i[0], 'name': i[1], 'money': i[2], 'coin': i[3], 'type': i[4]} \
               for i in data]
        return ret

    def get_user_balance(self, uid, lock=False):
        sql = 'SELECT money, coin FROM balance WHERE uid=%s'
        if lock:
            sql += ' FOR UPDATE'

        with self.conn.cursor() as cur:
            cur.execute(sql, (uid,))
            data = cur.fetchone()

            if data:
                return {
                    'money': data[0],
                    'coin': data[1]
                }
    
    def change_user_balance(self, uid, money_delta, coin_delta=0, commit=False):
        with self.conn.cursor() as cur:
            cur.execute('UPDATE balance SET money=money+%s, coin=coin+%s WHERE uid=%s',
                        (money_delta, coin_delta, uid))
        if commit:
            self.conn.commit()

    def set_user_balance(self, uid, money, coin, commit=False):
        with self.conn.cursor() as cur:
            cur.execute('INSERT INTO balance(uid, money, coin) VALUES (%s, %s, %s)'
                        'ON DUPLICATE KEY UPDATE money=%s, coin=%s',
                        (uid, money, coin, money, coin))

        if commit:
            self.conn.commit()
