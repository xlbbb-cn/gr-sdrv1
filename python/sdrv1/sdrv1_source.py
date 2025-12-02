#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2025 leonard.wang.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
## https://wiki.gnuradio.org/index.php/OutOfTreeModules
## https://wiki.gnuradio.org/index.php?title=Creating_Python_OOT_with_gr-modtool
## https://wiki.gnuradio.org/index.php/Stream_Tags

import numpy
from gnuradio import gr
import iio
import struct
from .utils import io_ctx # 导入 io_ctx


class sdrv1_source_fc32(gr.sync_block):
    """
    docstring for block sdrv1_source
    """
    def __init__(self, ip,chn,buffersize):
        gr.sync_block.__init__(self,
            name="sdrv1_source",
            in_sig=None,
            out_sig=[numpy.complex64, ])
        
        self._freq=0
        ctx_key = f"iio_network_context_{ip}"
        self._ctx = io_ctx().query_context(ctx_key)
        
        if not self._ctx:
            # 如果 io_ctx 中没有，则创建并保存
            try:
                self._ctx = iio.NetworkContext(ip)
                io_ctx().set_context(ctx_key, io_ctx().phy_name)
            except Exception as e:
                raise Exception(f"Failed to create IIO NetworkContext for IP {ip}: {e}")
        self._device=self._ctx.find_device("nrf9022-phy")
        if not self._device:
            raise Exception("cant fond phy")
        

    
        
        self._stream=self._ctx.find_device(io_ctx().rxstream_name)
        if not self._stream:
            raise Exception("cant fond rx stream device")
        
        self._rx1_chi=self._stream.find_channel('voltage0',False)
        self._rx1_chq=self._stream.find_channel('voltage1',False)
        self._rx2_chi=self._stream.find_channel('voltage2',False)
        self._rx2_chq=self._stream.find_channel('voltage3',False)
        self._buf_size=buffersize
        self._chn=chn
        
        Val=self._stream.reg_read(0x0)
        Val= Val & (~(0x3<<2))

        if chn == 'rx1':
            self._rx1_chi.enabled=True
            self._rx1_chq.enabled=True
            self._rx2_chi.enabled=False
            self._rx2_chq.enabled=False
            self._stream.reg_write(0x0,Val|(0x1 <<2))
        elif chn == "rx2":
            self._rx1_chi.enabled=False
            self._rx1_chq.enabled=False
            self._rx2_chi.enabled=True
            self._rx2_chq.enabled=True
            self._stream.reg_write(0x0,Val|(0x2 <<2))
        else:
            raise  Exception("chn must in rx1 / rx2")
        
        
        self._buf=iio.Buffer(self._stream,self._buf_size,False)
        self._tmp_data=[]
        
    def get_ch(self,ch_name):
        for ch in self._device.channels:
            if ch.name == ch_name:
                return ch
        return None
        
        
    def set_rx_gain(self,gain):
        
        if self._chn == "rx1" :
            self._device.debug_attrs["api"].value=f"tssetgain 2 {gain}"
        else:
            self._device.debug_attrs["api"].value=f"tssetgain 3 {gain}" 
            
        print(f"====>set rx gain to {gain},{self._device.debug_attrs["api"].value}")   
        

    def set_fs(self,fs):
        print(f"====>set fs to {fs}")
        self._device.attrs["sampling_frequency"].value=str(int(fs))

    def set_bw(self,bw):
        print(f"====>set rx analog filter bw to {bw}")
        chn=self.get_ch(self._chn)
        if chn:
            chn.attrs["bandwidth"].value =str(int(bw))

    def set_lo(self,lo):
        print(f"====>set rx lo to {lo}")
        chn=self.get_ch("LO2")
        if chn:
            chn.attrs["frequency"].value =str(int(lo))
    
        if abs(self._freq - lo) > 200e6:
            self._device.debug_attrs["api"].value="tsdcoc 1 1" if self._chn=="rx1" else "tsdcoc 2 1"
            print(f"dcoc => {self._device.debug_attrs["api"].value}")
            # do cal;
            self._freq=lo
            

    def work(self, input_items, output_items):
        out = output_items[0]
        noutput_items=len(out)
        
        
        
        while noutput_items > len(self._tmp_data):
            self._buf.refill()
            data_i=[]
            data_q=[]
            if self._chn == 'rx1':
                data_i=self._rx1_chi.read(self._buf)
                data_q=self._rx1_chq.read(self._buf)    
            if self._chn == 'rx2':
                data_i=self._rx2_chi.read(self._buf)
                data_q=self._rx2_chq.read(self._buf)
            data_i = struct.unpack("<"+"h"*self._buf_size,data_i)
            data_q = struct.unpack("<"+"h"*self._buf_size,data_q)
            data_ =  (numpy.array(data_i,dtype=numpy.float32)+numpy.array(data_q,dtype=numpy.float32)*1j) / 2048.0
            self._tmp_data=numpy.hstack((numpy.array(self._tmp_data) ,data_))
            # print(f"==>{ len(self._tmp_data)}")
                    
        out[:] = self._tmp_data[:noutput_items]
        self._tmp_data=self._tmp_data[noutput_items:]
        
        # test stream tags
        # indx=50
        # key = pmt.intern("k")
        # value = pmt.intern("v")
        # self.add_item_tag(0, # Write to output port 0
        #                   self.nitems_written(0) + indx, # Index of the tag in absolute terms
        #                   key, # Key of the tag
        #                   value # Value of the tag
        #                 )
                 
        return noutput_items

