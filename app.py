#!/usr/bin/env python

import signal
import sys

from threading import Thread, Event

from functools import wraps
from flask import Flask, render_template, session, request, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect

import RPi.GPIO as GPIO
#from EmulatorGUI import GPIO

import setup

from PowerSequences import PowerUpThread, PowerDnThread

async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
pwrupthread = Thread()
pwrdnthread = Thread()

def background_thread():
    """Continuous display of status to client."""
    count = 0
    while True:
        pinstate = ''
        for pin in setup.pinnames:
            pinstate = pinstate + 'Power block: {} state: {}<br>'.format(pin, setup.pindict[pin]['state'])
        socketio.emit('pwrstat',
                      {'data': pinstate},
                      namespace='/test')
        socketio.emit('pwrbar', {'progress':setup.percent_done}, namespace='/test')
        socketio.sleep(1)


loginhashappened = False
def login_required(f):
    global loginhashappened
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if loginhashappened is False:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def index():
    return render_template('index.html', async_mode=socketio.async_mode)

# route for handling the login page logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    global loginhashappened
    error = None
    if request.method == 'POST':
        if request.form['username'] != setup.userid or request.form['password'] != setup.userpwd:
            error = 'Invalid Credentials. Please try again.'
        else:
            loginhashappened = True
            return redirect(url_for('index'))
    return render_template('login.html', error=error)

@socketio.on('my_ping', namespace='/test')
def ping_pong():
    emit('my_pong')

@socketio.on('powerup', namespace='/test')
def power_up():
    global pwrupthread
    global pwrdnthread
    print('Power up request', request.sid)
    if not pwrupthread.isAlive():
        print('Starting PowerUpThread')
        pwrupthread = PowerUpThread()
        pwrupthread.start()

@socketio.on('powerdn', namespace='/test')
def power_down():
    global pwrupthread
    global pwrdnthread
    print('Power down request', request.sid)
    if not pwrdnthread.isAlive():
        print('Starting PowerDnThread')
        pwrdnthread = PowerDnThread()
        pwrdnthread.start()


@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    if thread is None:
        thread = socketio.start_background_task(target=background_thread)
    #emit('my_response', {'data': 'Connected', 'count': 0})


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)

def signal_handler(signal, frame1):
   GPIO.output(2, GPIO.HIGH)
   print('Exiting after GPIO.cleanup.')
   GPIO.cleanup()
   sys.exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    setup.read_config()
    setup.init_GPIO()
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
