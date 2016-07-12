#!/usr/bin/python3
# -*- coding: utf-8 -*-


import sys
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(filename)s[LINE:%(lineno)d] %(levelname)-8s %(message)s',
    handlers=[
        logging.FileHandler('log', encoding='utf8'),
        logging.StreamHandler(stream=sys.stdout),
    ],
)

# TODO: print заменить logging


if __name__ == '__main__':
    from sesonvar_api import *

    url = 'http://seasonvar.ru/serial-4574-Gravity_Falls.html'
    print(Serial.get_from_url(url))

    print(SeasonvarApi.search("Секретные материалы"))
    print(SeasonvarApi.search("Американский папаша"))
    print(SeasonvarApi.search("грэвети фоолс"))
