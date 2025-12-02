#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2025 leonard.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


import numpy as np
from gnuradio import gr
import iio
import struct
from .utils import io_ctx # 导入 io_ctx

class sdrv1_sink(gr.sync_block):
    """
    docstring for block sdrv1_sink
    """
    def __init__(self, ip,chn,buffersize):
        gr.sync_block.__init__(self,
            name="sdrv1_sink",
            in_sig=[np.complex64, ],
            out_sig=None)
        self._chn=chn
        self._buf_size=buffersize
        self._freq=0
            
        ctx_key = f"iio_network_context_{ip}"
        self._ctx = io_ctx().query_context(ctx_key)
        
        if not self._ctx:
            # 如果 io_ctx 中没有，则创建并保存
            try:
                self._ctx = iio.NetworkContext(ip)
                io_ctx().set_context(ctx_key, self._ctx)
            except Exception as e:
                raise Exception(f"Failed to create IIO NetworkContext for IP {ip}: {e}")
        self._device=self._ctx.find_device( io_ctx().phy_name)
        if not self._device:
            raise Exception("cant fond phy")
        self._stream_reg=self._ctx.find_device( io_ctx().rxstream_name)
        if not self._stream_reg:
            raise Exception("cant fond tx stream control device")
        self._stream=self._ctx.find_device( io_ctx().txstream_name)
        if not self._stream:
            raise Exception("cant fond tx stream device")

        self._tx1_chi=self._stream.find_channel('voltage0',True)
        self._tx1_chq=self._stream.find_channel('voltage1',True)
        self._tx2_chi=self._stream.find_channel('voltage2',True)
        self._tx2_chq=self._stream.find_channel('voltage3',True)
        
        Val=self._stream_reg.reg_read(0x0)
        Val= Val & (~0x3)
        
        if chn == 'tx1':
            self._tx1_chi.enabled=True
            self._tx1_chq.enabled=True
            self._tx2_chi.enabled=False
            self._tx2_chq.enabled=False
            self._stream_reg.reg_write(0x0,Val|(0x1))
            
        elif chn == "tx2":
            self._tx1_chi.enabled=False
            self._tx1_chq.enabled=False
            self._tx2_chi.enabled=True
            self._tx2_chq.enabled=True
            self._stream_reg.reg_write(0x0,Val|(0x2))
        else:
            raise  Exception("chn must in tx1 / tx2")
        
        self._buf=iio.Buffer(self._stream,self._buf_size,False)
        if(not self._buf):
            raise  Exception("cant create tx buffer")
        
        self.indata=[]
    
    def get_ch(self,ch_name):
        for ch in self._device.channels:
            if ch.name == ch_name:
                return ch
        return None
    
    def set_tx_gain(self,gain):
        if self._chn == "tx1" :
            self._device.debug_attrs["api"].value=f"tssetgain 0 {gain}"
        else:
            self._device.debug_attrs["api"].value=f"tssetgain 1 {gain}" 
            
        print(f"====>set tx gain to {gain},{self._device.debug_attrs["api"].value}")   
        

    def set_fs(self,fs):
        print(f"====>set fs to {fs}")
        self._device.attrs["sampling_frequency"].value=str(int(fs))
        
        
    def set_bw(self,bw):
        print(f"====>set tx analog bw to {bw}")
        chn=self.get_ch(self._chn)
        if chn:
            chn.attrs["bandwidth"].value =str(int(bw))

    def set_lo(self,lo):
        print(f"====>set tx lo to {lo}")
        chn=self.get_ch("LO1")
        if chn:
            chn.attrs["frequency"].value =str(int(lo))
            
        if abs(self._freq - lo) > 200e6:
            self._device.debug_attrs["api"].value="tstxcal 1" if self._chn=="tx1" else "tstxcal 2"
            print(f"txcal => {self._device.debug_attrs["api"].value}")
            self._freq=lo

    def work(self, input_items, output_items):
        self.indata.extend(input_items[0])
        indata_len=len(self.indata)
        
        if indata_len < self._buf_size:
            return len(input_items[0])
        else:
            data = np.array( self.indata[:self._buf_size])
            max_val = np.max(np.abs(data))
            if max_val > 1:
                raise Exception("max value > 1!!!!value error")
                
            in0_scaled = data  * 32767.0
            
            real_part = in0_scaled.real.astype(np.int16)
            imag_part = in0_scaled.imag.astype(np.int16)
            
            # # 交错实部和虚部，形成 int16 序列
            # # 例如：[real0, imag0, real1, imag1, ...]
            ptmp = np.stack((real_part, imag_part), axis=-1).flatten()
            ptmp = ptmp.tolist()
            
            bdata=struct.pack('<'+'h'*self._buf_size*2,*ptmp)
            self._buf.write(bytearray(bdata))
            self._buf.push()
            
            self.indata=self.indata[self._buf_size:]

        return len(input_items[0])