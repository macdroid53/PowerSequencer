Python/PYQT/FLASK code that sequences the Raspberry Pi GPIO.
The sequence of the GPIO pins is based on a group/pin/time defined in a configuration file.
The configuration file defines a username/password required to access the web interface.
The configuration file also defines the up and down times for each pin grouping.
The pin group is activated, then the softwares waits the defined time then proceeds to the next pin group.
The coded looks for the configuration file in <user>/.rackseq/rackseq.ini. Both .rackseq and rackseq.ini must exist.