#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re
from seasonvar_web_opener import *


class Serial:
    def __init__(self, url, id, name):
        self.__url = url
        self.__id = id
        self.__name = name

    def get_url(self):
        return self.__url

    def get_name(self):
        return self.__name

    def get_id(self):
        return self.__id

    def get_thumb(self):
        return 'http://cdn.seasonvar.ru/oblojka/' + self.__id + '.jpg'


class SeasonvarGrabber:
    __site = "http://seasonvar.ru"

    # TODO: rem
    # def __uniq_serials(self, serials):
    #     return to_return

    def get_main_page_data(self):
        html = SeasonvarWebOpener.get_html(self.__site)
        regexp = re.compile(
            r'film-list-item">.*?<a href="(\/serial-(.*?)-.*?)".*?>(.*?)<\/a>(.*?)<span>',
            re.DOTALL)
        data = regexp.findall(html)
        films = []
        ids_list = []

        for one_film in data:
            serial = Serial(self.__site + one_film[0], one_film[1], one_film[2] + one_film[3])

            if serial.get_id() not in ids_list:
                films.append(serial)
                ids_list.append(serial.get_id())

        return films
