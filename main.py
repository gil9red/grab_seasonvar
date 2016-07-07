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

from seasonvar_grabber import *

from urllib.parse import quote_plus
import json


SITE = "http://seasonvar.ru"


# import sys
# import xbmcgui
# import xbmcplugin
#
#
# def add_dir(url, name, iconImage, mode):
#     u = (sys.argv[0] +
#          "?url=" + urllib.quote_plus(url) +
#          "&mode=" + str(mode) +
#          "&name=" + urllib.quote_plus(name))
#     ok = True
#     liz = xbmcgui.ListItem(name, iconImage=iconImage)
#     liz.setInfo(type="Video", infoLabels={"Title": name})
#     ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
#                                      url=u, listitem=liz, isFolder=True)
#     return ok
#
#
# def get_keyboard(default="", heading="", hidden=False):
#     keyboard = xbmc.Keyboard(default, heading, hidden)
#     keyboard.doModal()
#     if (keyboard.isConfirmed()):
#         return unicode(keyboard.getText(), "utf-8")
#     return default


# def index(page, name):
#     html = SeasonvarWebOpener.get_html(page)
#     elem = re.findall('id": "(.*)", "serial": "(.*)" , "type": "html5", "secure": "(.*)"', html)[0]
#     id = elem[0]
#     secure = elem[2]
#     print_playlist(id, secure, name)

def index(serial_url):
    # TODO: не забыть убрать

    # html = SeasonvarWebOpener.get_html(serial_url)
    import os
    if os.path.exists('html.html'):
        html = open('html.html', 'r', encoding='utf-8').read()
    else:
        html = SeasonvarWebOpener.get_html(serial_url)
        open('html.html', 'w', encoding='utf-8').write(html)

    print(html)

    if html:
        pattern = 'var id = "(.*)";[\s\S]*var serial_id = "(.*)";[\s\S]*var secureMark = "(.*)";'
        match = re.search(pattern, html, re.MULTILINE)
        if not match:
            print('Не удалось найти id, serial_id и secureMark')
            quit()

        id, _, secure = match.groups()
        print_playlist(id, secure)


def print_playlist(id, secure):
    url = 'http://seasonvar.ru/playls2/' + secure + 'x/trans/' + id + '/list.xml'
    rs = SeasonvarWebOpener.get_json(url)
    print(rs)
    files = get_file_links(rs)

    for i, url in enumerate(files, 1):
        # add_downLink(name + " " + str(i), one_file, 2)
        print(i, url)


def get_file_links(json_response):
    files = []

    # TODO: а разве бывают в seasonvar вложенные плейлисты?
    for row in json_response['playlist']:
        if 'file' in row:
            files.append(row['file'])

        elif 'playlist' in row:
            for row2 in row['playlist']:
                files.append(row2['file'])

    return files


# def add_downLink(name, url, mode):
#     u = (sys.argv[0] +
#          "?url=" + urllib.quote_plus(url) +
#          "&mode=" + str(mode) +
#          "&name=" + urllib.quote_plus(name))
#     ok = True
#     liz = xbmcgui.ListItem(name, iconImage="icon.png")
#     liz.setInfo(type="Video", infoLabels={"Title": name})
#     ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
#                                      url=u, listitem=liz, isFolder=False)
#     return ok


# def play(url, name):
#     listitem = xbmcgui.ListItem(name)
#     listitem.setInfo('video', {'Title': name})
#     xbmc.Player().play(url, listitem)
#
#
# def get_params():
#     param = []
#     paramstring = sys.argv[2]
#     if len(paramstring) >= 2:
#         params = sys.argv[2]
#         cleanedparams = params.replace('?', '')
#         if (params[len(params) - 1] == '/'):
#             params = params[0:len(params) - 2]
#         pairsofparams = cleanedparams.split('&')
#         param = {}
#         for i in range(len(pairsofparams)):
#             splitparams = {}
#             splitparams = pairsofparams[i].split('=')
#             if (len(splitparams)) == 2:
#                 param[splitparams[0]] = splitparams[1]
#     return param


def search(search_title):
    # vq = get_keyboard(heading="Enter the query")
    # vq = vq.encode('utf-8')
    search_url = 'http://seasonvar.ru/autocomplete.php?query=' + quote_plus(search_title)
    rs = SeasonvarWebOpener.get_json(search_url)
    print(rs)

    # {'suggestions': ['ничего не найдено'], 'query': 'наруто блич', 'data': ['']}
    #
    # {
    #     'suggestions': [
    #         'Притяжению вопреки / Defying Gravity (1 сезон)',
    #         'Гравитация / Gravity (1 сезон)',
    #         'Грэвити Фоллс / Gravity Falls (1 сезон)',
    #         'Грэвити Фоллс / Gravity Falls (2 сезон)'
    #     ],
    #     'id': [
    #         '332',
    #         '1099',
    #         '4574',
    #         '10050'
    #     ],
    #     'query': 'gravity',
    #     'data': [
    #         'serial-332-Prityazheniyu_vopreki-1-season.html',
    #         'serial-1099-Gravitatciya-1-season.html',
    #         'serial-4574-Gravity_Falls.html',
    #         'serial-10050-Greviti_Folls-2-season.html'
    #     ]
    # }

    # data или пустой, или первый его элемент пустой
    if not rs['data'] or not rs['data'][0].strip():
        print('По запросу "{}" ничего не найдено.'.format(search_title))
        quit()

    for id, title, rel_url in zip(rs['id'], rs['suggestions'], rs['data']):
        from urllib.parse import urljoin
        url = urljoin(SITE, rel_url)

        print('{}: "{}": {}'.format(id, title, url))

    print()

if __name__ == '__main__':
    url = 'http://seasonvar.ru/serial-4574-Gravity_Falls.html'
    index(url)

    search("Секретные материалы")

    search("Американский папаша")

    search("грэвети фоолс")




# def main():
#     params = get_params()
#     url = None
#     name = None
#     mode = None
#
#     try:
#         url = urllib.unquote_plus(params["url"])
#     except:
#         pass
#     try:
#         name = urllib.unquote_plus(params["name"])
#     except:
#         pass
#     try:
#         mode = int(params["mode"])
#     except:
#         pass
#
#     localpath = sys.argv[0]
#     handle = int(sys.argv[1])
#
#     grabber = SeasonvarGrabber()
#
#     # first page
#     if mode is None:
#         li = xbmcgui.ListItem("Search")
#         u = localpath + "?mode=3"
#         xbmcplugin.addDirectoryItem(handle, u, li, True)
#         for serial in grabber.get_main_page_data():
#             add_dir(serial.get_url(), serial.get_name(), serial.get_thumb(), 1)
#
#     # page with links
#     elif mode is 1:
#         index(url, name)
#
#     # page with links
#     elif mode is 2:
#         play(url, name)
#
#     # page with links
#     elif mode == 3:
#         search(sys.argv[0], int(sys.argv[1]))
#
#     xbmcplugin.endOfDirectory(int(sys.argv[1]))
#
# main()
