#!/usr/bin/env python3
# -*- coding: utf-8 -*-


__author__ = 'ipetrash'


from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from base64 import b64decode


# TODO: временно
from test_serials import serial_list


# TODO:
class SerialPlayer(QWidget):
    def __init__(self, serial):
        super().__init__()

        self.setWindowTitle(self.serial['title'])
        self.serial = serial

    def get_serial(self):
        return self.serial


# TODO: добавить кнопку просмотра, которая открывает окно-плеер
class SerialInfoWidget(QWidget):
    play_serial = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.serial = None

        self.title = QLabel()
        self.title .setWordWrap(True)

        self.cover = QLabel()

        self.description = QLabel()
        self.description.setWordWrap(True)

        self.play_button = QPushButton('Смотреть.')

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.title)
        self.layout().addWidget(self.cover)
        self.layout().addWidget(self.description)
        self.layout().addWidget(self.play_button)

        self.clear()

    def set_serial(self, serial):
        self.serial = serial
        self._update_info()

    def clear(self):
        self.serial = None
        self._update_info()

    def _update_info(self):
        """Функция заполняет виджеты классы от self.serial."""

        if self.serial:
            self.title.setText(self.serial['title'])
            self.description.setText(self.serial['description'])

            pixmap = QPixmap()
            raw_image = b64decode(self.serial['cover_image'])
            pixmap.loadFromData(raw_image)
            self.cover.setPixmap(pixmap)
        else:
            self.title.clear()
            self.cover.clear()
            self.description.clear()


# TODO: добавить меню, в котором будут все окна-плееры
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Seasonvar Gui')

        splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(splitter)

        self.serial_search = QLineEdit()
        self.serial_search.setPlaceholderText('Введите название сериала...')
        self.serial_search.textEdited.connect(self._search_serials)

        self.serials_list = QListWidget()
        self.serials_list.itemClicked.connect(self._show_serial_info)
        self.serials_list.itemDoubleClicked.connect(self._open_player_serial)

        serials_search_and_list = QWidget()
        serials_search_and_list.setLayout(QVBoxLayout())
        serials_search_and_list.layout().addWidget(self.serial_search)
        serials_search_and_list.layout().addWidget(self.serials_list)

        self.serial_info = SerialInfoWidget()

        splitter.addWidget(serials_search_and_list)
        splitter.addWidget(self.serial_info)

        # Словарь по сериалам хранит их окна-плееры
        self._serials_by_player_dict = dict()
        # self._player_by_serials_dict = dict()

        # TODO: временно
        for serial in serial_list:
            item = QListWidgetItem(serial['title'])
            item.setData(Qt.UserRole, serial)
            self.serials_list.addItem(item)

    def _search_serials(self, text):
        self.serials_list.clear()
        self.serial_info.clear()

    def _show_serial_info(self, item):
        serial = item.data(Qt.UserRole)
        self.serial_info.set_serial(serial)

    def _open_player_serial(self, item):
        # serial = item.data(Qt.UserRole)
        serial = None

        # Если окно-плеера сериала нет, добавляем, иначе показываем окно
        if serial not in self._serials_by_player_dict:
            self._serials_by_player_dict[serial] = SerialPlayer(serial)
        else:
            player = self._serials_by_player_dict[serial]
            # player.show()
            player.showNormal()

    # TODO: следить за окнами-плеерами и при их закрытии/уничтожении убирать их из своего списка
    # def eventFilter(self, QObject, QEvent):
    #     pass


if __name__ == '__main__':
    a = QApplication([])

    mw = MainWindow()
    mw.show()
    # playlist = QMediaPlaylist()
    # # playlist.addMedia(QMediaContent(QUrl("http://data06-cdn.datalock.ru/fi2lm/953324b302d8aca1ca76975fe7055e44/7f_Gravity.Falls.S01E18.rus.vo.sienduk.a0.08.12.15.mp4")))
    # playlist.addMedia(QMediaContent(QUrl.fromLocalFile(r"C:\Users\ipetrash\Desktop\7f_Gravity.Falls.S01E01.rus.vo.sienduk.a1.08.12.15.mp4")))
    # playlist.setCurrentIndex(0)
    #
    # player = QMediaPlayer()
    # player.setPlaylist(playlist)
    #
    # videoWidget = QVideoWidget()
    # player.setVideoOutput(videoWidget)
    # videoWidget.show()
    #
    # videoWidget.resize(200, 200)
    #
    # mw = QMainWindow()
    # mw.setCentralWidget(videoWidget)
    # mw.show()
    #
    # player.play()

    a.exec_()
