# coding: utf-8

from os import path
from threading import Timer
from time import sleep
import json
from selenium import webdriver

class Chrome(object):
    def __init__(self, data_dir, timeout=8):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless') 
        options.add_argument("--enable-javascript")
        options.add_argument('--no-sandbox')
        # options.add_argument('--timeout=' + str(timeout * 1000))
        options.add_argument('--disable-gpu')
        options.add_argument('--user-data-dir=' + data_dir)

        self.status_file = path.join(data_dir, 'status.json')

        self.timeout = timeout
        self.driver = webdriver.Chrome(chrome_options=options)
        self.driver.set_page_load_timeout(timeout)
        self.driver.set_script_timeout(timeout)

    def add_cookie(self, cookie_dict):
        """
        Adds a cookie to your current session.

        :Args:
         - cookie_dict: A dictionary object, with required keys - "name" and "value";
            optional keys - "path", "domain", "secure", "expiry"

        Usage:
            driver.add_cookie({'name' : 'foo', 'value' : 'bar'})
            driver.add_cookie({'name' : 'foo', 'value' : 'bar', 'path' : '/'})
            driver.add_cookie({'name' : 'foo', 'value' : 'bar', 'path' : '/', 'secure':True})

        """
        try:
            self.driver.add_cookie(cookie_dict)
        except:
            pass

    def get(self, url):
        self.driver.get(url)

    def quit(self):
        self.save_status()
        self.driver.close()
        self.driver.quit()
        # self.driver.quit()

    def save_status(self):
        cookies = self.driver.get_cookies()
        local_storage = self.driver.execute_script("return Object.assign({}, localStorage)")
        # print('test', local_storage)
        with open(self.status_file, 'w') as f:
            json.dump({
                'cookies': cookies,
                'localStorage': local_storage
            }, f)

    def load_status(self):
        if not path.exists(self.status_file):
            return

        with open(self.status_file, 'r') as f:
            raw = f.read().strip()
            if len(raw) == 0:
                return

            data = json.loads(raw)
            
            self.driver.execute_script("Object.assign(localStorage, {})".format(json.dumps(data['localStorage'])))


def chrome_worker(uid, landing_page, cookie_domain, cookie_name, cookie_value, url):
    data_dir = path.join('/tmp', 'chrome-profile-' + str(uid))
    browser = Chrome(data_dir)

    browser.get(landing_page)
    browser.load_status()
    browser.add_cookie({
        'name': cookie_name,
        'value': cookie_value,
        'domain': cookie_domain,
    })

    t = Timer(browser.timeout, browser.quit)
    t.start()
    
    print(url)
    browser.get(url)
    sleep(2)
    # print(browser.driver.page_source)
    browser.quit()

    t.cancel()


def spawn_chrome(uid, landing_page, url, domain, app):
    try:
        chrome_worker(uid, landing_page, domain, app.session_cookie_name, app.secret_key, url)
        return None
    except Exception as e:
        print(e)
        return e