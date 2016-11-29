from threading import Thread, Event
import time

import RPi.GPIO as GPIO
#from EmulatorGUI import GPIO

import setup
thread_stop_event = Event()


class PowerUpThread(Thread):
    def __init__(self):
        self.delay = 1
        super(PowerUpThread, self).__init__()

    """"""
    def SequencePowerOn(self):
        #global upseqdict
        #global socketio
        self.pwruptime = self.total_time()
        print(self.pwruptime)
        accumulated_delay = 0
        while not thread_stop_event.isSet():
            # for each group in pingroups:
            # - set the pins on
            # - then wait the specified time
            # - then update the value that gets sent to the progress bar
            for pingroup in setup.pingroups:
                delaytime = pingroup['timeup']
                accumulated_delay += delaytime
                iolist = pingroup['group']
                for outputpin in iolist:
                    print(outputpin)
                    self.setpin(outputpin)
                time.sleep(delaytime)
                setup.percent_done = int((accumulated_delay/self.pwruptime) *100)
                print(setup.percent_done)
            thread_stop_event.set()
            print(thread_stop_event.isSet())

    def total_time(self):
        totalpwruptime = 0
        for grp in setup.pingroups:
            totalpwruptime = totalpwruptime + grp['timeup']
        return totalpwruptime

    def setpin(self, outputname):
        print('Output name: ' + outputname)
        setup.pindict[outputname]['state'] = GPIO.HIGH
        GPIO.output(setup.pindict[outputname]['pinnum'], setup.pindict[outputname]['state'])

    def run(self):
        thread_stop_event.clear()
        self.SequencePowerOn()

class PowerDnThread(Thread):
    def __init__(self):
        self.delay = 1
        super(PowerDnThread, self).__init__()

    """"""
    def SequencePowerOff(self):
        #global upseqdict
        #global socketio
        self.pwrdntime = self.total_time()
        print(self.pwrdntime)
        accumulated_delay = self.pwrdntime
        while not thread_stop_event.isSet():
            # for each group in pingroups:
            # - set the pins on
            # - then wait the specified time
            # - then update the value that gets sent to the progress bar
            for pingroup in reversed(setup.pingroups):
                delaytime = pingroup['timedn']
                accumulated_delay -= delaytime
                iolist = pingroup['group']
                for outputpin in iolist:
                    print(outputpin)
                    self.setpin(outputpin)
                time.sleep(delaytime)
                setup.percent_done = int((accumulated_delay/self.pwrdntime) *100)
                print(setup.percent_done)
            thread_stop_event.set()
            print(thread_stop_event.isSet())

    def total_time(self):
        totalpwrdntime = 0
        for grp in setup.pingroups:
            totalpwrdntime = totalpwrdntime + grp['timedn']
        return totalpwrdntime

    def setpin(self, outputname):
        print('Output name: ' + outputname)
        setup.pindict[outputname]['state'] = GPIO.LOW
        GPIO.output(setup.pindict[outputname]['pinnum'], setup.pindict[outputname]['state'])


    def run(self):
        thread_stop_event.clear()
        self.SequencePowerOff()