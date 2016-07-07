#!/usr/bin/env python3
# -*- coding: utf-8 -*-


__author__ = 'ipetrash'


from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *

a = QApplication([])

playlist = QMediaPlaylist()
playlist.addMedia(QMediaContent(QUrl("http://data06-cdn.datalock.ru/fi2lm/953324b302d8aca1ca76975fe7055e44/7f_Gravity.Falls.S01E18.rus.vo.sienduk.a0.08.12.15.mp4")))
playlist.setCurrentIndex(0)

player = QMediaPlayer()
player.setPlaylist(playlist)

videoWidget = QVideoWidget()
player.setVideoOutput(videoWidget)
videoWidget.show()

videoWidget.resize(200, 200)

mw = QMainWindow()
mw.setCentralWidget(videoWidget)
mw.show()

player.play()

a.exec_()
