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

import traceback

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtMultimediaWidgets import *
from PyQt5.QtMultimedia import *

from sesonvar_api import Serial, SeasonvarApi


# TODO: распространить для всего класса
def throws(func):
    """Декоратор используется для отлова исключений."""

    def tmp(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except BaseException as e:
            logging.exception(e)
            QMessageBox.critical(None, 'Error', str(e) + '\n\n' + traceback.format_exc())

    return tmp


class PlayerControls(QWidget):
    """Класс описывает виджет с медийными кнопками."""

    play_signal = pyqtSignal()
    pause_signal = pyqtSignal()
    stop_signal = pyqtSignal()
    next_signal = pyqtSignal()
    previous_signal = pyqtSignal()
    changeVolume_signal = pyqtSignal(int)
    changeMuting_signal = pyqtSignal(bool)
    changeRate_signal = pyqtSignal(float)

    def __init__(self):
        super().__init__()
        
        self.playerState = QMediaPlayer.StoppedState
        self.playerMuted = False

        self.playButton = QToolButton()
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.playClicked)
    
        self.stopButton = QToolButton()
        self.stopButton.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
        self.stopButton.setEnabled(False)
        self.stopButton.clicked.connect(self.stop_signal)

        self.nextButton = QToolButton()
        self.nextButton.setIcon(self.style().standardIcon(QStyle.SP_MediaSkipForward))
        self.nextButton.clicked.connect(self.next_signal)

        self.previousButton = QToolButton()
        self.previousButton.setIcon(self.style().standardIcon(QStyle.SP_MediaSkipBackward))
        self.previousButton.clicked.connect(self.previous_signal)

        self.muteButton = QToolButton()
        self.muteButton.setIcon(self.style().standardIcon(QStyle.SP_MediaVolume))
        self.muteButton.clicked.connect(self.muteClicked)
    
        self.volumeSlider = QSlider(Qt.Horizontal)
        self.volumeSlider.setRange(0, 100)
        self.volumeSlider.sliderMoved.connect(self.changeVolume_signal)

        self.rateBox = QComboBox()
        self.rateBox.addItem("0.5x", 0.5)
        self.rateBox.addItem("1.0x", 1.0)
        self.rateBox.addItem("2.0x", 2.0)
        self.rateBox.setCurrentIndex(1)
        self.rateBox.activated.connect(self.updateRate)
    
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.stopButton)
        layout.addWidget(self.previousButton)
        layout.addWidget(self.playButton)
        layout.addWidget(self.nextButton)
        layout.addWidget(self.muteButton)
        layout.addWidget(self.volumeSlider)
        layout.addWidget(self.rateBox)
        self.setLayout(layout)

        for tool_button in self.findChildren(QToolButton):
            tool_button.setAutoRaise(True)

    def state(self):
        return self.playerState
    
    def setState(self, state):
        if state != self.playerState:
            self.playerState = state

            if state == QMediaPlayer.StoppedState:
                self.stopButton.setEnabled(False)
                self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

            elif state == QMediaPlayer.PlayingState:
                self.stopButton.setEnabled(True)
                self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))

            elif state == QMediaPlayer.PausedState:
                self.stopButton.setEnabled(True)
                self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
    
    def volume(self):
        return self.volumeSlider.value()
    
    def setVolume(self, volume):
        if self.volumeSlider:
            self.volumeSlider.setValue(volume)
    
    def isMuted(self):
        return self.playerMuted
    
    def setMuted(self, muted):
        if muted != self.playerMuted:
            self.playerMuted = muted

            icon = QStyle.SP_MediaVolumeMuted if muted else QStyle.SP_MediaVolume
            self.muteButton.setIcon(self.style().standardIcon(icon))
    
    def playClicked(self):
        if self.playerState == QMediaPlayer.StoppedState or self.playerState == QMediaPlayer.PausedState:
            self.play_signal.emit()

        elif self.playerState == QMediaPlayer.PlayingState:
            self.pause_signal.emit()

    @throws
    def muteClicked(self, is_mute=None):
        self.changeMuting_signal.emit(not self.playerMuted)
    
    def playbackRate(self):
        return self.rateBox.itemData(self.rateBox.currentIndex()).toDouble()
    
    def setPlaybackRate(self, rate):
        for i in range(self.rateBox.count()):
            if qFuzzyCompare(rate, self.rateBox.itemData(i)):
                self.rateBox.setCurrentIndex(i)
                return
    
        self.rateBox.addItem("{}x".format(rate), rate)
        self.rateBox.setCurrentIndex(self.rateBox.count() - 1)
    
    def updateRate(self):
        self.changeRate.emit(self.playbackRate())


class SerialPlayerWindow(QMainWindow):
    """Класс описывает окно плеера с списком серий в нем."""

    def __init__(self, serial):
        super().__init__()

        self.serial = serial

        self.playlist = QMediaPlaylist()

        # TODO: обрабатывать сигналы плеера: http://doc.qt.io/qt-5/qmediaplayer.html#signals
        self.player = QMediaPlayer()
        self.player.setPlaylist(self.playlist)

        self.video_widget = QVideoWidget()
        self.video_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Нужно задать какое-нибудь значение, потому что по умолчанию размер 0x0
        self.player.setVideoOutput(self.video_widget)

        # TODO: смена видео двойныс кликом или при нажатии на enter/return
        self.series_list = QListWidget()

        # self.series_list.itemClicked.connect(lambda x: self.play(x.text()))
        # self.series_list.itemClicked.connect(lambda x: self.play(x.data(Qt.UserRole)))
        self.series_list.itemClicked.connect(lambda x: self.play())
        for series in self.serial.list_of_series:
            title, url = series
            item = QListWidgetItem(title)
            item.setData(Qt.UserRole, url)
            self.series_list.addItem(item)

            self.playlist.addMedia(QMediaContent(QUrl(url)))

        self.series_list.setCurrentRow(0)
        self.playlist.setCurrentIndex(0)

        self.controls = PlayerControls()
        # controls->setState(player->state());
        # controls->setVolume(player->volume());
        # controls->setMuted(controls->isMuted());
        #
        # connect(controls, SIGNAL(play()), player, SLOT(play()));
        # connect(controls, SIGNAL(pause()), player, SLOT(pause()));
        # connect(controls, SIGNAL(stop()), player, SLOT(stop()));
        # connect(controls, SIGNAL(next()), playlist, SLOT(next()));
        # connect(controls, SIGNAL(previous()), this, SLOT(previousClicked()));
        # connect(controls, SIGNAL(changeVolume(int)), player, SLOT(setVolume(int)));
        # connect(controls, SIGNAL(changeMuting(bool)), player, SLOT(setMuted(bool)));
        # connect(controls, SIGNAL(changeRate(qreal)), player, SLOT(setPlaybackRate(qreal)));
        #
        # connect(controls, SIGNAL(stop()), videoWidget, SLOT(update()));
        #
        # connect(player, SIGNAL(stateChanged(QMediaPlayer::State)),
        #         controls, SLOT(setState(QMediaPlayer::State)));
        # connect(player, SIGNAL(volumeChanged(int)), controls, SLOT(setVolume(int)));
        # connect(player, SIGNAL(mutedChanged(bool)), controls, SLOT(setMuted(bool)));

        # TODO:
        #     if (!player->isAvailable()) {
        #         QMessageBox::warning(this, tr("Service not available"),
        #                              tr("The QMediaPlayer object does not have a valid service.\n"\
        #                                 "Please check the media service plugins are installed."));
        #
        #         controls->setEnabled(false);
        #         playlistView->setEnabled(false);
        #         openButton->setEnabled(false);
        # #ifndef PLAYER_NO_COLOROPTIONS
        #         colorButton->setEnabled(false);
        # #endif
        #         fullScreenButton->setEnabled(false);
        #     }

        self.setCentralWidget(QWidget())
        self.centralWidget().setLayout(QVBoxLayout())
        self.centralWidget().layout().setContentsMargins(0, 0, 0, 0)
        self.centralWidget().layout().addWidget(self.video_widget)
        self.centralWidget().layout().addWidget(self.controls)

        series_list_dock_widget = QDockWidget("Список серий")
        series_list_dock_widget.setObjectName('series_list_dock_widget')
        series_list_dock_widget.setWidget(self.series_list)
        self.addDockWidget(Qt.RightDockWidgetArea, series_list_dock_widget)

        self.update_states()

    # TODO: временно
    def play(self):
        if self.series_list.count() == 0:
            logging.debug('Список видео пуст.')
            return

        if self.series_list.currentRow() == -1:
            self.series_list.setCurrentRow(0)

        url = self.series_list.currentItem().data(Qt.UserRole)
        logging.debug('Воспроизведение "%s".', url)

        self.player.stop()
        self.playlist.setCurrentIndex(self.series_list.currentRow())
        self.player.play()

        self.update_states()

    def get_serial(self):
        return self.serial

    def update_states(self):
        title = self.serial.name
        if self.series_list.currentRow() != -1:
            title += ' - ' + self.series_list.currentItem().text()

        self.setWindowTitle(title)

    def closeEvent(self, event):
        self.player.stop()

        super().closeEvent(event)


class SerialInfoWidget(QWidget):
    play_serial_signal = pyqtSignal(Serial)

    def __init__(self):
        super().__init__()

        self._serial = None

        # TODO: лучше сгенерировать html страничку с описанием
        self._title = QLabel()
        self._title.setWordWrap(True)
        self._title.setAlignment(Qt.AlignCenter)
        font = self._title.font()
        font.setPointSizeF(font.pointSizeF() + 3)
        self._title.setFont(font)

        self._cover = QLabel()
        self._cover.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        self._description = QLabel()
        self._description.setWordWrap(True)
        self._description.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        font = self._description.font()
        font.setPointSizeF(font.pointSizeF() + 1)
        self._description.setFont(font)

        self._play_button = QPushButton('Смотреть.')

        # В лябде проверяем, что self._serial не пустой и тогда отправляем сигнал с ним
        self._play_button.clicked.connect(self._play_button_clicked)

        # TODO: вроде бы, порядок всегда одинаковый, поэтмоу можно вручную проставить серии
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self._title)
        hlayout = QHBoxLayout()
        hlayout.addWidget(self._cover)
        hlayout.addItem(QSpacerItem(10, 10, QSizePolicy.Fixed, QSizePolicy.Fixed))
        hlayout.addWidget(self._description)
        self.layout().addLayout(hlayout)
        self.layout().addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.layout().addWidget(self._play_button)

        self.clear()

    def _play_button_clicked(self):
        if self._serial:
            self.play_serial_signal.emit(self._serial)

    def set_serial(self, serial):
        logging.debug('SerialInfoWidget.set_serial. serial: %s.', serial)

        self._serial = serial
        self._update_info()

    def clear(self):
        self._serial = None
        self._update_info()

    def _update_info(self):
        """Функция заполняет виджеты классы от self.serial."""

        logging.debug('SerialInfoWidget._update_info. serial: %s.', self._serial)

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

        # TODO: добавить кнопку, очищающую текст
        # TODO: задержка поиска пока ввода не окончится
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
        splitter.setSizes([self.width() / 2, self.width() / 2])

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

    @throws
    def _show_serial_info(self, item):
        logging.debug('_show_serial_info. item: %s.', item)
        serial = item.data(Qt.UserRole)
        logging.debug('_show_serial_info. serial: %s.', serial)
        self.serial_info.set_serial(serial)

    def _open_player_serial(self, serial):
        try:
            # Если окно-плеера сериала нет, добавляем, иначе показываем окно
            if serial not in self._serials_by_player_dict:
                player = SerialPlayerWindow(serial)
                self._serials_by_player_dict[serial] = player
            else:
                player = self._serials_by_player_dict[serial]

            # player.show()
            player.resize(800, 500)
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

    def closeEvent(self, *args, **kwargs):
        QApplication.quit()


# TODO: сохранение загрузка настроек
if __name__ == '__main__':
    a = QApplication([])

    mw = MainWindow()
    mw.resize(800, 600)
    mw.show()
    # TODO: rem
    mw.serial_search.setText('gravity')

    # serial = Serial('', '', '')
    # serial._Serial__list_of_series = [
    #     r'C:\Users\ipetrash\Desktop\7f_Gravity.Falls.S01E01.rus.vo.sienduk.a1.08.12.15.mp4'.replace('\\', '/'),
    #     r'C:\Users\ipetrash\Desktop\7f_Gravity.Falls.S01E01.rus.vo.sienduk.a1.08.12.15.mp4'.replace('\\', '/'),
    #     r'C:\Users\ipetrash\Desktop\7f_Gravity.Falls.S01E01.rus.vo.sienduk.a1.08.12.15.mp4'.replace('\\', '/'),
    #     r'C:\Users\ipetrash\Desktop\7f_Gravity.Falls.S01E01.rus.vo.sienduk.a1.08.12.15.mp4'.replace('\\', '/'),
    #     r'C:\Users\ipetrash\Desktop\7f_Gravity.Falls.S01E01.rus.vo.sienduk.a1.08.12.15.mp4'.replace('\\', '/'),
    # ]
    # serial._has_load_data = True
    # spw = SerialPlayerWindow(serial)
    # spw.show()
    # spw.play()

    a.exec_()
