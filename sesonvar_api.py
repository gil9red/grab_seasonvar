#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


class SeasonvarApi:
    """Класс, позволяющий взаимодействовать с сайтом http://seasonvar.ru/"""

    # TODO: добавить исключение.
    # TODO: добавить описание возвращаемых объектов и исключения.
    # TODO: поиск работает не только по сериалам, может вернуть и по актерам:
    # from seasonvar_web_opener import SeasonvarWebOpener
    # print(SeasonvarWebOpener.get_json('http://seasonvar.ru/autocomplete.php?query=%D0%BF%D0%B8%D0%B4%D0%B0'))
    def search(self, text):
        """Функция ищет сериалы на сайте и возвращает список объектов Serial, или выбрасывает исключение."""

    def get_serial(self, url):
        """Функция по указанному url возвращает объект Serial или выбрасывает исключение."""

    # TODO: post запрос http://seasonvar.ru/ajax.php?mode=pop
    def get_popular(self):
        """Функция возвращает список популярных сериалов."""

    # TODO: post запрос http://seasonvar.ru/ajax.php?mode=newest
    def get_newest(self):
        """Функция возвращает список новинок."""

    # TODO: post запрос http://seasonvar.ru/ajax.php?mode=new
    def get_new(self):
        """Функция возвращает список обновлений."""

    # TODO: post запрос http://seasonvar.ru/index.php
    def filter(self):
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
