#!/usr/bin/env python3
# -*- coding: utf-8 -*-


__author__ = 'ipetrash'


from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from base64 import b64decode

from sesonvar_api import *

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


# TODO: добавить кнопку просмотра, которая открывает окно-плеер
class SerialInfoWidget(QWidget):
    play_serial_signal = pyqtSignal(Serial)

    def __init__(self):
        super().__init__()

        self._serial = None

        self._title = QLabel()
        self._title .setWordWrap(True)

        self._cover = QLabel()

        self._description = QLabel()
        self._description.setWordWrap(True)

        self._play_button = QPushButton('Смотреть.')

        # TODO:
        # self._play_button.clicked.connect(lambda x=None: self.play_serial_signal.emit(self._serial))
        def play_button_click():
            try:
                print('dfsdfsdfs')
                # self.play_serial_signal.emit(self._serial)
                self.play_serial_signal.emit(Serial())
                print('2321323')
            except Exception as e:
                print(e)

        self._play_button.clicked.connect(play_button_click)

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self._title)
        self.layout().addWidget(self._cover)
        self.layout().addWidget(self._description)
        # TODO: вставить пружинку
        self.layout().addWidget(self._play_button)

        self.clear()

    def set_serial(self, serial):
        self._serial = serial
        self._update_info()

    def clear(self):
        self._serial = None
        self._update_info()

    def _update_info(self):
        """Функция заполняет виджеты классы от self.serial."""

        if self._serial:
            self._title.setText(self._serial['title'])
            self._description.setText(self._serial['description'])

            pixmap = QPixmap()
            raw_image = b64decode(self._serial['cover_image'])
            pixmap.loadFromData(raw_image)
            self._cover.setPixmap(pixmap)

            self._play_button.show()
        else:
            self._title.clear()
            self._cover.clear()
            self._description.clear()
            self._play_button.hide()


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

        # При двойном клике посылается указатель на item, у которого в лябда-выражении, из data
        # достаем объект Serial и его передаем в функцию открытия плеера
        self.serials_list.itemDoubleClicked.connect(lambda x: self._open_player_serial(x.data(Qt.UserRole)))

        serials_search_and_list = QWidget()
        serials_search_and_list.setLayout(QVBoxLayout())
        serials_search_and_list.layout().addWidget(self.serial_search)
        serials_search_and_list.layout().addWidget(self.serials_list)

        self.serial_info = SerialInfoWidget()
        self.serial_info.play_serial_signal.connect(self._open_player_serial)

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
        print('_open_player_serial', item)

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
    # TODO: try / except
    a = QApplication([])

    mw = MainWindow()
    mw.show()

    a.exec_()
