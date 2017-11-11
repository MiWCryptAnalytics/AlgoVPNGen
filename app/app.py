from flask import Flask, flash, redirect, request, render_template, session
from flask_bootstrap import Bootstrap
from wtforms import Form, BooleanField, StringField, SelectField, SubmitField, validators
from flask_wtf import FlaskForm
from flask_socketio import SocketIO, emit
from threading import Lock
import subprocess
import os
import io
from datetime import datetime


WTF_CSRF_SECRET_KEY = os.urandom(32)

class DigitalOceanForm(FlaskForm):
    do_access_token = StringField('Digital Ocean API Token', [
        validators.InputRequired(),
        validators.Length(min=64, max=64, message="Must be 64 Characters"),
        validators.Regexp("^[a-zA-Z0-9]*$", flags=0, message="Must be Alphanumeric")
    ])
    do_region = SelectField(
        'Digital Ocean Region',
        choices=[('ams1', 'Amsterdam 1'), ('ams2', 'Amsterdam 2'), ('ams3', 'Amsterdam 3')]
    )
    do_server_name = StringField("Server Name", [
        validators.InputRequired(),
        validators.Regexp("^[a-zA-Z0-9][a-zA-Z0-9-]*$", flags=0, message="Must be Alphanumeric and not start with -")

    ])
    submitbutton = SubmitField(label='Go')


app = Flask(__name__)
Bootstrap(app)
app.secret_key = os.urandom(32)
socketio = SocketIO(app)
thread = None
thread_lock = Lock()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/build')
def build():
    return render_template('testwebsocket.html', async_mode=socketio.async_mode)


@app.route('/test')
def test():
    return 'The app appears to be working correctly.'

@app.route('/digitalocean', methods=['GET', 'POST'])
def digitalocean():
    form = DigitalOceanForm(request.form)
    
    if form.validate_on_submit():
        string = "Will run: %s" % build_do_cmd_string(form.do_access_token.data, form.do_region.data, form.do_server_name.data)
        return render_template('build.html', status=string, async_mode=socketio.async_mode)

    if form.errors:
        for error_message in form.errors:
            flash("error : {error}".format(error=error_message))
    
    return render_template('digitalocean.html', form=form)



def ls_thread():
    proc = subprocess.Popen(["ls", "-la", "/tmp"], stdout=subprocess.PIPE)
    for line in io.TextIOWrapper(proc.stdout, encoding="utf-8"):
        socketio.emit('my_response',
                      {'data': line },
                      namespace='/tty')
    print("ls thread complete")

def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        socketio.sleep(10)
        count += 1
        socketio.emit('my_response',
                      {'data': 'Server generated event {time}'.format(time=datetime.now()), 'count': count},
                      namespace='/tty')

@socketio.on('my_event', namespace='/tty')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']})


@socketio.on('my_broadcast_event', namespace='/tty')
def test_broadcast_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']},
         broadcast=True)


@socketio.on('join', namespace='/tty')
def join(message):
    join_room(message['room'])
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'In rooms: ' + ', '.join(rooms()),
          'count': session['receive_count']})


@socketio.on('leave', namespace='/tty')
def leave(message):
    leave_room(message['room'])
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'In rooms: ' + ', '.join(rooms()),
          'count': session['receive_count']})


@socketio.on('close_room', namespace='/tty')
def close(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response', {'data': 'Room ' + message['room'] + ' is closing.',
                         'count': session['receive_count']},
         room=message['room'])
    close_room(message['room'])


@socketio.on('my_room_event', namespace='/tty')
def send_room_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']},
         room=message['room'])


@socketio.on('disconnect_request', namespace='/tty')
def disconnect_request():
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'Disconnected!', 'count': session['receive_count']})
    disconnect()


@socketio.on('connect', namespace='/tty')
def tty_connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=ls_thread)
    emit('my_response', {'data': 'Connected {sid}'.format(sid=request.sid) })


@socketio.on('disconnect', namespace='/test')
def tty_disconnect():
    print('Client disconnected', request.sid)

## Development helper functions

def build_do_cmd_string(token, region, name):
    return "heroku run -a algovpngen --type worker worker -e \"DO_ACCESS_TOKEN=%s;DO_REGION=%s;DO_SERVER_NAME=%s\"" % (token, region, name)