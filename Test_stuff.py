pindict = { 'LED1' : { 'pinnum':7,   'state' : 'GPIO.LOW'}, #Hdr:26
    		 'LED2' : {'pinnum':8,   'state' : 'GPIO.LOW'}, #Hdr:24
	    	 'LED3' : {'pinnum':17, 'state' : 'GPIO.LOW'}, #Hdr:11
	    	 'LED4' : {'pinnum':15, 'state' : 'GPIO.LOW'}, #Hdr:10
	    	 'LED5' : {'pinnum':18, 'state' : 'GPIO.LOW'}, #Hdr:12
	    	 'LED6' : {'pinnum':23, 'state' : 'GPIO.LOW'}, #Hdr:16
	    	 'LED7' : {'pinnum':24, 'state' : 'GPIO.LOW'}, #Hdr:18
	    	 'LED8' : {'pinnum':25, 'state' : 'GPIO.LOW'} #Hdr:22
		}


names = [ 'LED1' ,'LED2' ,'LED3' ,'LED4' ,'LED5' ,'LED6' ,'LED7' ,'LED8' ]
for name in names:
    print(name + ': {}'.format(pindict[name]['pinnum']))