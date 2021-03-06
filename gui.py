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

from seasonvar_api import Serial, SeasonvarApi, NotFoundException

from urllib.error import HTTPError


def log_uncaught_exceptions(ex_cls, ex, tb):
    text = '{}: {}:\n'.format(ex_cls.__name__, ex)
    text += ''.join(traceback.format_tb(tb))

    logging.critical(text)
    QMessageBox.critical(None, 'Error', text)
    quit()

sys.excepthook = log_uncaught_exceptions


class PlayerControls(QWidget):
    """Класс описывает виджет с медийными кнопками."""

    play_signal = pyqtSignal()
    pause_signal = pyqtSignal()
    stop_signal = pyqtSignal()
    next_signal = pyqtSignal()
    previous_signal = pyqtSignal()
    change_volume_signal = pyqtSignal(int)
    change_muting_signal = pyqtSignal(bool)
    change_rate_signal = pyqtSignal(float)

    def __init__(self, player):
        super().__init__()

        self.player_state = QMediaPlayer.StoppedState
        self.player_muted = False

        self.player_slider = QSlider(Qt.Horizontal)
        self.player_slider.sliderMoved.connect(lambda secs: player.setPosition(secs * 1000))

        self.label_duration = QLabel()
        player.durationChanged.connect(lambda duration: self.player_slider.setRange(0, duration // 1000))
        player.positionChanged.connect(self._position_changed)

        player.stateChanged.connect(self.set_state)
        player.volumeChanged.connect(self.set_volume)
        player.mutedChanged.connect(self.set_muted)

        # TODO: добавить горячие клавиши для управления медиа
        self.play_pause_button = QToolButton()
        self.play_pause_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.play_pause_button.clicked.connect(self.play_clicked)
    
        self.stop_button = QToolButton()
        self.stop_button.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_signal)

        self.next_button = QToolButton()
        self.next_button.setIcon(self.style().standardIcon(QStyle.SP_MediaSkipForward))
        self.next_button.clicked.connect(self.next_signal)

        self.previous_button = QToolButton()
        self.previous_button.setIcon(self.style().standardIcon(QStyle.SP_MediaSkipBackward))
        self.previous_button.clicked.connect(self.previous_signal)

        self.mute_button = QToolButton()
        self.mute_button.setIcon(self.style().standardIcon(QStyle.SP_MediaVolume))
        self.mute_button.clicked.connect(self.mute_clicked)
    
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.sliderMoved.connect(self.change_volume_signal)

        self.rate_box = QComboBox()
        self.rate_box.addItem("0.5x", 0.5)
        self.rate_box.addItem("1.0x", 1.0)
        self.rate_box.addItem("2.0x", 2.0)
        self.rate_box.setCurrentIndex(1)
        self.rate_box.activated.connect(self.update_rate)

        layout = QHBoxLayout()
        layout.addWidget(self.player_slider)
        layout.addWidget(self.label_duration)
    
        layout_buttons = QHBoxLayout()
        layout_buttons.setContentsMargins(0, 0, 0, 0)
        layout_buttons.setSpacing(0)
        layout_buttons.addWidget(self.stop_button)
        layout_buttons.addWidget(self.previous_button)
        layout_buttons.addWidget(self.play_pause_button)
        layout_buttons.addWidget(self.next_button)
        layout_buttons.addWidget(self.mute_button)
        layout_buttons.addWidget(self.volume_slider)
        layout_buttons.addWidget(self.rate_box)
        
        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addLayout(layout_buttons)
        self.setLayout(main_layout)

        for tool_button in self.findChildren(QToolButton):
            tool_button.setAutoRaise(True)

    def _position_changed(self, pos):
        # TODO: с этим условием при кликах на тело слайдера, ползунок слайдера сдвинется
        # но видео не будет перемотано
        if not self.player_slider.isSliderDown():
            self.player_slider.setValue(pos / 1000)

        self._update_duration_info()

    def _update_duration_info(self):
        ms_pattern = "{:0>2}:{:0>2}"
        hms_pattern = "{}:" + ms_pattern

        seconds = self.player_slider.value()
        current_minutes, current_seconds = divmod(seconds, 60)
        current_hours, current_minutes = divmod(current_minutes, 60)
        if current_hours > 0:
            current = hms_pattern.format(current_hours, current_minutes, current_seconds)
        else:
            current = ms_pattern.format(current_minutes, current_seconds)

        total_seconds = self.player_slider.maximum()
        total_minutes, total_seconds = divmod(total_seconds, 60)
        total_hours, total_minutes = divmod(total_minutes, 60)
        if total_hours > 0:
            total = hms_pattern.format(total_hours, total_minutes, total_seconds)
        else:
            total = ms_pattern.format(total_minutes, total_seconds)

        self.label_duration.setText(current + ' / ' + total)

    def state(self):
        return self.player_state
    
    def set_state(self, state):
        if state != self.player_state:
            self.player_state = state

            if state == QMediaPlayer.StoppedState:
                self.stop_button.setEnabled(False)
                self.play_pause_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

            elif state == QMediaPlayer.PlayingState:
                self.stop_button.setEnabled(True)
                self.play_pause_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))

            elif state == QMediaPlayer.PausedState:
                self.stop_button.setEnabled(True)
                self.play_pause_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
    
    def volume(self):
        return self.volume_slider.value()
    
    def set_volume(self, volume):
        self.volume_slider.setValue(volume)
    
    def is_muted(self):
        return self.player_muted
    
    def set_muted(self, muted):
        if muted != self.player_muted:
            self.player_muted = muted

            icon = QStyle.SP_MediaVolumeMuted if muted else QStyle.SP_MediaVolume
            self.mute_button.setIcon(self.style().standardIcon(icon))
    
    def play_clicked(self):
        if self.player_state == QMediaPlayer.StoppedState or self.player_state == QMediaPlayer.PausedState:
            self.play_signal.emit()

        elif self.player_state == QMediaPlayer.PlayingState:
            self.pause_signal.emit()

    def mute_clicked(self, is_mute=None):
        self.change_muting_signal.emit(not self.player_muted)
    
    def playback_rate(self):
        return self.rate_box.itemData(self.rate_box.currentIndex())
    
    def set_playback_rate(self, rate):
        for i in range(self.rate_box.count()):
            if qFuzzyCompare(rate, self.rate_box.itemData(i)):
                self.rate_box.setCurrentIndex(i)
                return
    
        self.rate_box.addItem("{}x".format(rate), rate)
        self.rate_box.setCurrentIndex(self.rate_box.count() - 1)
    
    def update_rate(self):
        self.change_rate_signal.emit(self.playback_rate())


class VideoWidget(QVideoWidget):
    def __init__(self):
        super().__init__()

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        p = self.palette()
        p.setColor(QPalette.Window, Qt.black)
        self.setPalette(p)
        self.setAttribute(Qt.WA_OpaquePaintEvent)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape and self.isFullScreen():
            self.setFullScreen(False)
            event.accept()
        else:
            super().keyPressEvent(event)

    def mouseDoubleClickEvent(self, event):
        self.setFullScreen(not self.isFullScreen())
        event.accept()


class PlayerWindow(QMainWindow):
    """Класс описывает окно плеера с списком серий в нем."""

    def __init__(self, list_of_series, serial_name):
        super().__init__()

        self.serial_name = serial_name
        self.playlist = QMediaPlaylist()

        # TODO: обрабатывать сигналы плеера: http://doc.qt.io/qt-5/qmediaplayer.html#signals
        self.player = QMediaPlayer()
        self.player.setPlaylist(self.playlist)


        # void 	audioRoleChanged(QAudio::Role role)
        # void 	currentMediaChanged(const QMediaContent &media)
        # void 	error(QMediaPlayer::Error error)
        # void 	mediaChanged(const QMediaContent &media)
        # void 	mediaStatusChanged(QMediaPlayer::MediaStatus status)
        # void 	networkConfigurationChanged(const QNetworkConfiguration &configuration)
        # void 	stateChanged(QMediaPlayer::State state)

        self.player.audioAvailableChanged.connect(lambda x: print('audioAvailableChanged:', x))
        self.player.audioRoleChanged.connect(lambda x: print('audioRoleChanged:', x))
        self.player.bufferStatusChanged.connect(lambda x: print('bufferStatusChanged:', x))
        self.player.durationChanged.connect(lambda x: print('durationChanged:', x))
        self.player.error.connect(lambda x: print('error:', {
            QMediaPlayer.NoError: 'NoError: No error has occurred.',
            QMediaPlayer.ResourceError:	"ResourceError: A media resource couldn't be resolved.",
            QMediaPlayer.FormatError:	"FormatError: The format of a media resource isn't (fully) supported. Playback may still be possible, but without an audio or video component.",
            QMediaPlayer.NetworkError:	'NetworkError: A network error occurred.',
            QMediaPlayer.AccessDeniedError: 'AccessDeniedError: There are not the appropriate permissions to play a media resource.',
            QMediaPlayer.ServiceMissingError: 'ServiceMissingError: A valid playback service was not found, playback cannot proceed.',
        }[x], self.player.errorString()))
        self.player.mediaChanged.connect(lambda x: print('mediaChanged:', x))

        self.player.mediaStatusChanged.connect(lambda x: print('mediaStatusChanged:', {
            QMediaPlayer.AccessDeniedError: 'AccessDeniedError',
            QMediaPlayer.BufferedMedia: 'BufferedMedia',
            QMediaPlayer.BufferingMedia: 'BufferingMedia',
            QMediaPlayer.EndOfMedia: 'EndOfMedia',
            QMediaPlayer.FormatError: 'FormatError',
            QMediaPlayer.InvalidMedia: 'InvalidMedia',
            QMediaPlayer.LoadedMedia: 'LoadedMedia',
            QMediaPlayer.LoadingMedia: 'LoadingMedia',
            QMediaPlayer.LowLatency: 'LowLatency',
            QMediaPlayer.NetworkError: 'NetworkError',
            QMediaPlayer.NoError: 'NoError',
            QMediaPlayer.NoMedia: 'NoMedia',
            QMediaPlayer.PausedState: 'PausedState',
            QMediaPlayer.PlayingState: 'PlayingState',
            QMediaPlayer.ResourceError: 'ResourceError',
            QMediaPlayer.ServiceMissingError: 'ServiceMissingError',
            QMediaPlayer.StalledMedia: 'StalledMedia',
            QMediaPlayer.StoppedState: 'StoppedState',
            QMediaPlayer.StreamPlayback: 'StreamPlayback',
            QMediaPlayer.UnknownMediaStatus: 'UnknownMediaStatus',
            QMediaPlayer.VideoSurface: 'VideoSurface',
        }[x]))

        self.player.networkConfigurationChanged.connect(lambda x: print('networkConfigurationChanged:', x))
        self.player.playbackRateChanged.connect(lambda x: print('playbackRateChanged:', x))
        self.player.positionChanged.connect(lambda x: print('positionChanged:', x))
        self.player.seekableChanged.connect(lambda x: print('seekableChanged:', x))
        self.player.stateChanged.connect(lambda x: print('stateChanged:', {
            QMediaPlayer.StoppedState: 'StoppedState: The media player is not playing content, playback will begin from the start of the current track.',
            QMediaPlayer.PlayingState: 'PlayingState: The media player is currently playing content.',
            QMediaPlayer.PausedState: 'PausedState: The media player has paused playback, playback of the current track will resume from the position the player was paused at.',
        }[x]))
        self.player.videoAvailableChanged.connect(lambda x: print('videoAvailableChanged:', x))
        self.player.volumeChanged.connect(lambda x: print('volumeChanged:', x))


        self.video_widget = VideoWidget()

        # Нужно задать какое-нибудь значение, потому что по умолчанию размер 0x0
        self.player.setVideoOutput(self.video_widget)

        self.series_list_widget = QListWidget()
        self.series_list_widget.installEventFilter(self)
        self.series_list_widget.itemDoubleClicked.connect(self._play_item)
        self.__current_item = None

        self.playlist.currentIndexChanged.connect(lambda row: self.series_list_widget.setCurrentRow(row))

        for series in list_of_series:
            title, url = series
            item = QListWidgetItem(title)
            item.setData(Qt.UserRole, url)
            self.series_list_widget.addItem(item)

            self.playlist.addMedia(QMediaContent(QUrl(url)))

        if not self.player.isAvailable():
            # TODO: перевод
            QMessageBox.warning(self, "Service not available",
                                "The QMediaPlayer object does not have a valid service.\n"
                                "Please check the media service plugins are installed.")

            self.controls.setEnabled(False)
            self.series_list_widget.setEnabled(False)
            # TODO: добавить кнопки colorButton и fullScreenButton
            # colorButton->setEnabled(false)
            # fullScreenButton->setEnabled(false)

        self.series_list_widget.setCurrentRow(0)
        self.playlist.setCurrentIndex(0)

        self.controls = PlayerControls(self.player)
        self.controls.set_state(self.player.state())
        self.controls.set_volume(self.player.volume())
        self.controls.set_muted(self.controls.is_muted())

        self.controls.play_signal.connect(self.player.play)
        self.controls.pause_signal.connect(self.player.pause)
        self.controls.stop_signal.connect(self.player.stop)
        self.controls.stop_signal.connect(self.video_widget.update)
        self.controls.next_signal.connect(self.playlist.next)
        self.controls.previous_signal.connect(self.playlist.previous)
        self.controls.change_volume_signal.connect(self.player.setVolume)
        self.controls.change_muting_signal.connect(self.player.setMuted)
        self.controls.change_rate_signal.connect(self.player.setPlaybackRate)

        self.setCentralWidget(QWidget())
        self.centralWidget().setLayout(QVBoxLayout())
        # TODO: обнаружился баг https://bugreports.qt.io/browse/QTBUG-54906, из-за которого
        # при указание "краев" не разворачивается во весь экран окно плеера
        # self.centralWidget().layout().setContentsMargins(0, 0, 0, 5)
        self.centralWidget().layout().addWidget(self.video_widget)
        self.centralWidget().layout().addWidget(self.controls)

        series_list_dock_widget = QDockWidget("Список серий")
        series_list_dock_widget.setObjectName('series_list_dock_widget')
        series_list_dock_widget.setWidget(self.series_list_widget)
        series_list_dock_widget.setFeatures(QDockWidget.DockWidgetMovable)
        self.addDockWidget(Qt.RightDockWidgetArea, series_list_dock_widget)

        self._update_states()

    def _play_item(self, item):
        # Проверяем, что клик не происходит по текущему элементу
        if self.__current_item != item:
            self.__current_item = item
            self.play()

    def play(self):
        if self.series_list_widget.count() == 0:
            logging.debug('Список видео пуст.')
            return

        if self.series_list_widget.currentRow() == -1:
            self.series_list_widget.setCurrentRow(0)

        url = self.series_list_widget.currentItem().data(Qt.UserRole)
        logging.debug('Воспроизведение "%s".', url)

        self.player.stop()
        self.playlist.setCurrentIndex(self.series_list_widget.currentRow())
        self.player.play()

        self._update_states()

    def _update_states(self):
        title = self.serial_name
        if self.series_list_widget.currentRow() != -1:
            title += ' - ' + self.series_list_widget.currentItem().text()

        self.setWindowTitle(title)

    def eventFilter(self, obj, event):
        # Воспроизведение видео при клике на кнопки Enter/Return в плейлисте
        if obj == self.series_list_widget and event.type() == QKeyEvent.KeyPress:
            if self.series_list_widget.hasFocus() and event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                item = self.series_list_widget.currentItem()
                if item is not None:
                    self._play_item(item)

        return super().eventFilter(obj, event)

    def closeEvent(self, event):
        self.player.stop()

        super().closeEvent(event)


class SerialInfoWidget(QWidget):
    play_serial_signal = pyqtSignal(Serial)

    def __init__(self):
        super().__init__()

        self._serial = None

        # TODO: наверное, лучше сгенерировать html страничку с описанием
        self._title = QLabel()
        self._title.setWordWrap(True)
        self._title.setAlignment(Qt.AlignCenter)
        font = self._title.font()
        font.setPointSizeF(font.pointSizeF() + 3)
        self._title.setFont(font)

        self._cover = QLabel()
        self._cover.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        self._description = QTextEdit()
        # Отключение автозаполнения фона текстового редактора
        self._description.viewport().setAutoFillBackground(False)
        self._description.setReadOnly(True)
        self._description.setFrameStyle(QTextEdit.NoFrame)
        self._description.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        font = self._description.font()
        font.setPointSizeF(font.pointSizeF() + 1)
        self._description.setFont(font)

        self._play_button = QPushButton('Смотреть.')
        self._play_button.clicked.connect(self._play_button_clicked)

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self._title)

        self._label_url = QLabel()
        self._label_url.setOpenExternalLinks(True)

        layout_cover_and_url = QVBoxLayout()
        layout_cover_and_url.addWidget(self._cover)
        layout_cover_and_url.addWidget(self._label_url)
        layout_cover_and_url.addItem(QSpacerItem(10, 10, QSizePolicy.Fixed, QSizePolicy.Expanding))

        hlayout = QHBoxLayout()
        hlayout.addLayout(layout_cover_and_url)
        hlayout.addItem(QSpacerItem(10, 10, QSizePolicy.Fixed, QSizePolicy.Fixed))
        hlayout.addWidget(self._description)
        self.layout().addLayout(hlayout)
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
        logging.debug('SerialInfoWidget.clear')

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

            self._label_url.setText('<a href="{}">Сериал на сайте</a>'.format(self._serial.url))

            for child in self.findChildren(QWidget):
                child.show()

            # TODO: показывать выше кнопки предупреждение о невозможности запуска
            # как вариант, причину блокировки брать с страницы -- скорее всего там будет
            # о блокировке в данной стране по просьбе правообладателя.
            self._play_button.setEnabled(self._serial.is_valid())

        else:
            self._title.clear()
            self._cover.clear()
            self._description.clear()
            self._label_url.clear()

            for child in self.findChildren(QWidget):
                child.hide()


# TODO: добавить меню, в котором будут все окна-плееры
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Seasonvar Gui')

        splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(splitter)

        self.serial_search = QLineEdit()
        self.serial_search.setPlaceholderText('Введите название сериала...')
        self.serial_search.setClearButtonEnabled(True)

        # Таймер нужен для задержки поиска. Поиск начнется когда произойдет задержка ввода
        timer_delayed_search = QTimer(self.serial_search)
        timer_delayed_search.setInterval(150)
        timer_delayed_search.setSingleShot(True)
        timer_delayed_search.timeout.connect(lambda x=None: self._search_serials(self.serial_search.text()))
        self.serial_search.textChanged.connect(timer_delayed_search.start)

        self._current_serial_item = None
        self.serials_list_widget = QListWidget()
        self.serials_list_widget.itemClicked.connect(self._show_serial_info)

        serials_search_and_list = QWidget()
        serials_search_and_list.setLayout(QVBoxLayout())
        serials_search_and_list.layout().addWidget(self.serial_search)
        serials_search_and_list.layout().addWidget(self.serials_list_widget)

        self.serial_info = SerialInfoWidget()
        self.serial_info.play_serial_signal.connect(self._open_player_serial)

        splitter.addWidget(serials_search_and_list)
        splitter.addWidget(self.serial_info)
        splitter.setSizes([self.width() * 0.4, self.width() * 0.6])

        self.info_widget = QTextEdit()
        self.info_widget.setReadOnly(True)
        self.info_widget.setFrameStyle(QTextEdit.NoFrame)
        self.info_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.info_widget.hide()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        layout.addWidget(self.info_widget)
        self.serials_list_widget.setLayout(layout)

        # Словарь по сериалам хранит их окна-плееры
        self._serials_by_player_dict = dict()
        # self._player_by_serials_dict = dict()

    def _search_serials(self, text):
        self.serials_list_widget.clear()
        self.info_widget.hide()

        if not text:
            return

        try:
            for serial in SeasonvarApi.search(text):
                item = QListWidgetItem(serial.name)
                item.setData(Qt.UserRole, serial)
                self.serials_list_widget.addItem(item)

        except NotFoundException as e:
            text = str(e)
            logging.debug(text)

            self.info_widget.setText(text)
            self.info_widget.show()

        except HTTPError as e:
            text = 'Проблема с интернетом. Ошибка: "{}".'.format(e)
            logging.exception(text)

            text += '\n\nСтек:\n' + traceback.format_exc()
            self.info_widget.setText(text)
            self.info_widget.show()

    def _show_serial_info(self, item):
        if self._current_serial_item == item:
            return
        else:
            self._current_serial_item = item

        logging.debug('_show_serial_info. item: %s.', item)
        serial = item.data(Qt.UserRole)
        logging.debug('_show_serial_info. serial: %s.', serial)
        self.serial_info.set_serial(serial)

    def _open_player_serial(self, serial):
        # Если окно-плеера сериала нет, добавляем, иначе показываем окно
        if serial not in self._serials_by_player_dict:
            player = PlayerWindow(serial.list_of_series, serial.name)
            self._serials_by_player_dict[serial] = player
        else:
            player = self._serials_by_player_dict[serial]

        # player.show()
        player.resize(800, 500)
        player.showNormal()

        # TODO: проверять что плеер уже запущен, и если окно плеера уже открыто, просто вывести его
        # на передний план
        player.play()

    # TODO: следить за окнами-плеерами и при их закрытии/уничтожении убирать их из своего списка
    # def eventFilter(self, QObject, QEvent):
    #     pass

    def closeEvent(self, *args, **kwargs):
        QApplication.quit()


# TODO: сохранение загрузка настроек
if __name__ == '__main__':
    app = QApplication([])

    mw = MainWindow()
    mw.resize(900, 600)
    mw.show()

    # mw._search_serials('Игра престолов')
    # for i in range(mw.serials_list_widget.count()):
    #     item = mw.serials_list_widget.item(i)
    #     if '1' in item.text():
    #         # mw.serials_list_widget.setCurrentItem(item)
    #         mw._show_serial_info(item)

    # TODO: rem
    mw.serial_search.setText('gravity')
    # mw.serial_search.setText('dfsdfsdfsdfsf')

    # list_of_series = [
    #     ('1 series', r'C:\Users\ipetrash\Desktop\7f_Gravity.Falls.S01E01.rus.vo.sienduk.a1.08.12.15.mp4'.replace('\\', '/')),
    #     ('2 series', r'C:\Users\ipetrash\Desktop\7f_Gravity.Falls.S01E01.rus.vo.sienduk.a1.08.12.15.mp4'.replace('\\', '/')),
    #     ('3 series', r'C:\Users\ipetrash\Desktop\7f_Gravity.Falls.S01E01.rus.vo.sienduk.a1.08.12.15.mp4'.replace('\\', '/')),
    #     ('4 series', r'C:\Users\ipetrash\Desktop\7f_Gravity.Falls.S01E01.rus.vo.sienduk.a1.08.12.15.mp4'.replace('\\', '/')),
    #     ('5 series', r'C:\Users\ipetrash\Desktop\7f_Gravity.Falls.S01E01.rus.vo.sienduk.a1.08.12.15.mp4'.replace('\\', '/')),
    # ]
    #
    # spw = PlayerWindow(list_of_series, 'test')
    # spw.player.setVolume(50)
    # # spw.video_widget.setFixedSize(30, 30)
    # # for dw in spw.findChildren(QDockWidget): dw.hide()
    # spw.show()
    # spw.play()
    # # QTimer.singleShot(5000, lambda x=None: a.quit())

    app.exec_()
