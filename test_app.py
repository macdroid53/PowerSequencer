#!/usr/bin/env python
from functools import wraps
from flask import Flask, render_template, session, request, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect


async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)

@app.route('/')
def index():
    return render_template('index_test.html')


if __name__ == '__main__':
    socketio.run(app, debug=True)
