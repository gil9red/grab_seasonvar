#!/usr/bin/python3
# -*- coding: utf-8 -*-


try:
    import urllib.request as urllib  # python3
except:
    import urllib2 as urllib  # python2

import json
import logging


class SeasonvarWebOpener:
    __web_opener = None

    @staticmethod
    def __get_opener():
        if SeasonvarWebOpener.__web_opener is None:
            web_opener = urllib.build_opener()
            web_opener.addheaders.append(('Cookie', 'sva=lVe324PqsI24'))
            urllib.install_opener(web_opener)
            SeasonvarWebOpener.__web_opener = web_opener

        return SeasonvarWebOpener.__web_opener

    @staticmethod
    def get_json(url):
        response = SeasonvarWebOpener.get_html(url)
        return json.loads(response)

    @staticmethod
    def get_html(url):
        try:
            conn = SeasonvarWebOpener.__get_opener().open(url)
            html = conn.read().decode('utf-8')
            conn.close()
            return html
        except:
            logging.exception('Error:')
            return None
