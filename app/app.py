from flask import Flask, flash, redirect, request, render_template, session
from flask_session import Session
from flask_bootstrap import Bootstrap
from wtforms import Form, BooleanField, StringField, SelectField, SubmitField, validators
from flask_wtf import FlaskForm
from flask_socketio import SocketIO, emit, join_room, leave_room
from threading import Lock
import subprocess
import os
import shlex
import io
import hashlib
from datetime import datetime
import time



# https://blog.miguelgrinberg.com/post/flask-socketio-and-the-user-session
app = Flask(__name__)
app.secret_key = os.urandom(32)
WTF_CSRF_SECRET_KEY = os.urandom(32)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600
Session(app)
socketio = SocketIO(app, manage_session=False, ping_timeout=30, ping_interval=5)
Bootstrap(app)


# to hold global socketio thread for cmd outputs
threads = {}
workers = {}
sockets = {}


# from https://gist.github.com/ericremoreynolds/dbea9361a97179379f3b Taiiwo
# Object that represents a socket connection
class Socket:
    def __init__(self, sid, namespace):
        self.sid = sid
        self.connected = True
        self.namespace = namespace
    # Emits data to a socket's unique room
    def emit(self, event, data):
        print("sending %s to %s" % (data, event))
        room = hashlib.sha256(self.sid.encode('utf-8')).hexdigest()
        emit(event, data, room=room, namespace=self.namespace)

class DigitalOceanForm(FlaskForm):
    do_access_token = StringField('Digital Ocean API Token', [
        validators.InputRequired(),
        validators.Length(min=64, max=64, message="Must be 64 Characters"),
        validators.Regexp("^[a-zA-Z0-9]*$", flags=0, message="Must be Alphanumeric")
    ])
    do_region = SelectField(
        'Digital Ocean Region',
        choices=[
          ('ams2', 'Amsterdam Datacenter 2'),
          ('ams3', 'Amsterdam Datacenter 3'),
          ('fra1', 'Frankfurt'),
          ('lon1', 'London'),
          ('nyc1', 'New York Datacenter 1'),
          ('nyc2', 'New York Datacenter 2'),
          ('nyc3', 'San Francisco Datacenter 1'),
          ('sfo2', 'San Francisco Datacenter 2'),
          ('sgp1', 'Singapore'),
          ('tor1', 'Toronto'),
          ('blr1', 'Bangalore'),
        ]
    )
    do_server_name = StringField("Server Name", [
        validators.InputRequired(),
        validators.Regexp("^[a-zA-Z0-9][a-zA-Z0-9-]*$", flags=0, message="Must be Alphanumeric and not start with -")

    ])
    submitbutton = SubmitField(label='Go')



@app.route('/')
def index():
    return render_template('index.html')

#@app.route('/build')
#def build():
#    roomhash = hashlib.sha256(session.sid.encode('utf-8')).hexdigest()
#    return render_template('build.html', async_mode=socketio.async_mode, roomhash=roomhash)


@app.route('/test')
def test():
    return 'The app appears to be working correctly.'

@app.route('/digitalocean', methods=['GET', 'POST'])
def digitalocean():
    form = DigitalOceanForm(request.form)
    
    if form.validate_on_submit():
        session['DO_ACCESS_TOKEN'] = form.do_access_token.data
        session['DO_REGION'] = form.do_region.data
        session['DO_SERVER_NAME'] = form.do_server_name.data
        session['READY_TO_PROVISION'] = True
        roomhash = hashlib.sha256(session.sid.encode('utf-8')).hexdigest()
        return render_template('build.html', async_mode=socketio.async_mode, roomhash=roomhash)

    if form.errors:
        for error_message in form.errors:
            flash("error : {error}".format(error=error_message))
    
    return render_template('digitalocean.html', form=form)

@app.route('/doaction', methods=['POST'])
def doaction():
  global sockets
  if not session.sid in sockets:
    return "Error: No connected websocket for {sid}".format(sid=session.sid)

  if not ('DO_ACCESS_TOKEN' in session and 'DO_REGION' in session and 'DO_SERVER_NAME' in session):
    return 'Error: Missing credentails'
  
  line = ""
  room = hashlib.sha256(session.sid.encode('utf-8')).hexdigest()
    
  if session['DO_ACCESS_TOKEN'] and session['DO_REGION'] and session['DO_SERVER_NAME']:
    if not session['READY_TO_PROVISION']:
      return "You have already started the build with this session. Please log in to your provider and remove any stale server that may have been created."
    else:
      dot = shlex.quote(session['DO_ACCESS_TOKEN'])
      dr = shlex.quote(session['DO_REGION'])
      sn = shlex.quote(session['DO_SERVER_NAME'])
      global workers
      workers[session.sid] = {'shell': build_do_cmd_string(dot, dr, sn), 'name': 'Run heroku to build %s in %s' % (sn, dr)}
      session['READY_TO_PROVISION']=False
      return "Starting build...\n(This can take a few seconds to get started...)\n"
  return "You are missing Cloud Provider API Credentials, Region or Servername from your session"

def exec_thread(sid, shell, room):
    splitshell = shlex.split(shell)
    #proc = 
    #for line in io.TextIOWrapper(proc.stdout, encoding="utf-8"):
    #
    starttime = time.perf_counter()    
    with subprocess.Popen(splitshell, bufsize=1, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) as proc:
      for line in iter(proc.stdout.readline, ""):
        socketio.emit('my_response', {'data': line }, namespace="/tty", room=room)
        ## Have to sleep this thread, to let it emit to the client
        socketio.sleep(0.01)
    endtime = time.perf_counter()
    print("Exec took %s seconds" % (endtime-starttime))
    print("Exec thread complete for room %s" % room)
    return

def ls_thread(sid, room):
    global sockets
    proc = subprocess.Popen(["ls", "-la", "/tmp"], stdout=subprocess.PIPE)
    for line in io.TextIOWrapper(proc.stdout, encoding="utf-8"):
        socketio.emit('my_response',
                      {'data': line }, namespace="/tty", room=room)
    print("ls thread complete")
    return

def socket_thread(sid):
    global workers
    room = hashlib.sha256(sid.encode('utf-8')).hexdigest()
    running = True
    while running:
      socketio.sleep(5)
      if (sid in workers and workers[sid]!=None):
        job = workers[sid]['shell']
        name = workers[sid]['name']
        print('job found, starting thread %s' % name)
        socketio.start_background_task(target=exec_thread, shell=job,sid=sid, room=room)
        #exec_thread(shell=job,sid=sid, room=room)
        workers[sid] = None
    print("Socket thread complete for room %s" % room)
    return

def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        socketio.sleep(10)
        count += 1
        socketio.emit('my_response',
                      {'data': 'Server generated event {time}'.format(time=datetime.now()), 'count': count},
                      namespace='/tty')
    return

@socketio.on('join', namespace='/tty')
def on_join(data):
    room = data['room']
    join_room(room)
    emit('my_response', {'data': 'Joined Room: {room}'.format(room=room) })
    print("SocketIO: Room %s was joined by %s" % (room, request.remote_addr))
    return

@socketio.on('leave', namespace='/tty')
def on_leave(data):
    room = data['room']
    leave_room(room)
    emit('my_response', {'data': 'Left Room: {room}'.format(room=room) })
    print("SocketIO: Room %s was left by %s" % (room, request.remote_addr))
    return

@socketio.on('disconnect_request', namespace='/tty')
def disconnect_request():
    emit('my_response',
         {'data': 'Disconnected!'})
    disconnect()
    return


@socketio.on('connect', namespace='/tty')
def tty_connect():
    global threads
    global sockets
    threads[session.sid] = socketio.start_background_task(target=socket_thread, sid=session.sid)
    sockets[session.sid] = Socket(session.sid, '/tty')
    emit('my_response', {'data': 'Connected {sid}'.format(sid=session.sid) })
    print('SocketIO: client connected %s' % request.remote_addr)
    return

@socketio.on('disconnect', namespace='/tty')
def tty_disconnect():
    print('SocketIO: client disconnected %s' % request.remote_addr)
    return

## Development helper functions

def build_do_cmd_string(token, region, name):
    #return "ls -al /tmp"
    return "heroku run -a algovpngen --type worker worker -e \"DO_ACCESS_TOKEN=%s;DO_REGION=%s;DO_SERVER_NAME=%s\"" % (token, region, name)