import os.path
import configparser

import RPi.GPIO as GPIO
#from EmulatorGUI import GPIO

GPIO.setmode(GPIO.BCM)

config = configparser.ConfigParser()
config.sections()

inifound = False
PATH = '/home/mac/.rackseq/rackseq.ini'
#PATH = '/home/pi/.rackseq/rackseq.ini'
if os.path.isfile(PATH) and os.access(PATH, os.R_OK):
    inifound = True
    config.read(PATH)

percent_done = 0

userid = 'admin'
userpwd = 'admin'

pinnames = [ 'LED1' ,'LED2' ,'LED3' ,'LED4' ,'LED5' ,'LED6' ,'LED7' ,'LED8' ]

pingroups = [	{'group':['LED1','LED2'],	'timeup': 1, 'timedn': 1},
            {'group':['LED3'],				'timeup': 1, 'timedn': 1},
            {'group':['LED4'],				'timeup': 1, 'timedn': 1},
            {'group':['LED5'],				'timeup': 1, 'timedn': 1},
            {'group':['LED6'],    			'timeup': 0, 'timedn': 0},
            {'group':['LED7'],    			'timeup': 0, 'timedn': 0},
            {'group':['LED8'],     			'timeup': 0, 'timedn': 0}]

pindict = { 'LED1' : { 'pinnum':7,   'state' : GPIO.LOW}, #Hdr:26
             'LED2' : {'pinnum':8,   'state' : GPIO.LOW}, #Hdr:24
             'LED3' : {'pinnum':17, 'state' : GPIO.LOW}, #Hdr:11
             'LED4' : {'pinnum':15, 'state' : GPIO.LOW}, #Hdr:10
             'LED5' : {'pinnum':18, 'state' : GPIO.LOW}, #Hdr:12
             'LED6' : {'pinnum':23, 'state' : GPIO.LOW}, #Hdr:16
             'LED7' : {'pinnum':24, 'state' : GPIO.LOW}, #Hdr:18
             'LED8' : {'pinnum':25, 'state' : GPIO.LOW} #Hdr:22
        }

def read_config():
    print('Reading config.')
    read_creds()
    read_pins()
    read_groups()
    return

def read_creds():
    global userid, userpwd
    if not inifound:  # no ini file, so use default
        return
    try:
        userid = config.get('creds', 'userid')
    except:
        pass
    try:
        userpwd = config.get('creds', 'userpwd')
    except:
        pass
    return


def read_pins():
    global pindict
    if not inifound: #no ini file, so use default
        return
    pindict = {}
    pincount = config.getint('counts','pins')
    phypins = config.items('pins_physical')
    for pin in range(pincount):
        try:
            #pindict['LED{}'.format(pin)]['pinnum'] = config['pins_physical']['LED{}'.format(pin)]
            pindict['LED{}'.format(pin + 1)] = { 'pinnum' : int(phypins[pin][1]),
                                             'state' : GPIO.LOW}
        except:
            pass
    return

def read_groups():
    global pingroups
    if not inifound: #no ini file, so use default
        return
    pingroups = []
    groupcount = config.getint('counts','groups')
    pin_groups = config.items('pin_groups')
    group_uptimes = config.items('group_uptimes')
    group_dntimes = config.items('group_dntimes')
    for grp in range(groupcount):
        print(grp)
        try:
            pingroups.append( {'group': pin_groups[grp][1].split(','),
                              'timeup': int(group_uptimes[grp][1]),
                              'timedn': int(group_dntimes[grp][1])})
        except:
            pass
    return

def init_GPIO():
    for pin in pindict:
        GPIO.setup(pindict[pin]['pinnum'], GPIO.OUT)
        GPIO.output(pindict[pin]['pinnum'], GPIO.LOW)

    # Set enable output pin on 74244 buffer
    GPIO.setup(2, GPIO.OUT)
    GPIO.output(2, GPIO.LOW)


if __name__ == '__main__':
    read_config()
    print('pindict:')
    pincount = len(pindict)
    for pin in range(1, pincount + 1):
        print('LED{}: '.format(pin) +
                 'Num: {}'.format(pindict['LED{}'.format(pin)]['pinnum']) +
              ' State: {}'.format(pindict['LED{}'.format(pin)]['state']))
    grpcount = len(pingroups)
    for grp in range(grpcount):
        print('Pin Group: {}'.format(pingroups[grp]['group']) + ' Up time: {}'.format(pingroups[grp]['timeup']) + ' Up time: {}'.format(pingroups[grp]['timedn']))
    init_GPIO()
    print('userid: {}'.format(userid))
    print('userpwd: {}'.format(userpwd))