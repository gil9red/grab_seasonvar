#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


import urllib.request as urllib  # python3
from urllib.request import urlopen
from urllib.parse import quote_plus, urljoin

import json
import logging

import re

# Регулярка для поиска последовательностей пробелов: от двух подряд и более
multi_space_pattern = re.compile(r'[ ]{2,}')


from lxml import etree


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
        rs = SeasonvarWebOpener.get_html(url)
        return json.loads(rs)

    @staticmethod
    def get_html(url):
        with SeasonvarWebOpener.__get_opener().open(url) as f:
            return f.read().decode('utf-8')


class Serial:
    """Класс, описывающий сериал."""

    def __init__(self, url, serial_id, name):
        self.url = url
        self.id = serial_id
        self.name = name
        self.__description = None
        self.__list_of_series = None
        self.__cover_image = None

        # Используется для получения списка серий
        self.__secure = None

        self._has_load_data = False

    def is_valid(self):
        """Возвращает true, если сериал можно посмотреть."""

        return self.__secure is not None

    @property
    def description(self):
        if self.__description is None:
            self.__load_data()

        return self.__description

    @property
    def list_of_series(self):
        if self.__list_of_series is None:
            # self.__secure нужен для получения списка серий и его можно получить
            # только на странице сериала
            if self.__secure is None:
                self.__load_data()

            self.__list_of_series = list()

            logging.debug('Выполнение запроса получения списка серий.')
            url_list_of_series = 'http://seasonvar.ru/playls2/' + self.__secure + 'x/trans/' + self.id + '/list.xml'
            rs = SeasonvarWebOpener.get_json(url_list_of_series)
            logging.debug('Результат:\n%s', rs)

            # TODO: а разве бывают в seasonvar вложенные плейлисты?
            # TODO: Обработать название серии в comment -- удалить указания вариантов качества видео SD/HD и т.п.
            # указание перевода можно оставить, но нужно его также оформить
            for row in rs['playlist']:
                if 'file' in row:
                    self.__list_of_series.append((row['comment'], row['file']))

                elif 'playlist' in row:
                    for row2 in row['playlist']:
                        self.__list_of_series.append((row2['comment'], row2['file']))

            logging.debug('Список серий:')
            for i, url in enumerate(self.__list_of_series, 1):
                logging.debug('%s. %s', i, url)

        return self.__list_of_series

    def get_cover_url(self):
        return 'http://cdn.seasonvar.ru/oblojka/' + self.id + '.jpg'

    def get_cover_image(self):
        if self.__cover_image is None:
            # Качаем обложку и сохраняем в переменную как base64
            with urlopen(self.get_cover_url()) as f:
                self.__cover_image = f.read()

        return self.__cover_image

    # TODO: выглядит костыльно
    def __load_data(self):
        """Функция парсит по указанному url и объект обновляет свои поля."""

        if self._has_load_data:
            return

        logging.debug('Запрос получения страницы по: %s', self.url)

        html = SeasonvarWebOpener.get_html(self.url)
        root = etree.HTML(html)

        # Если название сериала не указано, находим на странице. Дело в том, что название сериала из поиска
        # более хорошее, чем на странице. И данную функцию удобно вызывать после вызова поиска.
        if self.name is None:
            xpath = '//div[@class="full-news-title"]/h1[@class="hname"]/text()'
            match = root.xpath(xpath)
            if not match:
                logging.warning('Не удалось с помощью запроса "%s" получить название сериала.', xpath)
                return

            name = match[0]

            # Дополнительная обработка названия сериала.
            # Удаление последовательностей из двух и больше пробелов
            name = multi_space_pattern.sub(' ', name)

            # Удаление с начала строки "Сериал" и с конца "онлайн". Можно было заменой воспользоваться, но
            # есть опасение попасть на сериал, у которого окажутся такие же строки в названии
            name = name.strip()
            start, end = 'Сериал', 'онлайн'
            if name.startswith(start) and name.endswith(end):
                name = name[len(start): len(name) - len(end)]
                name = name.strip()

            self.name = name

        if self.__description is None:
            # Вытаскивание описания из страницы
            xpath = '//div[@class="full-news-title"]/following-sibling::p/text()'
            match = root.xpath(xpath)
            if not match:
                logging.warning('Не удалось с помощью запроса "%s" получить описание сериала.', xpath)
                logging.debug('Попытаемся получить заголовок из мета информации страницы.')

                # Попытаемся получить заголовок из мета информации страницы
                xpath = '//head/meta[@name="description"]/@content'
                match = root.xpath(xpath)
                if not match:
                    logging.warning('Не удалось с помощью запроса "%s" получить описание сериала.', xpath)
                    self.__description = '<not found>'
                    return

            description = match[0]

            # Удаление последовательностей из двух и больше пробелов
            description = multi_space_pattern.sub(' ', description)
            description = description.strip()
            self.__description = description

        # Вытаскивание secure, нужного для получения списка серий
        pattern = 'var id = "(.*)";[\s\S]*var serial_id = "(.*)";[\s\S]*var secureMark = "(.*)";'
        match = re.search(pattern, html, re.MULTILINE)
        if not match:
            # TODO: в этом случае скорее всего, присутствует какой-то запрет просмотра (например, по просьбе
            # правообладателя) и тогда лучше выбрасывать исключение и удалить данный объект
            logging.warning('Не удалось найти id, serial_id и secureMark. Url: %s', self.url)
            return

        _, _, self.__secure = match.groups()

        self._has_load_data = True

    def __repr__(self):
        return "<Serial(name='{}', url='{}', id='{}')>".format(self.name, self.url, self.id)


class NotFoundException(Exception):
    def __init__(self, mess):
        self.mess = mess

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return 'По запросу "{}" ничего не найдено.'.format(self.mess)


class SeasonvarApi:
    """Класс, позволяющий взаимодействовать с сайтом http://seasonvar.ru/"""

    SITE = "http://seasonvar.ru"

    @staticmethod
    def search(text):
        """Функция ищет сериалы на сайте и возвращает список объектов Serial."""

        logging.debug('Выполнение запроса поиска.')
        search_url = 'http://seasonvar.ru/autocomplete.php?query=' + quote_plus(text)
        rs = SeasonvarWebOpener.get_json(search_url)
        logging.debug('Rs:\n%s', rs)

        # data или пустой, или первый его элемент пустой
        if not rs['data'] or not rs['data'][0].strip():
            raise NotFoundException(text)

        serial_list = set()

        logging.debug('Результаты поиска:')
        for id, title, rel_url in zip(rs['id'], rs['suggestions'], rs['data']):
            # Поиск выдал не только сериалы, но и другие результаты: теги и/или актеры,
            # поэтому прерываем заполнение
            if title.startswith('<span'):
                logging.debug('Поиск содержит не только сериалы, прерываю заполнение.')
                break

            url = urljoin(SeasonvarApi.SITE, rel_url)
            logging.debug('%s: "%s": %s', id, title, url)

            serial = Serial(url, id, title)
            serial_list.add(serial)

        # Если список пуст
        if not serial_list:
            raise NotFoundException(text)

        return serial_list

    # @staticmethod
    # def get_serial(url):
    #     """Функция по указанному url возвращает объект Serial или выбрасывает исключение."""
    #
    #     return Serial.new_from_url(url)

    # TODO: post запрос http://seasonvar.ru/ajax.php?mode=pop
    @staticmethod
    def get_popular():
        """Функция возвращает список популярных сериалов."""

    # TODO: post запрос http://seasonvar.ru/ajax.php?mode=newest
    @staticmethod
    def get_newest():
        """Функция возвращает список новинок."""

    # TODO: post запрос http://seasonvar.ru/ajax.php?mode=new
    @staticmethod
    def get_new():
        """Функция возвращает список обновлений."""

    # TODO: post запрос http://seasonvar.ru/index.php
    @staticmethod
    def filter():
        """Функция фильтрует сериалы по указаннм категориям и возвращает список объектов Serial."""

        # TODO: пустой фильтр
        # filter[block]
        # filter[engName]
        # filter[hd]
        # filter[history]
        # filter[mark]
        # filter[nw]
        # filter[only]
        # filter[rait]	kp
        # filter[sub]

        # TODO: только русские
        # countFilter	yes
        # filter[block]
        # filter[engName]
        # filter[hd]
        # filter[history]
        # filter[mark]
        # filter[nw]
        # filter[only]	rus
        # filter[rait]	kp
        # filter[sub]

        # TODO: зарубежные
        # countFilter yes
        # filter[block]
        # filter[engName]
        # filter[hd]
        # filter[history]
        # filter[mark]
        # filter[nw]
        # filter[only] eng
        # filter[rait]  kp
        # filter[sub]

        # TODO: при фильтре "зарубежные" сначала возвращает с англоязычным названием (для все или
        # русские не включается на сайте)
        # filter[block]
        # filter[engName]	yes
        # filter[hd]
        # filter[history]
        # filter[mark]
        # filter[nw]
        # filter[only]	eng
        # filter[rait]	kp
        # filter[sub]

        # TODO: фильтр по жанру
        # filter[block]
        # filter[engName]	yes
        # filter[hd]
        # filter[history]
        # filter[mark]
        # filter[nw]
        # filter[only]	eng
        # filter[quotG][]	18
        # filter[rait]	kp
        # filter[sub]

        # TODO: фильтр по нескольким жанрам
        # filter[block]
        # filter[engName]
        # filter[hd]
        # filter[history]
        # filter[mark]
        # filter[nw]
        # filter[only]
        # filter[quotG][]	18
        # filter[quotG][]	17
        # filter[rait]	kp
        # filter[sub]

        # TODO: фильтр по нескольким жанрам, один из которых ищется как "не"
        # filter[block]
        # filter[engName]
        # filter[hd]
        # filter[history]
        # filter[mark]
        # filter[notQuotG][]	17
        # filter[quotG][]	18
        # filter[nw]
        # filter[only]
        # filter[rait]	kp
        # filter[sub]

        # TODO: фильтр по стране
        # filter[block]
        # filter[engName]
        # filter[hd]
        # filter[history]
        # filter[mark]
        # filter[nw]
        # filter[only]
        # filter[quotC][]	Великобритания
        # filter[rait]	kp
        # filter[sub]

        # TODO: фильтр "не" по стране
        # filter[block]
        # filter[engName]
        # filter[hd]
        # filter[history]
        # filter[mark]
        # filter[notQuotC][]	Австралия
        # filter[nw]
        # filter[only]
        # filter[rait]	kp
        # filter[sub]

        # TODO: фильтр по году (на сайте: 1914-2016). Варианты сравнениея:
        #    filter[quotY][] = равно
        #    filter[moreY][] = больше
        #    filter[underY][] = меньше
        #
        # filter[block]
        # filter[engName]
        # filter[hd]
        # filter[history]
        # filter[mark]
        # filter[nw]
        # filter[only]
        # filter[quotY][]	2013
        # filter[rait]	kp
        # filter[sub]

        # TODO: фильтр по количеству сезонов сериала (почему то для этого фильтра появился параметр countFilter):
        # равно  = filter[quotS][]
        # больше = filter[moreS][]
        # меньше = filter[underS][]
        #
        # countFilter=yes
        # filter[block]=
        # filter[engName]=
        # filter[hd]=
        # filter[history]=
        # filter[mark]=
        # filter[nw]=
        # filter[only]=
        # filter[quotS][]=1
        # filter[rait]=kp
        # filter[sub]=

        # TODO: рейтинг: filter[rait]=kp или filter[rait]=imdb
        # countFilter=yes
        # filter[block]=
        # filter[engName]=
        # filter[hd]=
        # filter[history]=
        # filter[mark]=
        # filter[nw]=
        # filter[only]=
        # filter[rait]=imdb
        # filter[sub]=
        # filter[underS][]=1

        # TODO: рейтинг с фильтром по баллам:
        # равно  = filter[quotR][]
        # больше = filter[moreR][]
        # меньше = filter[underR][]
        #
        # countFilter=yes
        # filter[block]=
        # filter[engName]=
        # filter[hd]=
        # filter[history]=
        # filter[mark]=
        # filter[nw]=
        # filter[only]=
        # filter[quotR][]=5
        # filter[rait]=imdb
        # filter[sub]=

        # TODO: перевод -- выбор Ancord
        # countFilter=yes
        # filter[block]=
        # filter[engName]=
        # filter[hd]=
        # filter[history]=
        # filter[mark]=
        # filter[nw]=
        # filter[only]=
        # filter[quotT][]=Ancord
        # filter[rait]=imdb
        # filter[sub]=
        # filter[underR][]=5
        #
        # перевод 2x2:
        # countFilter=yes
        # filter[block]=
        # filter[engName]=
        # filter[hd]=
        # filter[history]=
        # filter[mark]=
        # filter[nw]=
        # filter[only]=
        # filter[quotT][]=2x2
        # filter[rait]=kp
        # filter[sub]=

        # TODO: С субтитрами:
        # countFilter=yes
        # filter[block]=
        # filter[engName]=
        # filter[hd]=
        # filter[history]=
        # filter[mark]=
        # filter[nw]=
        # filter[only]=
        # filter[rait]=kp
        # filter[sub]=yes

        # TODO: сортировать по "названию"
        # filter[block]=
        # filter[engName]=
        # filter[hd]=
        # filter[history]=
        # filter[mark]=
        # filter[nw]=
        # filter[only]=
        # filter[rait]=kp
        # filter[sortTo][]=name
        # filter[sub]=

        # TODO: список видов сортировки:
        # <option selected="" value="all">нет</option>
        # <option value="name">названию</option>
        # <option value="kinopoisk">kinopoisk</option>
        # <option value="imdb">imdb</option>
        # <option value="god">году</option>
        # <option value="view">популярности</option>
        # <option value="newest">добавлению</option>

        # TODO: список переводов:
        # <option selected="" value="all">все</option>
        # <option value="1 канал">1 канал</option>
        # <option value="2x2">2x2</option>
        # <option value="AlexFilm">AlexFilm</option>
        # <option value="AltPro">AltPro</option>
        # <option value="Amedia">Amedia</option>
        # <option value="Ancord">Ancord</option>
        # <option value="AniDub">AniDub</option>
        # <option value="AniFilm">AniFilm</option>
        # <option value="AniLibria">AniLibria</option>
        # <option value="AniMedia">AniMedia</option>
        # <option value="AnimeReactor">AnimeReactor</option>
        # <option value="Axn SciFi">Axn SciFi</option>
        # <option value="BaibaKo">BaibaKo</option>
        # <option value="CBS Drama">CBS Drama</option>
        # <option value="Cuba77">Cuba77</option>
        # <option value="Disney">Disney</option>
        # <option value="Diva">Diva</option>
        # <option value="DIVA Universal">DIVA Universal</option>
        # <option value="DreamRecords">DreamRecords</option>
        # <option value="FiliZa">FiliZa</option>
        # <option value="FilmGate">FilmGate</option>
        # <option value="FOX">FOX</option>
        # <option value="Goblin">Goblin</option>
        # <option value="GraviTV">GraviTV</option>
        # <option value="GreenTea">GreenTea</option>
        # <option value="Hamster">Hamster</option>
        # <option value="Jetvis">Jetvis</option>
        # <option value="JimmyJ">JimmyJ</option>
        # <option value="Kansai">Kansai</option>
        # <option value="Kuraj-Bambey">Kuraj-Bambey</option>
        # <option value="LostFilm">LostFilm</option>
        # <option value="MTV">MTV</option>
        # <option value="NewStudio">NewStudio</option>
        # <option value="Nickelodeon">Nickelodeon</option>
        # <option value="novafilm">novafilm</option>
        # <option value="Ozz">Ozz</option>
        # <option value="Paramount">Paramount</option>
        # <option value="Persona99">Persona99</option>
        # <option value="RenTV">RenTV</option>
        # <option value="RG.Paravozik">RG.Paravozik</option>
        # <option value="Sci-Fi">Sci-Fi</option>
        # <option value="SDI Media">SDI Media</option>
        # <option value="seasonvar">seasonvar</option>
        # <option value="SET">SET</option>
        # <option value="Shachiburi">Shachiburi</option>
        # <option value="SHIZAProject">SHIZAProject</option>
        # <option value="Sony Sci-Fi">Sony Sci-Fi</option>
        # <option value="Sony Turbo">Sony Turbo</option>
        # <option value="STEPonee">STEPonee</option>
        # <option value="To4kaTV">To4kaTV</option>
        # <option value="turok1990">turok1990</option>
        # <option value="Universal">Universal</option>
        # <option value="ViruseProject">ViruseProject</option>
        # <option value="VO-production">VO-production</option>
        # <option value="Домашний">Домашний</option>
        # <option value="ДТВ">ДТВ</option>
        # <option value="кубик в кубе">кубик в кубе</option>
        # <option value="Невафильм">Невафильм</option>
        # <option value="НТВ">НТВ</option>
        # <option value="Оригинал">Оригинал</option>
        # <option value="СBS Drama">СBS Drama</option>
        # <option value="СТС">СТС</option>
        # <option value="Субтитры">Субтитры</option>
        # <option value="Сыендук">Сыендук</option>
        # <option value="ТВ3">ТВ3</option>
        # <option value="ТНТ">ТНТ</option>
        # <option value="Шадинский">Шадинский</option>

        # TODO: список баллов рейтинга
        # <option selected="" value="all">все</option>
        # <option value="0">0</option>
        # <option value="1">1</option>
        # <option value="2">2</option>
        # <option value="3">3</option>
        # <option value="4">4</option>
        # <option value="5">5</option>
        # <option value="6">6</option>
        # <option value="7">7</option>
        # <option value="8">8</option>
        # <option value="9">9</option>

        # TODO: список сезонов
        # <option selected="" value="all">все</option>
        # <option value="1">1</option>
        # <option value="2">2</option>
        # <option value="3">3</option>
        # <option value="4">4</option>
        # <option value="5">5</option>
        # <option value="6">6</option>
        # <option value="7">7</option>
        # <option value="8">8</option>
        # <option value="9">9</option>
        # <option value="10">10</option>

        # TODO: список жанров:
        # <option selected="" value="all">все</option>
        # <option value="19">Discovery&BBC</option>
        # <option value="1">анимационные</option>
        # <option value="18">аниме</option>
        # <option value="5">боевики</option>
        # <option value="6">детективы</option>
        # <option value="13">документальные</option>
        # <option value="8">драмы</option>
        # <option value="14">исторические</option>
        # <option value="17">комедия</option>
        # <option value="9">криминальные</option>
        # <option value="4">мелодрамы</option>
        # <option value="15">мистические</option>
        # <option value="10">отечественные</option>
        # <option value="11">приключения</option>
        # <option value="20">реалити-шоу</option>
        # <option value="12">семейные</option>
        # <option value="16">триллеры</option>
        # <option value="7">ужасы</option>
        # <option value="2">фантастические</option>
        # <option value="3">фэнтези</option>

        # TODO: список стран:
        # <option value="all">все</option>
        # <option value="Австралия">Австралия</option>
        # <option value="Австрия">Австрия</option>
        # <option value="Аргентина">Аргентина</option>
        # <option value="Беларусь">Беларусь</option>
        # <option value="Бельгия">Бельгия</option>
        # <option value="Болгария">Болгария</option>
        # <option value="Бразилия">Бразилия</option>
        # <option value="Великобритания">Великобритания</option>
        # <option value="Венгрия">Венгрия</option>
        # <option value="Венесуэла">Венесуэла</option>
        # <option value="Германия">Германия</option>
        # <option value="Голландия">Голландия</option>
        # <option value="Гонконг">Гонконг</option>
        # <option value="Греция">Греция</option>
        # <option value="Грузия">Грузия</option>
        # <option value="Дания">Дания</option>
        # <option value="Египет">Египет</option>
        # <option value="Израиль">Израиль</option>
        # <option value="Индия">Индия</option>
        # <option value="Иордания">Иордания</option>
        # <option value="Иран">Иран</option>
        # <option value="Ирландия">Ирландия</option>
        # <option value="Исландия">Исландия</option>
        # <option value="Испания">Испания</option>
        # <option value="Италия">Италия</option>
        # <option value="Казахстан">Казахстан</option>
        # <option value="Канада">Канада</option>
        # <option value="Катар">Катар</option>
        # <option value="Китай">Китай</option>
        # <option value="Колумбия">Колумбия</option>
        # <option value="Корея Южная">Корея Южная</option>
        # <option value="Кыргызстан">Кыргызстан</option>
        # <option value="Латвия">Латвия</option>
        # <option value="Ливан">Ливан</option>
        # <option value="Литва">Литва</option>
        # <option value="Люксембург">Люксембург</option>
        # <option value="Малайзия">Малайзия</option>
        # <option value="Марокко">Марокко</option>
        # <option value="Мексика">Мексика</option>
        # <option value="Нидерланды">Нидерланды</option>
        # <option value="Новая Зеландия">Новая Зеландия</option>
        # <option value="Норвегия">Норвегия</option>
        # <option value="Перу">Перу</option>
        # <option value="Польша">Польша</option>
        # <option value="Португалия">Португалия</option>
        # <option value="Россия">Россия</option>
        # <option value="Румыния">Румыния</option>
        # <option value="Сингапур">Сингапур</option>
        # <option value="Сирия">Сирия</option>
        # <option value="СССР">СССР</option>
        # <option value="Судан">Судан</option>
        # <option value="США">США</option>
        # <option value="Таиланд">Таиланд</option>
        # <option value="Тайвань">Тайвань</option>
        # <option value="Тайланд">Тайланд</option>
        # <option value="Турция">Турция</option>
        # <option value="Узбекистан">Узбекистан</option>
        # <option value="Украина">Украина</option>
        # <option value="Филиппины">Филиппины</option>
        # <option value="Финляндия">Финляндия</option>
        # <option value="Франция">Франция</option>
        # <option value="Хорватия">Хорватия</option>
        # <option value="Чехия">Чехия</option>
        # <option value="Чехословакия">Чехословакия</option>
        # <option value="Чили">Чили</option>
        # <option value="Швейцария">Швейцария</option>
        # <option value="Швеция">Швеция</option>
        # <option value="Эстония">Эстония</option>
        # <option value="ЮАР">ЮАР</option>
        # <option value="Япония">Япония</option>

        # TODO: мега фильтр: зарубежные, жанр комедия, старше 2005 года, рейтинг kp > 4
        # countFilter=yes
        # filter[block]=
        # filter[engName]=
        # filter[hd]=
        # filter[history]=
        # filter[mark]=
        # filter[moreR][]=4
        # filter[moreY][]=2005
        # filter[nw]=
        # filter[only]=eng
        # filter[quotC][]=Великобритания
        # filter[quotG][]=17
        # filter[rait]=kp
        # filter[sortTo][]=name
        # filter[sub]=

    # TODO: скорее не пригодится
    @staticmethod
    def get_main_page_serials():
        """Функция возвращает список сериалов, расположенных на главной странице."""

        # class SeasonvarGrabber:
        #     __site = "http://seasonvar.ru"
        #
        #     def get_main_page_data(self):
        #         html = SeasonvarWebOpener.get_html(self.__site)
        #         regexp = re.compile(
        #             r'film-list-item">.*?<a href="(\/serial-(.*?)-.*?)".*?>(.*?)<\/a>(.*?)<span>',
        #             re.DOTALL)
        #         data = regexp.findall(html)
        #         films = []
        #         ids_list = []
        #
        #         for one_film in data:
        #             serial = Serial(self.__site + one_film[0], one_film[1], one_film[2] + one_film[3])
        #
        #             if serial.get_id() not in ids_list:
        #                 films.append(serial)
        #                 ids_list.append(serial.get_id())
        #
        #         return films

    # TODO: поддержка тегов

    # TODO: поддержка просмотра рецензий
