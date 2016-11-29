#!/usr/bin/env python

from threading import Thread, Event

from functools import wraps
from flask import Flask, render_template, session, request, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect


import setup

from PowerSequences import PowerUpThread, PowerDnThread

# Create a dictionary called pins to store the pin number, name, and pin state:
class GPIO():
    LOW = 0

pins = {
   7 : {'name' : 'LED1', 'state' : GPIO.LOW}, #Hdr:26
   8 : {'name' : 'LED2', 'state' : GPIO.LOW}, #Hdr:24
   17 : {'name' : 'LED3', 'state' : GPIO.LOW}, #Hdr:11
   15 : {'name' : 'LED4', 'state' : GPIO.LOW}, #Hdr:10
   18 : {'name' : 'LED5', 'state' : GPIO.LOW}, #Hdr:12
   23 : {'name' : 'LED6', 'state' : GPIO.LOW}, #Hdr:16
   24 : {'name' : 'LED7', 'state' : GPIO.LOW}, #Hdr:18
   25 : {'name' : 'LED8', 'state' : GPIO.LOW} #Hdr:22
   }


# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
pwrupthread = Thread()
pwrdnthread = Thread()

#upseqdict = [{'name':'Pwr Blk 1', 'delay':4},{'name':'Pwr Blk 2', 'delay':5}]

# pinlist = [{'pinnum':7,'name' : 'LED1', 'state' : 'GPIO.LOW'},
#            {'pinnum':8,'name' : 'LED2', 'state' : 'GPIO.LOW'},
#            {'pinnum':17,'name' : 'LED3', 'state' : 'GPIO.LOW'}]

def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        #print('pulse')
        #socketio.sleep(5)
        count += 1
        #socketio.emit('my_response',
        #              {'data': 'Server generated event', 'count': count},
        #              namespace='/test')
        # socketio.emit('pwrstat',
        #               {'data': 'Server generated event', 'count': count},
        #               namespace='/test')
        pinstate = ''
        for pin in setup.pinnames:
            pinstate = pinstate + 'Power block: {} state: {}<br>'.format(pin, setup.pindict[pin]['state'])
        # for pin in range(len(pinlist)):
        #     #print('%done from background: {}'.format(setup.percent_done))
        #     pinstate = pinstate + 'Name: {}'.format(pinlist[pin]['name']) + ' State: {}'.format(pinlist[pin]['state']) + '<br>'
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
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            loginhashappened = True
            return redirect(url_for('index'))
    return render_template('login.html', error=error)

# @socketio.on('my_event', namespace='/test')
# def test_message(message):
#     session['receive_count'] = session.get('receive_count', 0) + 1
#     emit('my_response',
#          {'data': message['data'], 'count': session['receive_count']})


# @socketio.on('my_broadcast_event', namespace='/test')
# def test_broadcast_message(message):
#     session['receive_count'] = session.get('receive_count', 0) + 1
#     emit('my_response',
#          {'data': message['data'], 'count': session['receive_count']},
#          broadcast=True)


# @socketio.on('join', namespace='/test')
# def join(message):
#     join_room(message['room'])
#     session['receive_count'] = session.get('receive_count', 0) + 1
#     emit('my_response',
#          {'data': 'In rooms: ' + ', '.join(rooms()),
#           'count': session['receive_count']})


# @socketio.on('leave', namespace='/test')
# def leave(message):
#     leave_room(message['room'])
#     session['receive_count'] = session.get('receive_count', 0) + 1
#     emit('my_response',
#          {'data': 'In rooms: ' + ', '.join(rooms()),
#           'count': session['receive_count']})


# @socketio.on('close_room', namespace='/test')
# def close(message):
#     session['receive_count'] = session.get('receive_count', 0) + 1
#     emit('my_response', {'data': 'Room ' + message['room'] + ' is closing.',
#                          'count': session['receive_count']},
#          room=message['room'])
#     close_room(message['room'])


# @socketio.on('my_room_event', namespace='/test')
# def send_room_message(message):
#     session['receive_count'] = session.get('receive_count', 0) + 1
#     emit('my_response',
#          {'data': message['data'], 'count': session['receive_count']},
#          room=message['room'])


# @socketio.on('disconnect_request', namespace='/test')
# def disconnect_request():
#     session['receive_count'] = session.get('receive_count', 0) + 1
#     emit('my_response',
#          {'data': 'Disconnected!', 'count': session['receive_count']})
#     disconnect()


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
    emit('my_response', {'data': 'Connected', 'count': 0})


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)


if __name__ == '__main__':
    socketio.run(app, debug=True)
