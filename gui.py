#!/usr/bin/env python3
# -*- coding: utf-8 -*-


__author__ = 'ipetrash'


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

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtMultimediaWidgets import *
from PyQt5.QtMultimedia import *

from sesonvar_api import Serial, SeasonvarApi


# TODO:
class SerialPlayer(QWidget):
    def __init__(self, serial):
        super().__init__()

        self.serial = serial
        self.setWindowTitle(self.serial.name)

        # TODO: QMediaPlaylist объекдиинть с QListView
        # TODO: пока запускаем автоматом первую серию
        self.playlist = QMediaPlaylist()

        self.player = QMediaPlayer()
        self.player.setPlaylist(self.playlist)

        self.video_widget = QVideoWidget()
        # Нужно задать какое-нибудь значение, потому что по умолчанию размер 0x0
        self.player.setVideoOutput(self.video_widget)

        # TODO: лучше в dockwidget перенести
        # TODO: смена видео двойныс кликом или при нажатии на enter/return
        self.series_list = QListWidget()
        self.series_list.itemClicked.connect(lambda x: self.play(x.text()))
        for series in self.serial.list_of_series:
            self.series_list.addItem(series)

        self.setLayout(QHBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(self.video_widget)
        self.layout().addWidget(self.series_list)

        # self.video_widget.resize(400, 400)
        self.video_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    # TODO: временно
    def play(self, url=None):
        # TODO: избавиться от костыля с clear, add и setCurrentIndex

        if url is None:
            url = self.series_list.item(0).text()

        self.playlist.clear()
        self.playlist.addMedia(QMediaContent(QUrl(url)))
        self.playlist.setCurrentIndex(0)
        self.player.play()

    def get_serial(self):
        return self.serial

    def closeEvent(self, event):
        self.player.stop()

        super().closeEvent(event)


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

        # В лябде проверяем, что self._serial не пустой и тогда отправляем сигнал с ним
        self._play_button.clicked.connect(self._play_button_clicked)

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self._title)
        self.layout().addWidget(self._cover)
        self.layout().addWidget(self._description)

        # TODO: вроде бы, порядок всегда одинаковый, поэтмоу можно вручную проставить серии
        # TODO: вставить пружинку
        self.layout().addWidget(self._play_button)

        self.clear()

    def _play_button_clicked(self):
        if self._serial:
            self.play_serial_signal.emit(self._serial)

    def set_serial(self, serial):
        self._serial = serial
        self._update_info()

    def clear(self):
        self._serial = None
        self._update_info()

    def _update_info(self):
        """Функция заполняет виджеты классы от self.serial."""

        if self._serial:
            self._title.setText(self._serial.name)
            self._description.setText(self._serial.description)

            pixmap = QPixmap()
            raw_image = self._serial.get_cover_image()
            pixmap.loadFromData(raw_image)
            self._cover.setPixmap(pixmap)

            self._title.show()
            self._cover.show()
            self._description.show()
            self._play_button.show()
        else:
            self._title.clear()
            self._cover.clear()
            self._description.clear()
            self._series_list.clear()

            self._title.hide()
            self._cover.hide()
            self._description.hide()
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
        self.serial_search.textChanged.connect(self._search_serials)

        self.serials_list = QListWidget()
        self.serials_list.itemClicked.connect(self._show_serial_info)

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

    def _search_serials(self, text):
        self.serials_list.clear()
        self.serial_info.clear()

        serial_list = SeasonvarApi.search(text)
        if not serial_list:
            # TODO: добавить виджет с такой надписью:
            logging.debug('Ничего не найдено')
            return

        for serial in serial_list:
            item = QListWidgetItem(serial.name)
            item.setData(Qt.UserRole, serial)
            self.serials_list.addItem(item)

    def _show_serial_info(self, item):
        try:

            serial = item.data(Qt.UserRole)
            self.serial_info.set_serial(serial)

        except BaseException as e:
            logging.exception(e)

            import traceback
            QMessageBox.critical(None, 'Error', traceback.format_exc())
            quit()

    def _open_player_serial(self, serial):
        try:
            # Если окно-плеера сериала нет, добавляем, иначе показываем окно
            if serial not in self._serials_by_player_dict:
                player = SerialPlayer(serial)
                self._serials_by_player_dict[serial] = player
            else:
                player = self._serials_by_player_dict[serial]

            # player.show()
            player.resize(300, 300)
            player.showNormal()

            # TODO: временно
            # TODO: проверять что плеер уже запущен
            # TODO: запускать текущий выбранный в окне информации
            player.play()

        except BaseException as e:
            logging.exception(e)

            import traceback
            QMessageBox.critical(None, 'Error', traceback.format_exc())
            quit()

    # TODO: следить за окнами-плеерами и при их закрытии/уничтожении убирать их из своего списка
    # def eventFilter(self, QObject, QEvent):
    #     pass


# TODO: сохранение загрузка настроек
if __name__ == '__main__':
    a = QApplication([])

    mw = MainWindow()
    mw.resize(600, 600)
    mw.show()
    # TODO: rem
    mw.serial_search.setText('gravity')

    a.exec_()
