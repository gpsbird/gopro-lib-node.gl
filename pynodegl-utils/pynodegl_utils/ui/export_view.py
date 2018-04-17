#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2018 GoPro Inc.
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#

import subprocess
from PyQt5 import QtCore, QtWidgets
from fractions import Fraction

from pynodegl_utils.export import Exporter


class ExportView(QtWidgets.QWidget):

    def __init__(self, get_scene_func, config):
        super(ExportView, self).__init__()

        self._framerate = config.get('framerate')
        self._aspect_ratio = config.get('aspect_ratio')

        self._ofile_text = QtWidgets.QLineEdit('/tmp/ngl-export.mp4')
        ofile_btn = QtWidgets.QPushButton('Browse')

        file_box = QtWidgets.QHBoxLayout()
        file_box.addWidget(self._ofile_text)
        file_box.addWidget(ofile_btn)

        self._spinbox_width = QtWidgets.QSpinBox()
        self._spinbox_width.setRange(1, 0xffff)
        self._spinbox_width.setValue(800)

        self._spinbox_height = QtWidgets.QSpinBox()
        self._spinbox_height.setRange(1, 0xffff)
        self._spinbox_height.setValue(600)

        self._encopts_text = QtWidgets.QLineEdit()

        self._export_btn = QtWidgets.QPushButton('Export')

        self._pgbar = QtWidgets.QProgressBar()
        self._pgbar.hide()

        self._warning_label = QtWidgets.QLabel()
        self._warning_label.setStyleSheet('color: red')
        self._warning_label.hide()

        form = QtWidgets.QFormLayout(self)
        form.addRow('Filename:', file_box)
        form.addRow('Width:',    self._spinbox_width)
        form.addRow('Height:',   self._spinbox_height)
        form.addRow('Extra encoder arguments:', self._encopts_text)
        form.addRow(self._warning_label)
        form.addRow(self._export_btn)
        form.addRow(self._pgbar)

        self._exporter = Exporter(get_scene_func)
        self._exporter.progressed.connect(self._pgbar.setValue)

        ofile_btn.clicked.connect(self._select_ofile)
        self._export_btn.clicked.connect(self._export)
        self._ofile_text.textChanged.connect(self._check_settings)
        self._spinbox_width.valueChanged.connect(self._check_settings)
        self._spinbox_height.valueChanged.connect(self._check_settings)

    def enter(self):
        self._check_settings()

    @QtCore.pyqtSlot()
    def _check_settings(self):

        warnings = []

        if self._ofile_text.text().endswith('.gif'):
            fr = self._framerate
            gif_recommended_framerate = (Fraction(25, 1), Fraction(50, 1))
            if Fraction(*fr) not in gif_recommended_framerate:
                gif_framerates = ', '.join('%s' % x for x in gif_recommended_framerate)
                warnings.append('It is recommended to use one of these frame rate when exporting to GIF: {}'.format(gif_framerates))

        width = self._spinbox_width.value()
        height = self._spinbox_height.value()
        if Fraction(width, height) != Fraction(*self._aspect_ratio):
            warnings.append('width/height does not match specified aspect ratio {}'.format(self._aspect_ratio))

        if warnings:
            self._warning_label.setText('\n'.join(warnings))
            self._warning_label.show()
        else:
            self._warning_label.hide()

    @QtCore.pyqtSlot(tuple)
    def set_frame_rate(self, fr):
        self._framerate = fr
        self._check_settings()

    @QtCore.pyqtSlot(tuple)
    def set_aspect_ratio(self, ar):
        self._aspect_ratio = ar
        self._check_settings()

    @QtCore.pyqtSlot()
    def _export(self):
        ofile = self._ofile_text.text()
        width = self._spinbox_width.value()
        height = self._spinbox_height.value()

        extra_enc_args = self._encopts_text.text().split()

        self._pgbar.setValue(0)
        self._pgbar.show()
        cfg = self._exporter.export(ofile, width, height, extra_enc_args)
        if not cfg:
            QtWidgets.QMessageBox.critical(self, 'Error',
                                           "You didn't select any scene to export.",
                                           QtWidgets.QMessageBox.Ok)
        self._pgbar.hide()

    @QtCore.pyqtSlot()
    def _select_ofile(self):
        filenames = QtWidgets.QFileDialog.getSaveFileName(self, 'Select export file')
        if not filenames[0]:
            return
        self._ofile_text.setText(filenames[0])
