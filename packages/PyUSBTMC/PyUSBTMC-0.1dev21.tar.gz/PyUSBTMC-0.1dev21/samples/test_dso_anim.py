#!/usr/bin/python
#-*- coding:utf-8 -*-
"""
PyUSBTMC usage sample.
It require matplotlib and pytz modules.

"""
from __future_ import print_function

import matplotlib
## the default backend; one of GTK GTKAgg GTKCairo CocoaAgg FltkAgg
# MacOSX QtAgg Qt4Agg TkAgg WX WXAgg Agg Cairo GDK PS PDF SVG Template
#matplotlib.use('MacOSX')
matplotlib.use('WXAgg')
#matplotlib.use('TkAgg')

import numpy as np
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import serial,json,time

import datetime,sys
import matplotlib.dates as mdates
import pytz,time

JST= pytz.timezone("Asia/Tokyo")

import PyUSBTMC
import time,types
import pylab
import time,gc
from AgilentDSO import waveform,wpreamble

class TestDSO:
    def __init__(self):
        self.osc=PyUSBTMC.USB488_device.find_all()[0] # assuming only one USBTMC is connected to the system.
        self.osc.write(":STOP;")
        #self.osc.write("*CLS;")
        self.osc.write(":WAV:FORM BYTE")
        cmd=":WAV:FORM BYTE;:WAV:POIN:MODE MAX;\n"
        self.osc.write(cmd)
        cmd=":WAV:SOUR CHAN1;\n"
        self.osc.write(cmd)
        self.osc.write(":WAV:POIN %s;\n"%100000)
        self.osc.write(":RUN;\n")
        time.sleep(0.01)
        self.osc.write(":STOP;\n")

    def get_next_wfs(self):
        print ("start next wf:",time.time())
        self.osc.write(":STOP;\n")
        self.osc.write(":DIG chan1,chan2,chan3,chan4;*WAI;\n")
        wf1=wf2=wf3=wf4=None
        try:
            wfs=map(self.get_waveform, (1,2,3,4))
            print ("got waveforms",time.time())
            return wfs
        except:
            print ("failed to get waveform")
            return None

    def get_wave_preamble(self):
        """
        <preamble_block> ::= <formatNR1>, <type NR1>,<pointsNR1>,<count NR1>,
        <xincrementNR3>, <xorigin NR3>, <xreferenceNR1>,
        <yincrement NR3>, <yoriginNR3>, <yreference NR1>
        <format> ::= an integer in NR1format:
          0 for BYTE format
          1 for WORD format
          2 for ASCii format
        <type> ::= an integer in NR1format:
          0 for NORMal type
          1 for PEAK detect type
          2 for AVERage type
          3 for HRESolution type
        <count> ::= Average count, or 1if PEAK detect type or NORMal; aninteger in NR1 format
        """
        return wpreamble(self.osc.ask(":WAV:PRE?;").split("\n")[0])
    
    def get_waveform(self,ch=1,io_timeout=3000,requestSize=4096):       
        """
        it is better to stop scanning before get waveform data on TDS.
        """
        print ("get wavefor for ",ch)
        if (type(ch) ==types.StringType):
            self.osc.write(":WAV:SOUR %s;\n"%ch)
        else:
            self.osc.write(":WAV:SOUR CHAN%d;\n"%ch)
        header=self.get_wave_preamble()
        enc=self.osc.ask(":WAV:FORM?;").strip("").split("\n")[0]
        byteo=self.osc.ask(":WAV:BYT?").strip("").split("\n")[0]
        nd=self.osc.ask(":WAV:POIN?;").split("\n")[0]
        cmd=":WAV:DATA?;\n"
        request=int(nd)
        print ("ch:",ch,"nd:",nd,"request:",request, "header",header)
        r=self.osc.ask(cmd, io_timeout=3000, 
                       requestSize=request, termCharFlag=False)
        wf=waveform(r, format=enc, byteo=byteo, preamble=header)
        return wf
        
class Viewer():
    lcolors=("y","g","m","r")
    def __init__(self,osc):
        fig, ax = plt.subplots(4,1)
        self.fig=fig
        self.ax=ax
        self.osc=osc
        self.lines=None
        self.suptitle=self.fig.suptitle("DPO4K with PyVXI11 on %s"%time.ctime())
        plt.draw()
        self.ani = animation.FuncAnimation(fig=self.fig, 
                                           func=self.update, 
                                           frames=self.emitter,
                                           init_func=None,
                                           interval=1000,
                                           blit=False)
        plt.draw()

    def Run(self,flag=True):
        plt.show(flag)

    def plot(self, wf, subp, lcol):
        pylab.subplot(4,1,subp)
        pylab.cla()
        pylab.plot(wf.x[::1000],wf.y[::10000],lcol)

    def emitter(self):
        while True:
            wfs=self.osc.get_next_wfs()
            if wfs:
                yield wfs
            time.sleep(0.01)
    #
    def update(self,wfs):
        if self.lines:
            for l, wf in zip(self.lines,wfs):
                if wf:
                    l.set_data(wf.x[::10],wf.y[::10])
                    ax=l.get_axes()
                    ax.set_xlim(min(wf.x),max(wf.x))
                    ax.set_ylim(min(wf.y),max(wf.y))
                else:
                    l.get_axes().cla()
        else:
            self.lines= [ax.plot(wf.x[::10],wf.y[::10],lcol)[0] 
                    for ax,wf,lcol in zip(self.ax,wfs,self.lcolors)]
        self.suptitle.set_text("DPO4K with PyVXI11 on %s"%time.ctime())        
        plt.draw()
        return self.lines
    
def test():
    osc=TestDSO()
    viewer=Viewer(osc)
    viewer.Run()

if __name__ == "__main__":
    test()
    
