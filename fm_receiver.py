#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: FM Receiver
# Author: leonard
# Copyright: NJAVC
# GNU Radio version: 3.10.12.0

from PyQt5 import Qt
from gnuradio import qtgui
from PyQt5 import QtCore
from gnuradio import analog
from gnuradio import audio
from gnuradio import blocks
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import sdrv1
import sip
import threading



class fm_receiver(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "FM Receiver", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("FM Receiver")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except BaseException as exc:
            print(f"Qt GUI: Could not set Icon: {str(exc)}", file=sys.stderr)
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "fm_receiver")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)
        self.flowgraph_started = threading.Event()

        ##################################################
        # Variables
        ##################################################
        self.exLNA_gain = exLNA_gain = 22
        self.samp_rate = samp_rate = 1e6
        self.rx_real_gain_val = rx_real_gain_val = exLNA_gain
        self.qtgui_msgdigitalnumbercontrol_0 = qtgui_msgdigitalnumbercontrol_0 = 110e6
        self.f_offset = f_offset = 0
        self.audio_rate_pre = audio_rate_pre = 192e3

        ##################################################
        # Blocks
        ##################################################

        self._rx_real_gain_val_range = qtgui.Range(exLNA_gain+0, exLNA_gain+77, 1, exLNA_gain, 200)
        self._rx_real_gain_val_win = qtgui.RangeWidget(self._rx_real_gain_val_range, self.set_rx_real_gain_val, "rx gain", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._rx_real_gain_val_win)
        self._qtgui_msgdigitalnumbercontrol_0_msgdigctl_win = qtgui.MsgDigitalNumberControl(lbl='Rx1 LO', min_freq_hz=30e6, max_freq_hz=5000e6, parent=self, thousands_separator=",", background_color="black", fontColor="green", var_callback=self.set_qtgui_msgdigitalnumbercontrol_0, outputmsgname='freq')
        self._qtgui_msgdigitalnumbercontrol_0_msgdigctl_win.setValue(110e6)
        self._qtgui_msgdigitalnumbercontrol_0_msgdigctl_win.setReadOnly(False)
        self.qtgui_msgdigitalnumbercontrol_0 = self._qtgui_msgdigitalnumbercontrol_0_msgdigctl_win

        self.top_grid_layout.addWidget(self._qtgui_msgdigitalnumbercontrol_0_msgdigctl_win, 0, 0, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._f_offset_range = qtgui.Range(-samp_rate/1e3, samp_rate/1e3, 1, 0, 200)
        self._f_offset_win = qtgui.RangeWidget(self._f_offset_range, self.set_f_offset, "freq_offset(khz)", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._f_offset_win)
        self.sdrv1_sdrv1_source_0 = sdrv1.sdrv1_source_fc32('192.168.50.11', 'rx1',8192)
        self.sdrv1_sdrv1_source_0.set_lo(qtgui_msgdigitalnumbercontrol_0)
        self.sdrv1_sdrv1_source_0.set_fs(samp_rate)
        self.sdrv1_sdrv1_source_0.set_bw(samp_rate)
        self.sdrv1_sdrv1_source_0.set_rx_gain((rx_real_gain_val-exLNA_gain))
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
                interpolation=1,
                decimation=(int(samp_rate/audio_rate_pre)),
                taps=[],
                fractional_bw=0.4)
        self.qtgui_sink_x_0 = qtgui.sink_c(
            4096, #fftsize
            window.WIN_HANN, #wintype
            0, #fc
            samp_rate, #bw
            "fin", #name
            True, #plotfreq
            True, #plotwaterfall
            True, #plottime
            False, #plotconst
            None # parent
        )
        self.qtgui_sink_x_0.set_update_time(1.0/10)
        self._qtgui_sink_x_0_win = sip.wrapinstance(self.qtgui_sink_x_0.qwidget(), Qt.QWidget)

        self.qtgui_sink_x_0.enable_rf_freq(True)

        self.top_grid_layout.addWidget(self._qtgui_sink_x_0_win, 1, 0, 50, 50)
        for r in range(1, 51):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 50):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.blocks_rotator_cc_0 = blocks.rotator_cc((6.282*f_offset*1e3/samp_rate), False)
        self.blocks_correctiq_0 = blocks.correctiq()
        self.audio_sink_0 = audio.sink(48000, '', True)
        self.analog_fm_demod_cf_0 = analog.fm_demod_cf(
        	channel_rate=audio_rate_pre,
        	audio_decim=(int(audio_rate_pre/48e3)),
        	deviation=75000,
        	audio_pass=15000,
        	audio_stop=16000,
        	gain=1.0,
        	tau=(75e-6),
        )


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_fm_demod_cf_0, 0), (self.audio_sink_0, 0))
        self.connect((self.blocks_correctiq_0, 0), (self.blocks_rotator_cc_0, 0))
        self.connect((self.blocks_rotator_cc_0, 0), (self.qtgui_sink_x_0, 0))
        self.connect((self.blocks_rotator_cc_0, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.analog_fm_demod_cf_0, 0))
        self.connect((self.sdrv1_sdrv1_source_0, 0), (self.blocks_correctiq_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "fm_receiver")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_exLNA_gain(self):
        return self.exLNA_gain

    def set_exLNA_gain(self, exLNA_gain):
        self.exLNA_gain = exLNA_gain
        self.set_rx_real_gain_val(self.exLNA_gain)
        self.sdrv1_sdrv1_source_0.set_rx_gain((self.rx_real_gain_val-self.exLNA_gain))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.blocks_rotator_cc_0.set_phase_inc((6.282*self.f_offset*1e3/self.samp_rate))
        self.qtgui_sink_x_0.set_frequency_range(0, self.samp_rate)
        self.sdrv1_sdrv1_source_0.set_fs(self.samp_rate)
        self.sdrv1_sdrv1_source_0.set_bw(self.samp_rate)

    def get_rx_real_gain_val(self):
        return self.rx_real_gain_val

    def set_rx_real_gain_val(self, rx_real_gain_val):
        self.rx_real_gain_val = rx_real_gain_val
        self.sdrv1_sdrv1_source_0.set_rx_gain((self.rx_real_gain_val-self.exLNA_gain))

    def get_qtgui_msgdigitalnumbercontrol_0(self):
        return self.qtgui_msgdigitalnumbercontrol_0

    def set_qtgui_msgdigitalnumbercontrol_0(self, qtgui_msgdigitalnumbercontrol_0):
        self.qtgui_msgdigitalnumbercontrol_0 = qtgui_msgdigitalnumbercontrol_0
        self.sdrv1_sdrv1_source_0.set_lo(self.qtgui_msgdigitalnumbercontrol_0)

    def get_f_offset(self):
        return self.f_offset

    def set_f_offset(self, f_offset):
        self.f_offset = f_offset
        self.blocks_rotator_cc_0.set_phase_inc((6.282*self.f_offset*1e3/self.samp_rate))

    def get_audio_rate_pre(self):
        return self.audio_rate_pre

    def set_audio_rate_pre(self, audio_rate_pre):
        self.audio_rate_pre = audio_rate_pre




def main(top_block_cls=fm_receiver, options=None):

    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()
    tb.flowgraph_started.set()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
